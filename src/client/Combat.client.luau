local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

-- Modern procedural R6 sprint.
local RUN_CYCLE_SPEED = 11.5
local LEG_SWING = math.rad(38)
local ARM_SWING = math.rad(28)
local BASE_FORWARD_LEAN = math.rad(-12)
local TORSO_TWIST = math.rad(4.5)
local TORSO_ROLL = math.rad(1.5)
local BODY_BOUNCE = 0.07

-- Automatic punch overlay.
local PUNCH_DURATION = 0.30
local PUNCH_OUT_FRACTION = 0.34
local PUNCH_FORWARD_ANGLE = math.rad(94)
local PUNCH_SIDE_ANGLE = math.rad(8)
local PUNCH_TORSO_TWIST = math.rad(8)
local PUNCH_EXTRA_LEAN = math.rad(-4)

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local currentCharacter: Model? = nil
local currentHumanoid: Humanoid? = nil
local currentAnimate: LocalScript? = nil
local currentAnimator: Animator? = nil

local rightShoulder: Motor6D? = nil
local leftShoulder: Motor6D? = nil
local rightHip: Motor6D? = nil
local leftHip: Motor6D? = nil
local rootJoint: Motor6D? = nil
local neck: Motor6D? = nil

local customRunning = false
local runPhase = 0
local nextPunchIsRight = true
local punchStartedAt = -math.huge
local punchRightSide = true
local warnedRig = false

local function easeOutCubic(alpha: number): number
	return 1 - (1 - alpha) ^ 3
end

local function easeInOutQuad(alpha: number): number
	if alpha < 0.5 then
		return 2 * alpha * alpha
	end

	return 1 - ((-2 * alpha + 2) ^ 2) / 2
end

local function lerpNumber(a: number, b: number, alpha: number): number
	return a + (b - a) * alpha
end

local function clearJointTransforms()
	for _, joint in {rightShoulder, leftShoulder, rightHip, leftHip, rootJoint, neck} do
		if joint and joint.Parent then
			joint.Transform = CFrame.identity
		end
	end
end

local function stopPlayingTracks()
	local animator = currentAnimator
	if not animator then
		return
	end

	for _, track in animator:GetPlayingAnimationTracks() do
		track:Stop(0.08)
	end
end

local function setClassicAnimateEnabled(enabled: boolean)
	local animate = currentAnimate
	if animate and animate.Parent then
		animate.Enabled = enabled
	end

	if not enabled then
		stopPlayingTracks()
	end
end

-- Build an animation-like Motor6D Transform from a rotation around the actual
-- joint pivot. This lets us describe movement in torso/root space instead of
-- depending on the unusual internal axis orientation of classic R6 joints.
local function poseJoint(joint: Motor6D?, rotation: CFrame, translation: Vector3?)
	if not joint or not joint.Parent or not joint.Part0 or not joint.Part1 then
		return
	end

	local c0 = joint.C0
	local pivot = c0.Position
	local neutralPart1Local = c0 * joint.C1:Inverse()
	local positionOffset = translation or Vector3.zero

	local desiredPart1Local = CFrame.new(positionOffset)
		* CFrame.new(pivot)
		* rotation
		* CFrame.new(-pivot)
		* neutralPart1Local

	joint.Transform = c0:Inverse() * desiredPart1Local * joint.C1
end

local function findMotor(parent: Instance?, name: string): Motor6D?
	if not parent then
		return nil
	end

	local instance = parent:FindFirstChild(name)
	if instance and instance:IsA("Motor6D") then
		return instance
	end

	return nil
end

local function loadR6Rig(character: Model): boolean
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid or humanoid.RigType ~= Enum.HumanoidRigType.R6 then
		if humanoid and not warnedRig then
			warn("[Animation] Expected forced R6 rig, got " .. humanoid.RigType.Name)
			warnedRig = true
		end
		return false
	end

	local torso = character:FindFirstChild("Torso")
	local humanoidRootPart = character:FindFirstChild("HumanoidRootPart")
	if not torso or not humanoidRootPart then
		return false
	end

	rightShoulder = findMotor(torso, "Right Shoulder")
	leftShoulder = findMotor(torso, "Left Shoulder")
	rightHip = findMotor(torso, "Right Hip")
	leftHip = findMotor(torso, "Left Hip")
	neck = findMotor(torso, "Neck")
	rootJoint = findMotor(humanoidRootPart, "RootJoint")

	if not rightShoulder or not leftShoulder or not rightHip or not leftHip then
		if not warnedRig then
			warn("[Animation] Forced R6 character is missing standard R6 joints")
			warnedRig = true
		end
		return false
	end

	return true
end

local function startCustomRun()
	if customRunning then
		return
	end

	local character = currentCharacter
	local humanoid = currentHumanoid
	if not character or not humanoid or humanoid.Health <= 0 then
		return
	end

	if not loadR6Rig(character) then
		return
	end

	customRunning = true
	runPhase = 0
	nextPunchIsRight = true
	punchStartedAt = -math.huge

	setClassicAnimateEnabled(false)
	clearJointTransforms()
