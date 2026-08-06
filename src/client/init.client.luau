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

local ACTION_LEFT = "RunnerLeft"
local ACTION_RIGHT = "RunnerRight"
local ACTION_BLOCK = "RunnerBlockOtherMovement"
local ACTION_PRIORITY = Enum.ContextActionPriority.High.Value + 10

local cameraOffset = Vector3.new(0, 14, -24)
local cameraFocusOffset = Vector3.new(0, 4, 16)
local forwardDirection = Vector3.new(0, 0, 1)
local upDirection = Vector3.new(0, 1, 0)

local activeLeftInputs = {}
local activeRightInputs = {}
local movementConnection: RBXScriptConnection? = nil
local deathConnection: RBXScriptConnection? = nil
local currentCharacter: Model? = nil
local currentHumanoid: Humanoid? = nil
local currentRoot: BasePart? = nil
local running = false
local defaultControls = nil

local function inputHeld(inputs): boolean
	return next(inputs) ~= nil
end

local function horizontalInput(): number
	local left = inputHeld(activeLeftInputs) and 1 or 0
	local right = inputHeld(activeRightInputs) and 1 or 0
	return right - left
end

local function handleDirectionalInput(inputs)
	return function(_, inputState: Enum.UserInputState, inputObject: InputObject)
		if inputState == Enum.UserInputState.Begin then
			inputs[inputObject] = true
		elseif inputState == Enum.UserInputState.End or inputState == Enum.UserInputState.Cancel then
			inputs[inputObject] = nil
		end

		return Enum.ContextActionResult.Sink
	end
end

local function blockInput()
	return Enum.ContextActionResult.Sink
end

local function bindRunControls()
	ContextActionService:BindActionAtPriority(
		ACTION_LEFT,
		handleDirectionalInput(activeLeftInputs),
		true,
		ACTION_PRIORITY,
		Enum.KeyCode.Q,
		Enum.KeyCode.A,
		Enum.KeyCode.Left,
		Enum.KeyCode.ButtonL1
	)

	ContextActionService:BindActionAtPriority(
		ACTION_RIGHT,
		handleDirectionalInput(activeRightInputs),
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

	ContextActionService:SetTitle(ACTION_LEFT, "LEFT")
	ContextActionService:SetTitle(ACTION_RIGHT, "RIGHT")
	ContextActionService:SetPosition(ACTION_LEFT, UDim2.fromScale(0.14, 0.78))
	ContextActionService:SetPosition(ACTION_RIGHT, UDim2.fromScale(0.82, 0.78))
end

local function unbindRunControls()
	ContextActionService:UnbindAction(ACTION_LEFT)
	ContextActionService:UnbindAction(ACTION_RIGHT)
	ContextActionService:UnbindAction(ACTION_BLOCK)
	table.clear(activeLeftInputs)
	table.clear(activeRightInputs)
end

local function stopRun()
	running = false

	if movementConnection then
		movementConnection:Disconnect()
		movementConnection = nil
	end

	unbindRunControls()

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
	if running or not currentCharacter or not currentHumanoid or not currentRoot then
		return
	end

	running = true
	currentHumanoid.AutoRotate = false
	currentHumanoid.Jump = false
	currentHumanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, false)

	if defaultControls then
		defaultControls:Disable()
	end

	bindRunControls()

	movementConnection = RunService.RenderStepped:Connect(function()
		local humanoid = currentHumanoid
		local root = currentRoot
		if not humanoid or not root or humanoid.Health <= 0 or not root.Parent then
			return
		end

		local maxX = PATH_WIDTH / 2 - EDGE_MARGIN
		local position = root.Position
		local clampedX = math.clamp(position.X, -maxX, maxX)
		local steering = horizontalInput()
		local lateralVelocity = steering * STRAFE_SPEED

		if clampedX ~= position.X then
			position = Vector3.new(clampedX, position.Y, position.Z)
		end

		if (position.X >= maxX and lateralVelocity > 0) or (position.X <= -maxX and lateralVelocity < 0) then
			lateralVelocity = 0
		end

		root.CFrame = CFrame.lookAt(position, position + forwardDirection, upDirection)
		root.AssemblyAngularVelocity = Vector3.zero
		root.AssemblyLinearVelocity = Vector3.new(
			lateralVelocity,
			root.AssemblyLinearVelocity.Y,
			FORWARD_SPEED
		)

		local camera = Workspace.CurrentCamera
		if camera then
			camera.CameraType = Enum.CameraType.Scriptable
			camera.CFrame = CFrame.lookAt(
				root.Position + cameraOffset,
				root.Position + cameraFocusOffset,
				upDirection
			)
		end
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

local playerScripts = player:WaitForChild("PlayerScripts")
task.spawn(function()
	local success, controls = pcall(function()
		local playerModule = require(playerScripts:WaitForChild("PlayerModule"))
		return playerModule:GetControls()
	end)

	if success then
		defaultControls = controls
		if running then
			defaultControls:Disable()
		end
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
