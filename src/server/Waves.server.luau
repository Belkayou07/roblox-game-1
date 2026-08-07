local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local world = Workspace:WaitForChild("GeneratedWorld")

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local PATH_WIDTH = world:GetAttribute("PathWidth") or 60

-- Wave tuning. Roblox measures world distance in studs.
local FIRST_WAVE_DISTANCE = 120
local WAVE_SPACING = 150
local ENEMIES_PER_WAVE = 3
local ENEMY_SPAWN_AHEAD = 75
local ENEMY_SPEED = 14
local ENEMY_REACHED_DISTANCE = 3.5
local PATH_EDGE_MARGIN = 7
local ENEMY_TORSO_Y = 4.2

local ENEMY_COLOR = Color3.fromRGB(205, 55, 55)
local ENEMY_DARK_COLOR = Color3.fromRGB(115, 25, 25)
local ENEMY_HEAD_COLOR = Color3.fromRGB(225, 76, 76)

local enemiesFolder = Instance.new("Folder")
enemiesFolder.Name = "Enemies"
enemiesFolder.Parent = world

type PlayerWaveState = {
	startZ: number,
	nextWaveZ: number,
	waveNumber: number,
}

type ActiveEnemy = {
	model: Model,
	target: Player,
}

local playerStates: {[Player]: PlayerWaveState} = {}
local activeEnemies: {ActiveEnemy} = {}

local function createEnemyPart(
	model: Model,
	name: string,
	size: Vector3,
	position: Vector3,
	color: Color3
): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.CanCollide = false
	part.CanTouch = false
	part.CanQuery = true
	part.Size = size
	part.Position = position
	part.Material = Enum.Material.SmoothPlastic
	part.Color = color
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = model
	return part
end

local function createEnemy(spawnPosition: Vector3, target: Player, waveNumber: number): Model
	local enemy = Instance.new("Model")
	enemy.Name = string.format("Enemy_W%02d", waveNumber)
	enemy:SetAttribute("Enemy", true)
	enemy:SetAttribute("TargetUserId", target.UserId)
	enemy:SetAttribute("WaveNumber", waveNumber)
	enemy.Parent = enemiesFolder

	local torso = createEnemyPart(enemy, "Torso", Vector3.new(3, 3.2, 1.6), Vector3.zero, ENEMY_COLOR)
	createEnemyPart(enemy, "Head", Vector3.new(2.1, 2.1, 2.1), Vector3.new(0, 2.7, 0), ENEMY_HEAD_COLOR)
	createEnemyPart(enemy, "LeftArm", Vector3.new(1.15, 3, 1.15), Vector3.new(-2.05, 0, 0), ENEMY_DARK_COLOR)
	createEnemyPart(enemy, "RightArm", Vector3.new(1.15, 3, 1.15), Vector3.new(2.05, 0, 0), ENEMY_DARK_COLOR)
	createEnemyPart(enemy, "LeftLeg", Vector3.new(1.25, 3, 1.25), Vector3.new(-0.85, -3.05, 0), ENEMY_DARK_COLOR)
	createEnemyPart(enemy, "RightLeg", Vector3.new(1.25, 3, 1.25), Vector3.new(0.85, -3.05, 0), ENEMY_DARK_COLOR)

	enemy.PrimaryPart = torso
	enemy:PivotTo(CFrame.lookAt(
		spawnPosition,
		spawnPosition + Vector3.new(0, 0, -1)
	))

	table.insert(activeEnemies, {
		model = enemy,
		target = target,
	})

	return enemy
end

local function getWaveXPositions(count: number): {number}
	local positions = {}
	local usableWidth = PATH_WIDTH - PATH_EDGE_MARGIN * 2

	if count <= 1 then
		return {0}
	end

	for index = 1, count do
		local alpha = (index - 1) / (count - 1)
		local x = -usableWidth / 2 + usableWidth * alpha
		table.insert(positions, x)
	end

	return positions
end

