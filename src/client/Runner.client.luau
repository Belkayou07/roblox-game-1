local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local player = Players.LocalPlayer
local world = Workspace:WaitForChild("GeneratedWorld")

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local PATH_WIDTH = world:GetAttribute("PathWidth") or 60
local FORWARD_SPEED = world:GetAttribute("ForwardSpeed") or 24
local STRAFE_SPEED = world:GetAttribute("StrafeSpeed") or 20
local EDGE_MARGIN = 3

local ACTION_LEFT = "RunnerLeftV2"
local ACTION_RIGHT = "RunnerRightV2"
local ACTION_BLOCK = "RunnerBlockV2"
local CAMERA_BIND_NAME = "RunnerCameraV2"
local ACTION_PRIORITY = Enum.ContextActionPriority.High.Value + 20

local CAMERA_FIELD_OF_VIEW = 55
local CAMERA_OFFSET = Vector3.new(0, 12, 30)
local CAMERA_FOCUS_OFFSET = Vector3.new(0, 3, 0)
local FORWARD = Vector3.new(0, 0, 1)
local UP = Vector3.new(0, 1, 0)

local currentCharacter: Model? = nil
local currentHumanoid: Humanoid? = nil
local currentRoot: BasePart? = nil
local movementConnection: RBXScriptConnection? = nil
local deathConnection: RBXScriptConnection? = nil
local defaultControls = nil
local running = false
local leftHeld = false
local rightHeld = false

local function showLoadedBanner()
	local playerGui = player:WaitForChild("PlayerGui")
	local oldGui = playerGui:FindFirstChild("RunnerClientV2Gui")
	if oldGui then
		oldGui:Destroy()
	end

	local gui = Instance.new("ScreenGui")
	gui.Name = "RunnerClientV2Gui"
	gui.IgnoreGuiInset = true
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 1000
	gui.Parent = playerGui

	local label = Instance.new("TextLabel")
	label.AnchorPoint = Vector2.new(0.5, 0)
	label.Position = UDim2.fromScale(0.5, 0.03)
	label.Size = UDim2.fromScale(0.62, 0.08)
	label.BackgroundColor3 = Color3.fromRGB(190, 35, 220)
	label.BorderSizePixel = 0
	label.Font = Enum.Font.GothamBold
	label.Text = "RUNNER CLIENT V2 LOADED"
	label.TextColor3 = Color3.new(1, 1, 1)
	label.TextScaled = true
	label.Parent = gui

	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = label

	task.delay(8, function()
		if gui.Parent then
			gui:Destroy()
		end
	end)
end

local function handleLeft(_, inputState: Enum.UserInputState)
	leftHeld = inputState == Enum.UserInputState.Begin or inputState == Enum.UserInputState.Change
	if inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
		leftHeld = false
	end
	return Enum.ContextActionResult.Sink
end

local function handleRight(_, inputState: Enum.UserInputState)
	rightHeld = inputState == Enum.UserInputState.Begin or inputState == Enum.UserInputState.Change
	if inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
		rightHeld = false
	end
	return Enum.ContextActionResult.Sink
end

local function blockInput()
	return Enum.ContextActionResult.Sink
end

local function bindControls()
	ContextActionService:BindActionAtPriority(
		ACTION_LEFT,
		handleLeft,
		true,
		ACTION_PRIORITY,
		Enum.KeyCode.Q,
		Enum.KeyCode.A,
		Enum.KeyCode.Left,
		Enum.KeyCode.ButtonL1
	)
	ContextActionService:BindActionAtPriority(
		ACTION_RIGHT,
		handleRight,
		true,
		ACTION_PRIORITY,
		Enum.KeyCode.D,
		Enum.KeyCode.Right,
		Enum.KeyCode.ButtonR1
	)
	ContextActionService:BindActionAtPriority(
		ACTION_BLOCK,
		blockInput,
		false,
		ACTION_PRIORITY,
		Enum.KeyCode.W,
		Enum.KeyCode.Z,
		Enum.KeyCode.Up,
		Enum.KeyCode.S,
		Enum.KeyCode.Down,
		Enum.KeyCode.Space,
		Enum.KeyCode.ButtonA
	)
