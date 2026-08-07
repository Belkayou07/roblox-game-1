local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local ArmyFactory = require(script.Parent:WaitForChild("ArmyFactory"))
local world = Workspace:WaitForChild("GeneratedWorld")

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local SQUAD_COUNT_ATTRIBUTE = "SquadCount"

local FIRST_WAVE_DISTANCE = 105
local WAVE_SPACING = 145
local ENEMY_SPAWN_AHEAD = 105
local BASE_ENEMIES_PER_WAVE = 6
local EXTRA_ENEMIES_PER_WAVE = 2
local MAX_ENEMIES_PER_WAVE = 14
local ENEMY_BASE_HEALTH = 15
local ENEMY_HEALTH_PER_WAVE = 2
local ENEMY_BASE_SPEED = 10.5
local ENEMY_SPEED_PER_WAVE = 0.55
local ENEMY_CONTACT_DISTANCE = 4.2

local STARTING_SQUAD_SIZE = 6
local SQUAD_FIRE_INTERVAL = 0.32
local SQUAD_FIRE_RANGE = 88
local SQUAD_BULLET_DAMAGE = 5
local UNIT_CENTER_Y = 4.0
local TRACER_LIFETIME = 0.06

local armiesFolder = Instance.new("Folder")
armiesFolder.Name = "PlayerArmies"
armiesFolder.Parent = world

local enemiesFolder = Instance.new("Folder")
enemiesFolder.Name = "Enemies"
enemiesFolder.Parent = world

type PlayerState = {
	player: Player,
	squadFolder: Folder,
	squadModels: {Model},
	nextWaveZ: number,
	waveNumber: number,
	nextFireAt: number,
}

type EnemyState = {
	model: Model,
	target: Player,
	health: number,
	speed: number,
}

local playerStates: {[Player]: PlayerState} = {}
local activeEnemies: {EnemyState} = {}

local function getAliveCharacter(player: Player): (Model?, BasePart?, Humanoid?)
	local character = player.Character
	if not character then
		return nil, nil, nil
	end

	local root = character:FindFirstChild("HumanoidRootPart")
	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not root or not root:IsA("BasePart") or not humanoid or humanoid.Health <= 0 then
		return character, nil, humanoid
	end

	return character, root, humanoid
end

local function createTracer(startPosition: Vector3, endPosition: Vector3)
	local difference = endPosition - startPosition
	local distance = difference.Magnitude
	if distance <= 0.05 then
		return
	end

	local tracer = Instance.new("Part")
	tracer.Name = "SquadTracer"
	tracer.Anchored = true
	tracer.CanCollide = false
	tracer.CanTouch = false
	tracer.CanQuery = false
	tracer.Material = Enum.Material.Neon
	tracer.Color = Color3.fromRGB(255, 235, 90)
	tracer.Size = Vector3.new(0.12, 0.12, distance)
	tracer.CFrame = CFrame.lookAt((startPosition + endPosition) / 2, endPosition)
	tracer.Parent = world
	Debris:AddItem(tracer, TRACER_LIFETIME)
end

local function removeEnemyAt(index: number)
	local enemyState = activeEnemies[index]
	if enemyState and enemyState.model.Parent then
		enemyState.model:Destroy()
	end
	table.remove(activeEnemies, index)
end

local function removeEnemiesForPlayer(player: Player)
	for index = #activeEnemies, 1, -1 do
		if activeEnemies[index].target == player then
			removeEnemyAt(index)
		end
	end
end

local function syncSquadModels(state: PlayerState, desiredCount: number)
	desiredCount = math.max(0, math.floor(desiredCount))

	while #state.squadModels < desiredCount do
		local index = #state.squadModels + 1
		local unit = ArmyFactory.createSquadUnit(
			state.squadFolder,
			index,
			Vector3.new(0, UNIT_CENTER_Y, 0)
		)
		table.insert(state.squadModels, unit)
	end

	while #state.squadModels > desiredCount do
		local unit = table.remove(state.squadModels)
		if unit and unit.Parent then
			unit:Destroy()
		end
	end

	state.player:SetAttribute(SQUAD_COUNT_ATTRIBUTE, desiredCount)
