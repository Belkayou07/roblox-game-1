local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

-- Existing Roblox catalog animations. No manual joint posing.
local RUN_ANIMATION_ID = "rbxassetid://656118852" -- Roblox Ninja Run
local PUNCH_EMOTE_NAME = "AutoPunch"
local PUNCH_EMOTE_ID = 92995770101297 -- Roblox Boxing Punch - KSI emote

local remotesFolder = ReplicatedStorage:WaitForChild(REMOTES_FOLDER_NAME)
local attackEvent = remotesFolder:WaitForChild(ATTACK_EVENT_NAME) :: RemoteEvent

local currentCharacter: Model? = nil
local currentHumanoid: Humanoid? = nil
local currentRunTrack: AnimationTrack? = nil
local warnedPunchFailure = false

local function stopRunAnimation()
	if currentRunTrack then
		currentRunTrack:Stop(0.12)
		currentRunTrack = nil
	end
end

local function installPunchEmote(humanoid: Humanoid)
	local success, description = pcall(function()
		return humanoid:GetAppliedDescription()
	end)

	if not success or not description then
		warn("[Combat] Could not read HumanoidDescription for boxing emote")
		return
	end

	local emotes = description:GetEmotes()
	emotes[PUNCH_EMOTE_NAME] = {PUNCH_EMOTE_ID}
	description:SetEmotes(emotes)

	local applied, applyError = pcall(function()
		humanoid:ApplyDescriptionAsync(description)
	end)

	if not applied then
		warn("[Combat] Could not install boxing emote: " .. tostring(applyError))
	end
end

local function loadRunAnimation(humanoid: Humanoid): AnimationTrack?
	local animator = humanoid:FindFirstChildOfClass("Animator")
	if not animator then
		animator = humanoid:WaitForChild("Animator", 5) :: Animator?
	end

	if not animator then
		warn("[Combat] Animator not found")
		return nil
	end

	local animation = Instance.new("Animation")
	animation.Name = "RunnerCatalogRun"
	animation.AnimationId = RUN_ANIMATION_ID

	local success, track = pcall(function()
		return animator:LoadAnimation(animation)
	end)
	animation:Destroy()

	if not success or not track then
		warn("[Combat] Could not load Roblox run animation")
		return nil
	end

	track.Priority = Enum.AnimationPriority.Movement
	track.Looped = true
	return track
end

local function startRunAnimation()
	local humanoid = currentHumanoid
	if not humanoid or humanoid.Health <= 0 then
		return
	end

	if not currentRunTrack then
		currentRunTrack = loadRunAnimation(humanoid)
	end

	if currentRunTrack and not currentRunTrack.IsPlaying then
		currentRunTrack:Play(0.12, 1, 1)
	end
end

local function playPunch()
	local humanoid = currentHumanoid
	if not humanoid or humanoid.Health <= 0 then
		return
	end

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
		return
	end

	task.spawn(function()
		local success, result = pcall(function()
			return humanoid:PlayEmoteAsync(PUNCH_EMOTE_NAME)
		end)

		if (not success or result ~= true) and not warnedPunchFailure then
			warnedPunchFailure = true
			warn("[Combat] Roblox boxing emote could not play")
		end
	end)
end

local function attachCharacter(character: Model)
	stopRunAnimation()

	currentCharacter = character
	currentHumanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	warnedPunchFailure = false

	local humanoid = currentHumanoid
	if not humanoid or player.Character ~= character then
		return
	end

	-- Configure the existing Roblox emote once for this character.
	installPunchEmote(humanoid)

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRunAnimation()
	end

	humanoid.Died:Connect(stopRunAnimation)
end

attackEvent.OnClientEvent:Connect(function()
	playPunch()
end)

player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRunAnimation()
	else
		stopRunAnimation()
	end
end)

player.CharacterAdded:Connect(attachCharacter)
if player.Character then
	task.spawn(attachCharacter, player.Character)
end
