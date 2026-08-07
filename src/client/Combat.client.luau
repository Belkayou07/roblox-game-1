local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

local PUNCH_OUT_TIME = 0.09
local PUNCH_RETURN_TIME = 0.15
local PUNCH_FORWARD_ANGLE = math.rad(-92)
local PUNCH_SIDE_ANGLE = math.rad(12)

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local nextPunchIsRight = true
local activePunchId = 0

local function findMotor(character: Model, names: {string}): Motor6D?
	for _, name in names do
		local joint = character:FindFirstChild(name, true)
		if joint and joint:IsA("Motor6D") then
			return joint
		end
	end

	return nil
end

local function getShoulder(character: Model, rightSide: boolean): Motor6D?
	if rightSide then
		return findMotor(character, {"RightShoulder", "Right Shoulder"})
	end

	return findMotor(character, {"LeftShoulder", "Left Shoulder"})
end

local function playPunch()
	local character = player.Character
	if not character then
		return
	end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid or humanoid.Health <= 0 then
		return
	end

	local rightSide = nextPunchIsRight
	nextPunchIsRight = not nextPunchIsRight

	local shoulder = getShoulder(character, rightSide)
	if not shoulder then
		warn("[Combat] Could not find shoulder joint for fist animation")
		return
	end

	activePunchId += 1
	local punchId = activePunchId
	local restingC0 = shoulder.C0
	local sideRotation = rightSide and -PUNCH_SIDE_ANGLE or PUNCH_SIDE_ANGLE
	local punchC0 = restingC0
		* CFrame.Angles(PUNCH_FORWARD_ANGLE, 0, sideRotation)
		* CFrame.new(0, 0, -0.2)

	local punchTween = TweenService:Create(
		shoulder,
		TweenInfo.new(PUNCH_OUT_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{C0 = punchC0}
	)
	punchTween:Play()

	task.delay(PUNCH_OUT_TIME, function()
		if punchId ~= activePunchId or not shoulder.Parent then
			return
		end

		local returnTween = TweenService:Create(
			shoulder,
			TweenInfo.new(PUNCH_RETURN_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
			{C0 = restingC0}
		)
		returnTween:Play()
	end)
end

attackEvent.OnClientEvent:Connect(function()
	playPunch()
end)

player.CharacterAdded:Connect(function()
	nextPunchIsRight = true
	activePunchId += 1
end)