end

local function stopCustomRun()
	if customRunning then
		customRunning = false
		clearJointTransforms()
		setClassicAnimateEnabled(true)
	end

	punchStartedAt = -math.huge
end

local function getPunchWeight(now: number): number
	local normalized = (now - punchStartedAt) / PUNCH_DURATION
	if normalized < 0 or normalized >= 1 then
		return 0
	end

	if normalized <= PUNCH_OUT_FRACTION then
		return easeOutCubic(normalized / PUNCH_OUT_FRACTION)
	end

	return 1 - easeInOutQuad((normalized - PUNCH_OUT_FRACTION) / (1 - PUNCH_OUT_FRACTION))
end

local function renderModernRun(deltaTime: number)
	if not customRunning then
		return
	end

	local humanoid = currentHumanoid
	if not humanoid or humanoid.Health <= 0 then
		stopCustomRun()
		return
	end

	runPhase += deltaTime * RUN_CYCLE_SPEED

	local stride = math.sin(runPhase)
	local doubleStep = math.sin(runPhase * 2)
	local bounce = math.abs(math.cos(runPhase))
	local punchWeight = getPunchWeight(time())

	local rightLegAngle = stride * LEG_SWING
	local leftLegAngle = -stride * LEG_SWING
	local rightArmAngle = -stride * ARM_SWING
	local leftArmAngle = stride * ARM_SWING

	local torsoLean = BASE_FORWARD_LEAN + math.rad(1.2) * doubleStep
	local torsoTwist = stride * TORSO_TWIST
	local torsoRoll = stride * TORSO_ROLL

	local rightArmSide = math.rad(-2)
	local leftArmSide = math.rad(2)

	if punchWeight > 0 then
		local punchTwist = PUNCH_TORSO_TWIST * punchWeight
		torsoLean += PUNCH_EXTRA_LEAN * punchWeight

		if punchRightSide then
			rightArmAngle = lerpNumber(rightArmAngle, PUNCH_FORWARD_ANGLE, punchWeight)
			rightArmSide = lerpNumber(rightArmSide, -PUNCH_SIDE_ANGLE, punchWeight)
			leftArmAngle = lerpNumber(leftArmAngle, math.rad(20), punchWeight * 0.35)
			torsoTwist -= punchTwist
		else
			leftArmAngle = lerpNumber(leftArmAngle, PUNCH_FORWARD_ANGLE, punchWeight)
			leftArmSide = lerpNumber(leftArmSide, PUNCH_SIDE_ANGLE, punchWeight)
			rightArmAngle = lerpNumber(rightArmAngle, math.rad(20), punchWeight * 0.35)
			torsoTwist += punchTwist
		end
	end

	-- Athletic sprint posture: forward body lean, light vertical bounce and twist.
	poseJoint(
		rootJoint,
		CFrame.Angles(torsoLean, torsoTwist, torsoRoll),
		Vector3.new(0, BODY_BOUNCE * bounce, 0)
	)

	-- Keep the head more stable than the torso for a less robotic silhouette.
	poseJoint(
		neck,
		CFrame.Angles(-torsoLean * 0.45, -torsoTwist * 0.55, -torsoRoll * 0.4)
	)

	-- Long, clean sprint strides.
	poseJoint(rightHip, CFrame.Angles(rightLegAngle, 0, math.rad(2)))
	poseJoint(leftHip, CFrame.Angles(leftLegAngle, 0, math.rad(-2)))

	-- Natural opposite arm swing, with the current fist attack layered on top.
	poseJoint(rightShoulder, CFrame.Angles(rightArmAngle, 0, rightArmSide))
	poseJoint(leftShoulder, CFrame.Angles(leftArmAngle, 0, leftArmSide))
end

local function playPunch()
	if not customRunning then
		return
	end

	punchRightSide = nextPunchIsRight
	nextPunchIsRight = not nextPunchIsRight
	punchStartedAt = time()
end

local function attachCharacter(character: Model)
	stopCustomRun()

	currentCharacter = character
	currentHumanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	currentAnimate = character:FindFirstChild("Animate") :: LocalScript?
	currentAnimator = nil

	if not currentHumanoid or player.Character ~= character then
		return
	end

	currentAnimator = currentHumanoid:FindFirstChildOfClass("Animator")
	if not currentAnimator then
		currentAnimator = currentHumanoid:WaitForChild("Animator", 5) :: Animator?
	end

	warnedRig = false
	loadR6Rig(character)

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startCustomRun()
	end
end

attackEvent.OnClientEvent:Connect(function()
	playPunch()
end)

player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startCustomRun()
	else
		stopCustomRun()
	end
end)

RunService.RenderStepped:Connect(renderModernRun)

player.CharacterAdded:Connect(attachCharacter)
if player.Character then
	task.spawn(attachCharacter, player.Character)
end
