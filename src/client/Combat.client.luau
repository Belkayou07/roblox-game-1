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

local function isArmPartName(name: string, rightSide: boolean): boolean
	if rightSide then
		return name == "RightUpperArm" or name == "Right Arm"
	end

	return name == "LeftUpperArm" or name == "Left Arm"
end

local function getShoulder(character: Model, rightSide: boolean): Motor6D?
	-- Do not depend on the joint's Name. Custom avatars can rename the Motor6D,
	-- while the connected Roblox arm body part still tells us which shoulder it is.
	for _, descendant in character:GetDescendants() do
		if descendant:IsA("Motor6D") then
			local part0 = descendant.Part0
			local part1 = descendant.Part1

			if part1 and isArmPartName(part1.Name, rightSide) then
				return descendant
			end

			if part0 and isArmPartName(part0.Name, rightSide) then
				return descendant
			end
		end
	end

	-- Final fallback for unusual rigs that still use recognizable joint names.
	local sideWord = rightSide and "right" or "left"
	for _, descendant in character:GetDescendants() do
		if descendant:IsA("Motor6D") then
			local lowerName = string.lower(descendant.Name)
			if string.find(lowerName, sideWord, 1, true)
				and (string.find(lowerName, "shoulder", 1, true) or string.find(lowerName, "arm", 1, true)) then
				return descendant
			end
		end
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

	local rightSide = nextPunchIsRight
	nextPunchIsRight = not nextPunchIsRight

	local shoulder = getShoulder(character, rightSide)
	if not shoulder then
		warn(string.format(
			"[Combat] Could not find %s arm Motor6D on %s rig",
			rightSide and "right" or "left",
			humanoid.RigType.Name
		))
		return
	end

	activePunchId += 1
	local punchId = activePunchId
	local restingC0 = shoulder.C0
	local sideRotation = rightSide and -PUNCH_SIDE_ANGLE or PUNCH_SIDE_ANGLE
	local punchC0 = restingC0
		* CFrame.Angles(PUNCH_FORWARD_ANGLE, 0, sideRotation)
		* CFrame.new(0, 0, -0.35)

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
