local ContextActionService = game:GetService("ContextActionService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage.Shared.Config)

local RunnerController = {}

local player = Players.LocalPlayer
local movementConnection: RBXScriptConnection? = nil
local currentLaneIndex = 2
local cameraInitialized = false

local ACTION_LEFT = "RunnerMoveLeft"
local ACTION_RIGHT = "RunnerMoveRight"
local FORWARD = Vector3.new(0, 0, 1)
local UP = Vector3.new(0, 1, 0)

local function getClosestLaneIndex(xPosition: number): number
	local closestIndex = 1
	local closestDistance = math.huge

	for laneIndex, laneX in Config.Runner.LanePositions do
		local distance = math.abs(xPosition - laneX)
		if distance < closestDistance then
			closestDistance = distance
			closestIndex = laneIndex
		end
	end

	return closestIndex
end

local function changeLane(direction: number, inputState: Enum.UserInputState)
	if inputState == Enum.UserInputState.Begin and player:GetAttribute("RunActive") == true then
		currentLaneIndex = math.clamp(
			currentLaneIndex + direction,
			1,
			#Config.Runner.LanePositions
		)
	end

	return Enum.ContextActionResult.Sink
end

local function bindControls()
	ContextActionService:UnbindAction(ACTION_LEFT)
	ContextActionService:UnbindAction(ACTION_RIGHT)

	ContextActionService:BindActionAtPriority(
		ACTION_LEFT,
		function(_, inputState)
			return changeLane(-1, inputState)
		end,
		true,
		Enum.ContextActionPriority.High.Value,
		Enum.KeyCode.Q,
		Enum.KeyCode.A,
		Enum.KeyCode.Left,
		Enum.KeyCode.ButtonL1
	)

	ContextActionService:BindActionAtPriority(
		ACTION_RIGHT,
		function(_, inputState)
			return changeLane(1, inputState)
		end,
		true,
		Enum.ContextActionPriority.High.Value,
		Enum.KeyCode.D,
		Enum.KeyCode.Right,
		Enum.KeyCode.ButtonR1
	)

	ContextActionService:SetTitle(ACTION_LEFT, "<")
	ContextActionService:SetTitle(ACTION_RIGHT, ">")
	ContextActionService:SetPosition(ACTION_LEFT, UDim2.fromScale(0.13, 0.78))
	ContextActionService:SetPosition(ACTION_RIGHT, UDim2.fromScale(0.83, 0.78))
end

local function updateCamera(root: BasePart, deltaTime: number)
	local camera = Workspace.CurrentCamera
	if not camera then
		return
	end

	camera.CameraType = Enum.CameraType.Scriptable
	local desiredPosition = root.Position + Config.Camera.Offset
	local focusPosition = root.Position + Config.Camera.FocusOffset
	local desiredCFrame = CFrame.lookAt(desiredPosition, focusPosition, UP)

	if not cameraInitialized then
		camera.CFrame = desiredCFrame
		cameraInitialized = true
		return
	end

	local alpha = 1 - math.exp(-Config.Camera.Responsiveness * deltaTime)
	camera.CFrame = camera.CFrame:Lerp(desiredCFrame, alpha)
end

local function attachCharacter(character: Model)
	if movementConnection then
		movementConnection:Disconnect()
		movementConnection = nil
	end

	cameraInitialized = false

	local humanoid = character:WaitForChild("Humanoid", 10)
	local root = character:WaitForChild("HumanoidRootPart", 10)
	if not humanoid or not humanoid:IsA("Humanoid") then
		return
	end
	if not root or not root:IsA("BasePart") then
		return
	end
	if player.Character ~= character then
		return
	end

	currentLaneIndex = getClosestLaneIndex(root.Position.X)

	movementConnection = RunService.RenderStepped:Connect(function(deltaTime)
		if not root.Parent or humanoid.Health <= 0 then
			return
		end

		local isRunning = player:GetAttribute("RunActive") == true
		if isRunning then
			local targetX = Config.Runner.LanePositions[currentLaneIndex]
			local lateralError = targetX - root.Position.X
			local lateralVelocity = math.clamp(
				lateralError * Config.Runner.LaneChangeStrength,
				-Config.Runner.MaxLaneSpeed,
				Config.Runner.MaxLaneSpeed
			)

			root.CFrame = CFrame.lookAt(root.Position, root.Position + FORWARD, UP)
			root.AssemblyLinearVelocity = Vector3.new(
				lateralVelocity,
				root.AssemblyLinearVelocity.Y,
				Config.Runner.ForwardSpeed
			)
		else
			root.AssemblyLinearVelocity = Vector3.new(0, root.AssemblyLinearVelocity.Y, 0)
		end

		updateCamera(root, deltaTime)
	end)
end

function RunnerController.start()
	bindControls()

	player.CharacterAdded:Connect(function(character)
		task.spawn(attachCharacter, character)
	end)

	if player.Character then
		task.spawn(attachCharacter, player.Character)
	end
end

return RunnerController
