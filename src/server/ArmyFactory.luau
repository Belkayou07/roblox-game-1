local ArmyFactory = {}

local SQUAD_PRIMARY = Color3.fromRGB(54, 142, 235)
local SQUAD_DARK = Color3.fromRGB(28, 74, 140)
local SQUAD_HEAD = Color3.fromRGB(120, 190, 255)
local ENEMY_PRIMARY = Color3.fromRGB(220, 67, 67)
local ENEMY_DARK = Color3.fromRGB(126, 31, 31)
local ENEMY_HEAD = Color3.fromRGB(255, 124, 124)
local GUN_COLOR = Color3.fromRGB(35, 38, 43)

local function createPart(
	model: Model,
	name: string,
	size: Vector3,
	offset: Vector3,
	color: Color3
): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.CanCollide = false
	part.CanTouch = false
	part.CanQuery = false
	part.Size = size
	part.Position = offset
	part.Material = Enum.Material.SmoothPlastic
	part.Color = color
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = model
	return part
end

local function createUnitModel(
	parent: Instance,
	name: string,
	position: Vector3,
	facing: Vector3,
	primaryColor: Color3,
	darkColor: Color3,
	headColor: Color3,
	withGun: boolean
): Model
	local model = Instance.new("Model")
	model.Name = name
	model.Parent = parent

	local torso = createPart(model, "Torso", Vector3.new(1.55, 1.9, 0.9), Vector3.zero, primaryColor)
	createPart(model, "Head", Vector3.new(1.2, 1.2, 1.2), Vector3.new(0, 1.55, 0), headColor)
	createPart(model, "LeftArm", Vector3.new(0.55, 1.75, 0.55), Vector3.new(-1.05, 0, 0), darkColor)
	createPart(model, "RightArm", Vector3.new(0.55, 1.75, 0.55), Vector3.new(1.05, 0, 0), darkColor)
	createPart(model, "LeftLeg", Vector3.new(0.62, 1.8, 0.62), Vector3.new(-0.42, -1.85, 0), darkColor)
	createPart(model, "RightLeg", Vector3.new(0.62, 1.8, 0.62), Vector3.new(0.42, -1.85, 0), darkColor)

	if withGun then
		createPart(model, "Gun", Vector3.new(0.28, 0.28, 1.75), Vector3.new(0.78, 0.15, 0.95), GUN_COLOR)
	end

	model.PrimaryPart = torso
	model:PivotTo(CFrame.lookAt(position, position + facing))
	return model
end

function ArmyFactory.createSquadUnit(parent: Instance, index: number, position: Vector3): Model
	local unit = createUnitModel(
		parent,
		string.format("Squad_%02d", index),
		position,
		Vector3.new(0, 0, 1),
		SQUAD_PRIMARY,
		SQUAD_DARK,
		SQUAD_HEAD,
		true
	)
	unit:SetAttribute("SquadUnit", true)
	return unit
end

function ArmyFactory.createEnemy(parent: Instance, waveNumber: number, index: number, position: Vector3): Model
	local enemy = createUnitModel(
		parent,
		string.format("Enemy_W%02d_%02d", waveNumber, index),
		position,
		Vector3.new(0, 0, -1),
		ENEMY_PRIMARY,
		ENEMY_DARK,
		ENEMY_HEAD,
		false
	)
	enemy:SetAttribute("Enemy", true)
	enemy:SetAttribute("WaveNumber", waveNumber)
	return enemy
end

function ArmyFactory.getSquadOffset(index: number, count: number): Vector3
	local columns = math.clamp(math.ceil(math.sqrt(count * 1.4)), 1, 8)
	local row = math.floor((index - 1) / columns)
	local column = (index - 1) % columns + 1
	local remaining = count - row * columns
	local rowCount = math.min(columns, remaining)
	local spacingX = 2.65
	local spacingZ = 2.85
	local x = (column - (rowCount + 1) / 2) * spacingX
	local z = -4.5 - row * spacingZ
	return Vector3.new(x, 0, z)
end

function ArmyFactory.getEnemyOffset(index: number, count: number): Vector3
	local columns = math.clamp(math.ceil(math.sqrt(count * 1.25)), 1, 7)
	local row = math.floor((index - 1) / columns)
	local column = (index - 1) % columns + 1
	local remaining = count - row * columns
	local rowCount = math.min(columns, remaining)
	local spacingX = 3.1
	local spacingZ = 3.25
	local x = (column - (rowCount + 1) / 2) * spacingX
	local z = row * spacingZ
	return Vector3.new(x, 0, z)
end

return ArmyFactory