end

local function destroyPlayerState(player: Player)
	local state = playerStates[player]
	if state then
		if state.squadFolder.Parent then
			state.squadFolder:Destroy()
		end
		playerStates[player] = nil
	end

	removeEnemiesForPlayer(player)
	player:SetAttribute(SQUAD_COUNT_ATTRIBUTE, 0)
end

local function createPlayerState(player: Player, root: BasePart): PlayerState
	local squadFolder = Instance.new("Folder")
	squadFolder.Name = string.format("Army_%d", player.UserId)
	squadFolder.Parent = armiesFolder

	local state: PlayerState = {
		player = player,
		squadFolder = squadFolder,
		squadModels = {},
		nextWaveZ = root.Position.Z + FIRST_WAVE_DISTANCE,
		waveNumber = 0,
		nextFireAt = 0,
	}

	playerStates[player] = state
	syncSquadModels(state, STARTING_SQUAD_SIZE)
	return state
end

local function getState(player: Player, root: BasePart): PlayerState
	return playerStates[player] or createPlayerState(player, root)
end

local function updateSquadFormation(state: PlayerState, root: BasePart)
	local count = #state.squadModels
	for index, unit in state.squadModels do
		if not unit.Parent or not unit.PrimaryPart then
			continue
		end

		local offset = ArmyFactory.getSquadOffset(index, count)
		local position = Vector3.new(
			root.Position.X + offset.X,
			UNIT_CENTER_Y,
			root.Position.Z + offset.Z
		)
		unit:PivotTo(CFrame.lookAt(position, position + Vector3.new(0, 0, 1)))
	end
end

local function spawnWave(state: PlayerState, root: BasePart)
	state.waveNumber += 1

	local enemyCount = math.min(
		MAX_ENEMIES_PER_WAVE,
		BASE_ENEMIES_PER_WAVE + (state.waveNumber - 1) * EXTRA_ENEMIES_PER_WAVE
	)
	local health = ENEMY_BASE_HEALTH + (state.waveNumber - 1) * ENEMY_HEALTH_PER_WAVE
	local speed = ENEMY_BASE_SPEED + (state.waveNumber - 1) * ENEMY_SPEED_PER_WAVE
	local center = Vector3.new(0, UNIT_CENTER_Y, root.Position.Z + ENEMY_SPAWN_AHEAD)

	for index = 1, enemyCount do
		local offset = ArmyFactory.getEnemyOffset(index, enemyCount)
		local position = center + offset
		local model = ArmyFactory.createEnemy(enemiesFolder, state.waveNumber, index, position)
		model:SetAttribute("Health", health)
		model:SetAttribute("TargetUserId", state.player.UserId)

		table.insert(activeEnemies, {
			model = model,
			target = state.player,
			health = health,
			speed = speed,
		})
	end

	print(string.format(
		"[ArmyCombat] Wave %d: %d enemies for %s",
		state.waveNumber,
		enemyCount,
		state.player.Name
	))
end

local function updateWaveProgress(state: PlayerState, root: BasePart)
	while root.Position.Z >= state.nextWaveZ do
		spawnWave(state, root)
		state.nextWaveZ += WAVE_SPACING
	end
end

local function getTargetsInRange(player: Player, root: BasePart): {EnemyState}
	local targets = {}

	for _, enemyState in activeEnemies do
		local enemy = enemyState.model
		if enemyState.target ~= player or not enemy.Parent or not enemy.PrimaryPart then
			continue
		end

		local difference = enemy.PrimaryPart.Position - root.Position
		if difference.Z >= -6 and difference.Magnitude <= SQUAD_FIRE_RANGE then
			table.insert(targets, enemyState)
		end
	end

	table.sort(targets, function(a, b)
		local aDistance = a.model.PrimaryPart and (a.model.PrimaryPart.Position - root.Position).Magnitude or math.huge
		local bDistance = b.model.PrimaryPart and (b.model.PrimaryPart.Position - root.Position).Magnitude or math.huge
		return aDistance < bDistance
	end)

	return targets
