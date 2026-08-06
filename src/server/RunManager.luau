local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage.Shared.Config)

local RunManager = {}

local trackedPlayers = {}
local heartbeatAccumulator = 0

local function setRunState(player: Player, status: string, isActive: boolean)
	player:SetAttribute("RunStatus", status)
	player:SetAttribute("RunActive", isActive)
end

local function prepareCharacter(player: Player, character: Model)
	setRunState(player, "Preparing", false)
	player:SetAttribute("RunCompleted", false)
	player:SetAttribute("RunDistance", 0)

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

	humanoid.WalkSpeed = 0
	humanoid.JumpPower = 0
	humanoid.JumpHeight = 0
	humanoid.AutoRotate = false
	humanoid:SetStateEnabled(Enum.HumanoidStateType.Jumping, false)

	character:PivotTo(CFrame.lookAt(
		Config.Runner.SpawnPosition,
		Config.Runner.SpawnPosition + Vector3.new(0, 0, 1)
	))
	root.AssemblyLinearVelocity = Vector3.zero
	root.AssemblyAngularVelocity = Vector3.zero

	local generatedWorld = Workspace:FindFirstChild("GeneratedWorld")
	local spawn = if generatedWorld then generatedWorld:FindFirstChild("RunnerSpawn") else nil
	if spawn and spawn:IsA("SpawnLocation") then
		player.RespawnLocation = spawn
	end

	pcall(function()
		root:SetNetworkOwner(player)
	end)

	trackedPlayers[player] = {
		character = character,
		humanoid = humanoid,
		root = root,
		lastDistance = -1,
	}

	humanoid.Died:Connect(function()
		if player.Character == character then
			setRunState(player, "Defeated", false)
		end
	end)

	setRunState(player, "Running", true)
end

local function finishRun(player: Player, record)
	if player:GetAttribute("RunActive") ~= true then
		return
	end

	setRunState(player, "Complete", false)
	player:SetAttribute("RunCompleted", true)
	player:SetAttribute("RunDistance", math.floor(Config.Runner.FinishZ - Config.Runner.SpawnPosition.Z))
	record.root.AssemblyLinearVelocity = Vector3.zero
	record.root.AssemblyAngularVelocity = Vector3.zero

	task.delay(Config.Runner.FinishRestartDelay, function()
		if player.Parent == Players and player.Character == record.character then
			player:LoadCharacter()
		end
	end)
end

local function updateRuns(deltaTime: number)
	heartbeatAccumulator += deltaTime
	if heartbeatAccumulator < Config.Runner.DistanceUpdateInterval then
		return
	end
	heartbeatAccumulator = 0

	for player, record in trackedPlayers do
		if player.Parent ~= Players or player.Character ~= record.character then
			trackedPlayers[player] = nil
			continue
		end

		if record.humanoid.Health <= 0 then
			continue
		end

		if record.root.Position.Y < Config.Runner.KillHeight then
			record.humanoid.Health = 0
			continue
		end

		if player:GetAttribute("RunActive") == true then
			local rawDistance = math.max(0, record.root.Position.Z - Config.Runner.SpawnPosition.Z)
			local distance = math.floor(rawDistance + 0.5)
			if distance ~= record.lastDistance then
				record.lastDistance = distance
				player:SetAttribute("RunDistance", distance)
			end

			if record.root.Position.Z >= Config.Runner.FinishZ then
				finishRun(player, record)
			end
		end
	end
end

local function addPlayer(player: Player)
	setRunState(player, "Preparing", false)
	player:SetAttribute("RunCompleted", false)
	player:SetAttribute("RunDistance", 0)

	player.CharacterAdded:Connect(function(character)
		task.spawn(prepareCharacter, player, character)
	end)

	if player.Character then
		task.spawn(prepareCharacter, player, player.Character)
	end
end

function RunManager.start()
	Players.PlayerAdded:Connect(addPlayer)
	Players.PlayerRemoving:Connect(function(player)
		trackedPlayers[player] = nil
	end)

	for _, player in Players:GetPlayers() do
		addPlayer(player)
	end

	RunService.Heartbeat:Connect(updateRuns)
end

return RunManager
