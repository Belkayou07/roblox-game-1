local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage.Shared.Config)

local WorldBuilder = {}

local GENERATED_WORLD_NAME = "GeneratedWorld"

local function createPart(
	name: string,
	size: Vector3,
	cframe: CFrame,
	color: Color3,
	parent: Instance,
	canCollide: boolean?
): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Size = size
	part.CFrame = cframe
	part.Color = color
	part.Material = Enum.Material.SmoothPlastic
	part.Anchored = true
	part.CanCollide = if canCollide == nil then true else canCollide
	part.CanTouch = part.CanCollide
	part.CanQuery = true
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = parent
	return part
end

local function disableOldSpawnLocations()
	for _, descendant in Workspace:GetDescendants() do
		if descendant:IsA("SpawnLocation") then
			descendant.Enabled = false
		end
	end
end

local function buildTrack(world: Folder)
	local runnerConfig = Config.Runner
	local segmentCount = math.ceil(runnerConfig.TrackLength / runnerConfig.TrackSegmentLength)

	for segmentIndex = 0, segmentCount - 1 do
		local segmentStart = runnerConfig.TrackStartZ + segmentIndex * runnerConfig.TrackSegmentLength
		local remainingLength = runnerConfig.TrackLength - segmentIndex * runnerConfig.TrackSegmentLength
		local segmentLength = math.min(runnerConfig.TrackSegmentLength, remainingLength)
		local centerZ = segmentStart + segmentLength * 0.5
		local color = if segmentIndex % 2 == 0
			then Color3.fromRGB(57, 63, 73)
			else Color3.fromRGB(64, 71, 82)

		createPart(
			string.format("Track_%02d", segmentIndex + 1),
			Vector3.new(runnerConfig.TrackWidth, runnerConfig.TrackHeight, segmentLength),
			CFrame.new(0, runnerConfig.TrackHeight * 0.5, centerZ),
			color,
			world
		)
	end
end

local function buildLaneGuides(world: Folder)
	local runnerConfig = Config.Runner
	local dividerPositions = {
		(runnerConfig.LanePositions[1] + runnerConfig.LanePositions[2]) * 0.5,
		(runnerConfig.LanePositions[2] + runnerConfig.LanePositions[3]) * 0.5,
	}
	local centerZ = runnerConfig.TrackStartZ + runnerConfig.TrackLength * 0.5

	for dividerIndex, dividerX in dividerPositions do
		local divider = createPart(
			string.format("LaneDivider_%d", dividerIndex),
			Vector3.new(0.18, 0.08, runnerConfig.TrackLength),
			CFrame.new(dividerX, runnerConfig.TrackHeight + 0.05, centerZ),
			Color3.fromRGB(220, 225, 235),
			world,
			false
		)
		divider.Material = Enum.Material.Neon
		divider.Transparency = 0.25
	end

	local railX = runnerConfig.TrackWidth * 0.5 + 0.5
	for _, side in { -1, 1 } do
		createPart(
			if side < 0 then "LeftRail" else "RightRail",
			Vector3.new(1, 4, runnerConfig.TrackLength),
			CFrame.new(railX * side, 2.5, centerZ),
			Color3.fromRGB(28, 31, 38),
			world
		)
	end
end

local function buildDistanceMarkers(world: Folder)
	local runnerConfig = Config.Runner

	for markerZ = 100, runnerConfig.FinishZ - 50, 100 do
		local marker = createPart(
			string.format("Distance_%d", markerZ),
			Vector3.new(runnerConfig.TrackWidth - 2, 0.06, 0.35),
			CFrame.new(0, runnerConfig.TrackHeight + 0.04, markerZ),
			Color3.fromRGB(100, 111, 130),
			world,
			false
		)
		marker.Material = Enum.Material.Neon
		marker.Transparency = 0.45
	end
end

local function buildStartAndFinish(world: Folder): SpawnLocation
	local runnerConfig = Config.Runner

	local startLine = createPart(
		"StartLine",
		Vector3.new(runnerConfig.TrackWidth - 2, 0.1, 1),
		CFrame.new(0, runnerConfig.TrackHeight + 0.06, runnerConfig.SpawnPosition.Z - 5),
		Color3.fromRGB(65, 160, 255),
		world,
		false
	)
	startLine.Material = Enum.Material.Neon

	local finishLine = createPart(
		"FinishLine",
		Vector3.new(runnerConfig.TrackWidth - 2, 0.1, 1.2),
		CFrame.new(0, runnerConfig.TrackHeight + 0.06, runnerConfig.FinishZ),
		Color3.fromRGB(80, 235, 130),
		world,
		false
	)
	finishLine.Material = Enum.Material.Neon

	local archWidth = runnerConfig.TrackWidth - 4
	local postX = archWidth * 0.5
	local archColor = Color3.fromRGB(80, 235, 130)

	for _, side in { -1, 1 } do
		local post = createPart(
			if side < 0 then "FinishPostLeft" else "FinishPostRight",
			Vector3.new(1.5, 10, 1.5),
			CFrame.new(postX * side, 6, runnerConfig.FinishZ),
			archColor,
			world
		)
		post.Material = Enum.Material.Neon
	end

	local top = createPart(
		"FinishArchTop",
		Vector3.new(archWidth + 1.5, 1.5, 1.5),
		CFrame.new(0, 10.25, runnerConfig.FinishZ),
		archColor,
		world
	)
	top.Material = Enum.Material.Neon

	local spawn = Instance.new("SpawnLocation")
	spawn.Name = "RunnerSpawn"
	spawn.Size = Vector3.new(8, 1, 8)
	spawn.CFrame = CFrame.lookAt(
		Vector3.new(0, runnerConfig.TrackHeight + 0.55, runnerConfig.SpawnPosition.Z),
		Vector3.new(0, runnerConfig.TrackHeight + 0.55, runnerConfig.SpawnPosition.Z + 1)
	)
	spawn.Color = Color3.fromRGB(65, 160, 255)
	spawn.Material = Enum.Material.Neon
	spawn.Transparency = 0.25
	spawn.Anchored = true
	spawn.CanCollide = true
	spawn.Neutral = true
	spawn.Duration = 0
	spawn.Enabled = true
	spawn.Parent = world

	return spawn
end

function WorldBuilder.build(): Folder
	local oldWorld = Workspace:FindFirstChild(GENERATED_WORLD_NAME)
	if oldWorld then
		oldWorld:Destroy()
	end

	disableOldSpawnLocations()

	local world = Instance.new("Folder")
	world.Name = GENERATED_WORLD_NAME
	world.Parent = Workspace

	buildTrack(world)
	buildLaneGuides(world)
	buildDistanceMarkers(world)
	buildStartAndFinish(world)

	Workspace.FallenPartsDestroyHeight = -50
	return world
end

return WorldBuilder