end

local function damageEnemy(enemyState: EnemyState, damage: number)
	if not enemyState.model.Parent then
		return
	end

	enemyState.health -= damage
	enemyState.model:SetAttribute("Health", math.max(0, enemyState.health))

	if enemyState.health <= 0 then
		for index = #activeEnemies, 1, -1 do
			if activeEnemies[index] == enemyState then
				removeEnemyAt(index)
				break
			end
		end
	end
end

local function fireSquad(state: PlayerState, root: BasePart, now: number)
	if now < state.nextFireAt or #state.squadModels == 0 then
		return
	end

	local targets = getTargetsInRange(state.player, root)
	if #targets == 0 then
		return
	end

	state.nextFireAt = now + SQUAD_FIRE_INTERVAL

	for index, unit in state.squadModels do
		if not unit.Parent or not unit.PrimaryPart then
			continue
		end

		local target = targets[((index - 1) % #targets) + 1]
		if not target.model.Parent or not target.model.PrimaryPart then
			continue
		end

		local startPosition = unit.PrimaryPart.Position + Vector3.new(0.75, 0.2, 1.5)
		local endPosition = target.model.PrimaryPart.Position
		createTracer(startPosition, endPosition)
		damageEnemy(target, SQUAD_BULLET_DAMAGE)
	end
end

local function consumeSquadMember(state: PlayerState, humanoid: Humanoid)
	local remaining = math.max(0, #state.squadModels - 1)
	syncSquadModels(state, remaining)

	if remaining <= 0 then
		humanoid.Health = 0
	end
end

local function updateEnemies(deltaTime: number)
	for index = #activeEnemies, 1, -1 do
		local enemyState = activeEnemies[index]
		local enemy = enemyState.model
		local player = enemyState.target
		local state = playerStates[player]
		local _, root, humanoid = getAliveCharacter(player)

		if not state
			or player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true
			or not root
			or not humanoid
			or not enemy.Parent
			or not enemy.PrimaryPart then
			removeEnemyAt(index)
			continue
		end

		local enemyPosition = enemy.PrimaryPart.Position
		local targetPosition = Vector3.new(root.Position.X, UNIT_CENTER_Y, root.Position.Z - 2)
		local difference = targetPosition - enemyPosition
		local distance = difference.Magnitude

		if distance <= ENEMY_CONTACT_DISTANCE then
			consumeSquadMember(state, humanoid)
			removeEnemyAt(index)
			continue
		end

		local step = math.min(enemyState.speed * deltaTime, distance)
		local nextPosition = enemyPosition + difference.Unit * step
		enemy:PivotTo(CFrame.lookAt(nextPosition, targetPosition))
	end
end

local function updatePlayer(player: Player, now: number)
	if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
		if playerStates[player] then
			destroyPlayerState(player)
		end
		return
	end

	local _, root, humanoid = getAliveCharacter(player)
	if not root or not humanoid then
		return
	end

	local state = getState(player, root)
	updateSquadFormation(state, root)
	updateWaveProgress(state, root)
	fireSquad(state, root, now)
end

local function connectPlayer(player: Player)
	player:SetAttribute(SQUAD_COUNT_ATTRIBUTE, 0)
	player:GetAttributeChangedSignal(RUN_STARTED_ATTRIBUTE):Connect(function()
		if player:GetAttribute(RUN_STARTED_ATTRIBUTE) ~= true then
			destroyPlayerState(player)
		end
	end)
end

for _, player in Players:GetPlayers() do
	connectPlayer(player)
end

Players.PlayerAdded:Connect(connectPlayer)
Players.PlayerRemoving:Connect(destroyPlayerState)

RunService.Heartbeat:Connect(function(deltaTime)
	local now = Workspace:GetServerTimeNow()

	for _, player in Players:GetPlayers() do
		updatePlayer(player, now)
	end

	updateEnemies(deltaTime)
end)

print("[ArmyCombat] Squad runner combat initialized")
