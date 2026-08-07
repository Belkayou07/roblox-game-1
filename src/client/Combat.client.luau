local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")

local player = Players.LocalPlayer

local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

local PUNCH_OUT_TIME = 0.09
local PUNCH_RETURN_TIME = 0.15
local PUNCH_FORWARD_ANGLE = math.rad(-92)
local PUNCH_SIDE_ANGLE = math.rad(10)

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local nextPunchIsRight = true
local punchSerial = 0
local warnedWrongRig = false

local function getR6Shoulder(character: Model, rightSide: boolean): Motor6D?
	local torso = character:FindFirstChild("Torso")
	if not torso then
		return nil
	end

	local jointName = rightSide and "Right Shoulder" or "Left Shoulder"
	local shoulder = torso:FindFirstChild(jointName)
	if shoulder and shoulder:IsA("Motor6D") then
		return shoulder
	end

	return nil
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

	if humanoid.RigType ~= Enum.HumanoidRigType.R6 then
		if not warnedWrongRig then
			warn("[Combat] This game expects an R6 character, but the player spawned as " .. humanoid.RigType.Name)
			warnedWrongRig = true
		end
		return
	end

	local rightSide = nextPunchIsRight
	nextPunchIsRight = not nextPunchIsRight

	local shoulder = getR6Shoulder(character, rightSide)
	if not shoulder then
		return
	end

	punchSerial += 1
	local thisPunch = punchSerial
	local restingC0 = shoulder.C0
	local sideAngle = rightSide and -PUNCH_SIDE_ANGLE or PUNCH_SIDE_ANGLE
	local punchC0 = restingC0 * CFrame.Angles(PUNCH_FORWARD_ANGLE, 0, sideAngle)

	local outTween = TweenService:Create(
		shoulder,
		TweenInfo.new(PUNCH_OUT_TIME, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{C0 = punchC0}
	)
	outTween:Play()

	task.delay(PUNCH_OUT_TIME, function()
		if thisPunch ~= punchSerial or not shoulder.Parent then
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
	punchSerial += 1
	warnedWrongRig = false
end)