end

local function unbindControls()
	ContextActionService:UnbindAction(ACTION_LEFT)
	ContextActionService:UnbindAction(ACTION_RIGHT)
	ContextActionService:UnbindAction(ACTION_BLOCK)
	leftHeld = false
	rightHeld = false
end

local function stopRun()
	running = false
	RunService:UnbindFromRenderStep(CAMERA_BIND_NAME)

	if movementConnection then
		movementConnection:Disconnect()
		movementConnection = nil
	end

	unbindControls()

	if defaultControls then
		defaultControls:Enable()
	end

	if currentHumanoid then
		currentHumanoid.AutoRotate = true
		currentHumanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, true)
	end

	local camera = Workspace.CurrentCamera
	if camera then
		camera.CameraType = Enum.CameraType.Custom
	end
end

local function startRun()
	if running or not currentHumanoid or not currentRoot then
		return
	end

	running = true
	currentHumanoid.AutoRotate = false
	currentHumanoid.Jump = false
	currentHumanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, false)

	if defaultControls then
		defaultControls:Disable()
	end

	bindControls()

	local root = currentRoot
	RunService:BindToRenderStep(CAMERA_BIND_NAME, Enum.RenderPriority.Camera.Value + 100, function()
		if not running or not root.Parent then
			return
		end

		local camera = Workspace.CurrentCamera
		if camera then
			camera.CameraType = Enum.CameraType.Scriptable
			camera.FieldOfView = CAMERA_FIELD_OF_VIEW
			camera.CFrame = CFrame.lookAt(
				root.Position + CAMERA_OFFSET,
				root.Position + CAMERA_FOCUS_OFFSET,
				UP
			)
		end
	end)

	movementConnection = RunService.RenderStepped:Connect(function()
		local humanoid = currentHumanoid
		if not humanoid or humanoid.Health <= 0 or not root.Parent then
			return
		end

		local steering = (rightHeld and 1 or 0) - (leftHeld and 1 or 0)
		local maxX = PATH_WIDTH / 2 - EDGE_MARGIN
		local position = root.Position
		local clampedX = math.clamp(position.X, -maxX, maxX)
		local lateralVelocity = steering * STRAFE_SPEED

		if clampedX ~= position.X then
			position = Vector3.new(clampedX, position.Y, position.Z)
		end
		if (position.X >= maxX and lateralVelocity > 0) or (position.X <= -maxX and lateralVelocity < 0) then
			lateralVelocity = 0
		end

		root.CFrame = CFrame.lookAt(position, position + FORWARD, UP)
		root.AssemblyAngularVelocity = Vector3.zero
		root.AssemblyLinearVelocity = Vector3.new(
			lateralVelocity,
			root.AssemblyLinearVelocity.Y,
			FORWARD_SPEED
		)
	end)
end

local function attachCharacter(character: Model)
	stopRun()
	currentCharacter = character
	currentHumanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	currentRoot = character:WaitForChild("HumanoidRootPart", 10) :: BasePart?

	if not currentHumanoid or not currentRoot or player.Character ~= character then
		return
	end

	if deathConnection then
		deathConnection:Disconnect()
	end
	deathConnection = currentHumanoid.Died:Connect(stopRun)

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRun()
	end
end

showLoadedBanner()
print("[Client] RUNNER CLIENT V2 LOADED")

local playerScripts = player:WaitForChild("PlayerScripts")
task.spawn(function()
	local success, controls = pcall(function()
		local playerModule = require(playerScripts:WaitForChild("PlayerModule"))
		return playerModule:GetControls()
	end)
	if success then
		defaultControls = controls
	end
end)

player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRun()
	else
		stopRun()
	end
end)

player.CharacterAdded:Connect(attachCharacter)
if player.Character then
	task.spawn(attachCharacter, player.Character)
end
