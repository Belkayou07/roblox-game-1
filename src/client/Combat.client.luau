local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer

local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

local PUNCH_DURATION = 0.24
local PUNCH_OUT_FRACTION = 0.36
local PUNCH_FORWARD_ANGLE = math.rad(-96)
local PUNCH_SIDE_ANGLE = math.rad(10)
local MIN_LATERAL_DISTANCE = 0.55

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local nextPunchIsRight = true
local activePunch: {
	motor: Motor6D,
	startedAt: number,
	rightSide: boolean,
}? = nil

local cachedCharacter: Model? = nil
local cachedRightShoulder: Motor6D? = nil
local cachedLeftShoulder: Motor6D? = nil
local printedRigFailure = false

local function easeOutQuad(alpha: number): number
	return 1 - (1 - alpha) * (1 - alpha)
end

local function easeInOutQuad(alpha: number): number
	if alpha < 0.5 then
		return 2 * alpha * alpha
	end

	return 1 - ((-2 * alpha + 2) ^ 2) / 2
end

local function describeRig(character: Model): string
	local entries = {}

	for _, descendant in character:GetDescendants() do
		if descendant:IsA("Motor6D") then
			local part0Name = descendant.Part0 and descendant.Part0.Name or "nil"
			local part1Name = descendant.Part1 and descendant.Part1.Name or "nil"
			table.insert(entries, string.format("%s:%s->%s", descendant.Name, part0Name, part1Name))
		end
	end

	if #entries == 0 then
		return "no Motor6D joints found"
	end

	return table.concat(entries, " | ")
end

local function discoverShoulders(character: Model): (Motor6D?, Motor6D?)
	local root = character:FindFirstChild("HumanoidRootPart")
	if not root or not root:IsA("BasePart") then
		return nil, nil
	end

	local bestRight: Motor6D? = nil
	local bestLeft: Motor6D? = nil
	local bestRightScore = -math.huge
	local bestLeftScore = -math.huge

	for _, descendant in character:GetDescendants() do
		if descendant:IsA("Motor6D") then
			local part0 = descendant.Part0
			local part1 = descendant.Part1
			if not part0 or not part1 then
				continue
			end

			local local0 = root.CFrame:PointToObjectSpace(part0.Position)
			local local1 = root.CFrame:PointToObjectSpace(part1.Position)

			local outerPosition = local0
			local innerPosition = local1
			if math.abs(local1.X) > math.abs(local0.X) then
				outerPosition = local1
				innerPosition = local0
			end

			local outerX = math.abs(outerPosition.X)
			local innerX = math.abs(innerPosition.X)
			local lateralStep = outerX - innerX

			-- A shoulder is normally a high joint that moves from the torso's
			-- center outward toward one side. This rejects elbows and hips without
			-- depending on Roblox's body-part or Motor6D names.
			if outerX >= MIN_LATERAL_DISTANCE and lateralStep > 0.2 then
				local score = outerPosition.Y * 5 + lateralStep * 4 + outerX

				if outerPosition.X > 0 and score > bestRightScore then
					bestRightScore = score
					bestRight = descendant
				elseif outerPosition.X < 0 and score > bestLeftScore then
					bestLeftScore = score
					bestLeft = descendant
				end
			end
		end
	end

	return bestRight, bestLeft
end

local function getShoulder(character: Model, rightSide: boolean): Motor6D?
	if cachedCharacter ~= character then
		cachedCharacter = character
		cachedRightShoulder = nil
		cachedLeftShoulder = nil
		printedRigFailure = false
	end

	if not cachedRightShoulder or not cachedLeftShoulder then
		cachedRightShoulder, cachedLeftShoulder = discoverShoulders(character)
	end

	return rightSide and cachedRightShoulder or cachedLeftShoulder
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
		if not printedRigFailure then
			printedRigFailure = true
			warn(string.format(
				"[Combat] Shoulder discovery failed on %s rig. %s",
				humanoid.RigType.Name,
				describeRig(character)
			))
		end
		return
	end

	activePunch = {
		motor = shoulder,
		startedAt = time(),
		rightSide = rightSide,
	}
end

-- Animator writes Motor6D.Transform during the animation step. PreSimulation runs
-- afterward, so this adds the punch on top of the normal running animation instead
-- of being immediately replaced by it.
RunService.PreSimulation:Connect(function()
	local punch = activePunch
	if not punch then
		return
	end

	local motor = punch.motor
	if not motor.Parent then
		activePunch = nil
		return
	end

	local elapsed = time() - punch.startedAt
	local normalized = elapsed / PUNCH_DURATION
	if normalized >= 1 then
		activePunch = nil
		return
	end

	local weight: number
	if normalized <= PUNCH_OUT_FRACTION then
		weight = easeOutQuad(normalized / PUNCH_OUT_FRACTION)
	else
		weight = 1 - easeInOutQuad((normalized - PUNCH_OUT_FRACTION) / (1 - PUNCH_OUT_FRACTION))
	end

	local sideAngle = punch.rightSide and -PUNCH_SIDE_ANGLE or PUNCH_SIDE_ANGLE
	local punchOffset = CFrame.Angles(PUNCH_FORWARD_ANGLE * weight, 0, sideAngle * weight)
	motor.Transform = motor.Transform * punchOffset
end)

attackEvent.OnClientEvent:Connect(function()
	playPunch()
end)

player.CharacterAdded:Connect(function(character)
	nextPunchIsRight = true
	activePunch = nil
	cachedCharacter = character
	cachedRightShoulder = nil
	cachedLeftShoulder = nil
	printedRigFailure = false
end)
