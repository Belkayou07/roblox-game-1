local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

local PUNCH_OUT_TIME = 0.08
local PUNCH_RETURN_TIME = 0.12
local PUNCH_FORWARD_ANGLE = math.rad(-58)
local PUNCH_SIDE_ANGLE = math.rad(8)

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local nextPunchIsRight = true
local activePunchId = 0

local function getShoulder(character: Model, rightSide: boolean): Motor6D?
	local upperTorso = character:FindFirstChild("UpperTorso")
	if upperTorso then
		local shoulderName = rightSide and "RightShoulder" or "LeftShoulder"
		local shoulder = upperTorso:FindFirstChild(shoulderName)
		if shoulder and shoulder:IsA("Motor6D") then
			return shoulder
		end
	end

	local torso = character:FindFirstChild("Torso")
	if torso then
		local shoulderName = rightSide and "Right Shoulder" or "Left Shoulder"
		local shoulder = torso:FindFirstChild(shoulderName)
		if shoulder and shoulder:IsA("Motor6D") then
			return shoulder
		end
	end

	return nil
end

local function playPunch()
	local character = player.Character
	if not character then
		return
	end

	local rightSide = nextPunchIsRight
	nextPunchIsRight = not nextPunchIsRight

	local shoulder = getShoulder(character, rightSide)
	if not shoulder then
		return
	end

	activePunchId += 1
	local punchId = activePunchId
	local restingC0 = shoulder.C0
	local sideRotation = rightSide and -PUNCH_SIDE_ANGLE or PUNCH_SIDE_ANGLE
	local punchC0 = restingC0 * CFrame.Angles(PUNCH_FORWARD_ANGLE, 0, sideRotation)

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
