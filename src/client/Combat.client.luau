local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

-- Existing Roblox animations. No manual joint posing and no emote installation.
local RUN_ANIMATION_ID = "rbxassetid://656118852" -- Roblox Ninja Run
local PUNCH_ANIMATION_ID = "rbxassetid://522635514" -- Roblox default R15 ToolSlash

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local currentHumanoid: Humanoid? = nil
local currentAnimator: Animator? = nil
local currentRunTrack: AnimationTrack? = nil
local currentPunchTrack: AnimationTrack? = nil
local warnedPunchFailure = false

local function stopTracks()
	if currentRunTrack then
		currentRunTrack:Stop(0.12)
		currentRunTrack = nil
	end

	if currentPunchTrack then
		currentPunchTrack:Stop(0.05)
		currentPunchTrack = nil
	end
end

local function getAnimator(humanoid: Humanoid): Animator?
	local animator = humanoid:FindFirstChildOfClass("Animator")
	if not animator then
		animator = humanoid:WaitForChild("Animator", 5) :: Animator?
	end
	return animator
end

local function loadTrack(
	animator: Animator,
	name: string,
	animationId: string,
	priority: Enum.AnimationPriority,
	looped: boolean
): AnimationTrack?
	local animation = Instance.new("Animation")
	animation.Name = name
	animation.AnimationId = animationId

	local success, track = pcall(function()
		return animator:LoadAnimation(animation)
	end)
	animation:Destroy()

	if not success or not track then
		return nil
	end

	track.Priority = priority
	track.Looped = looped
	return track
end

local function startRunAnimation()
	local humanoid = currentHumanoid
	local animator = currentAnimator
	if not humanoid or humanoid.Health <= 0 or not animator then
		return
	end

	if not currentRunTrack then
		currentRunTrack = loadTrack(
			animator,
			"RunnerCatalogRun",
			RUN_ANIMATION_ID,
			Enum.AnimationPriority.Movement,
			true
		)
	end

	if currentRunTrack and not currentRunTrack.IsPlaying then
		currentRunTrack:Play(0.12, 1, 1)
	end
end

local function playPunch()
	local humanoid = currentHumanoid
	local animator = currentAnimator
	if not humanoid or humanoid.Health <= 0 or not animator then
		return
	end

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
		return
	end

	if not currentPunchTrack then
		currentPunchTrack = loadTrack(
			animator,
			"RunnerAutoHit",
			PUNCH_ANIMATION_ID,
			Enum.AnimationPriority.Action,
			false
		)
	end

	if not currentPunchTrack then
		if not warnedPunchFailure then
			warnedPunchFailure = true
			warn("[Combat] Could not load Roblox punch action animation")
		end
		return
	end

	-- Restart cleanly for each automatic attack pulse.
	if currentPunchTrack.IsPlaying then
		currentPunchTrack:Stop(0.02)
	end
	currentPunchTrack:Play(0.03, 1, 1.35)
end

local function attachCharacter(character: Model)
	stopTracks()

	currentHumanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	currentAnimator = nil
	warnedPunchFailure = false

	local humanoid = currentHumanoid
	if not humanoid or player.Character ~= character then
		return
	end

	currentAnimator = getAnimator(humanoid)
	if not currentAnimator then
		warn("[Combat] Animator not found")
		return
	end

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRunAnimation()
	end

	humanoid.Died:Connect(stopTracks)
end

attackEvent.OnClientEvent:Connect(function()
	playPunch()
end)

player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRunAnimation()
	else
		stopTracks()
	end
end)

player.CharacterAdded:Connect(attachCharacter)
if player.Character then
	task.spawn(attachCharacter, player.Character)
end
