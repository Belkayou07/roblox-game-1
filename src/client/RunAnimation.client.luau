local Players = game:GetService("Players")

local player = Players.LocalPlayer

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local RUN_ANIMATION_ID = "rbxassetid://656118852" -- Roblox Ninja Run

local currentHumanoid: Humanoid? = nil
local currentRunTrack: AnimationTrack? = nil

local function stopRunAnimation()
	if currentRunTrack then
		currentRunTrack:Stop(0.12)
		currentRunTrack = nil
	end
end

local function getAnimator(humanoid: Humanoid): Animator?
	local animator = humanoid:FindFirstChildOfClass("Animator")
	if not animator then
		animator = humanoid:WaitForChild("Animator", 5) :: Animator?
	end
	return animator
end

local function loadRunAnimation(humanoid: Humanoid): AnimationTrack?
	local animator = getAnimator(humanoid)
	if not animator then
		warn("[RunAnimation] Animator not found")
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
		warn("[RunAnimation] Could not load Roblox Ninja Run animation")
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

local function attachCharacter(character: Model)
	stopRunAnimation()

	currentHumanoid = character:WaitForChild("Humanoid", 10) :: Humanoid?
	local humanoid = currentHumanoid
	if not humanoid or player.Character ~= character then
		return
	end

	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		startRunAnimation()
	end

	humanoid.Died:Connect(stopRunAnimation)
end

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