local function spawnWave(player: Player, waveNumber: number, playerZ: number)
	local spawnZ = playerZ + ENEMY_SPAWN_AHEAD
	local xPositions = getWaveXPositions(ENEMIES_PER_WAVE)

	for _, x in xPositions do
		createEnemy(
			Vector3.new(x, ENEMY_TORSO_Y, spawnZ),
			player,
			waveNumber
		)
	end

	print(string.format("[Waves] Spawned wave %d for %s", waveNumber, player.Name))
end

local function removePlayerEnemies(player: Player)
	for index = #activeEnemies, 1, -1 do
		local entry = activeEnemies[index]
		if entry.target == player then
			if entry.model.Parent then
				entry.model:Destroy()
			end
			table.remove(activeEnemies, index)
		end
	end
end

local function resetPlayer(player: Player)
	playerStates[player] = nil
	removePlayerEnemies(player)
end

local function updateWaveProgress(player: Player)
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
		if playerStates[player] then
			resetPlayer(player)
		end
		return
	end

	local character = player.Character
	local root = character and character:FindFirstChild("HumanoidRootPart")
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not root or not root:IsA("BasePart") or not humanoid or humanoid.Health <= 0 then
		return
	end

	local state = playerStates[player]
	if not state then
		state = {
			startZ = root.Position.Z,
			nextWaveZ = root.Position.Z + FIRST_WAVE_DISTANCE,
			waveNumber = 0,
		}
		playerStates[player] = state
	end

	while root.Position.Z >= state.nextWaveZ do
		state.waveNumber += 1
		spawnWave(player, state.waveNumber, root.Position.Z)
		state.nextWaveZ += WAVE_SPACING
	end
end

local function updateEnemies(deltaTime: number)
	for index = #activeEnemies, 1, -1 do
		local entry = activeEnemies[index]
		local enemy = entry.model
		local target = entry.target
		local character = target.Character
		local targetRoot = character and character:FindFirstChild("HumanoidRootPart")
		local targetHumanoid = character and character:FindFirstChildOfClass("Humanoid")

		if target.Parent ~= Players
			or target:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true
			or not targetRoot
			or not targetRoot:IsA("BasePart")
			or not targetHumanoid
			or targetHumanoid.Health <= 0
			or not enemy.Parent
			or not enemy.PrimaryPart then
			if enemy.Parent then
				enemy:Destroy()
			end
			table.remove(activeEnemies, index)
			continue
		end

		local enemyPosition = enemy.PrimaryPart.Position
		local targetPosition = Vector3.new(targetRoot.Position.X, ENEMY_TORSO_Y, targetRoot.Position.Z)
		local difference = targetPosition - enemyPosition
		local distance = difference.Magnitude

		if distance <= ENEMY_REACHED_DISTANCE then
			enemy:Destroy()
			table.remove(activeEnemies, index)
			continue
		end

		local moveDistance = math.min(ENEMY_SPEED * deltaTime, distance)
		local nextPosition = enemyPosition + difference.Unit * moveDistance
		local faceTarget = Vector3.new(targetPosition.X, nextPosition.Y, targetPosition.Z)

		if (faceTarget - nextPosition).Magnitude > 0.01 then
			enemy:PivotTo(CFrame.lookAt(nextPosition, faceTarget))
		else
			enemy:PivotTo(CFrame.new(nextPosition))
		end
	end
end

for _, player in Players:GetPlayers() do
	player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
		if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
			resetPlayer(player)
		end
	end)
end

Players.PlayerAdded:Connect(function(player)
	player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
		if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
			resetPlayer(player)
		end
	end)
end)

Players.PlayerRemoving:Connect(function(player)
	resetPlayer(player)
end)

RunService.Heartbeat:Connect(function(deltaTime)
	for _, player in Players:GetPlayers() do
		updateWaveProgress(player)
	end

	updateEnemies(deltaTime)
end)

print(string.format(
	"[Waves] Enemy waves initialized: first at %d studs, then every %d studs",
	FIRST_WAVE_DISTANCE,
	WAVE_SPACING
))
