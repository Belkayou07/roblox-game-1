local Workspace = game:GetService("Workspace")

local PATH_WIDTH = 60
local PATH_LENGTH = 2000
local PATH_THICKNESS = 2
local START_LINE_Z = 40
local SPAWN_Z = 15

local oldWorld = Workspace:FindFirstChild("GeneratedWorld")
if oldWorld then
	oldWorld:Destroy()
end

local baseplate = Workspace:FindFirstChild("Baseplate")
if baseplate then
	baseplate:Destroy()
end

for _, child in Workspace:GetChildren() do
	if child:IsA("SpawnLocation") then
		child:Destroy()
	end
end

local world = Instance.new("Folder")
world.Name = "GeneratedWorld"
world.Parent = Workspace

local path = Instance.new("Part")
path.Name = "Path"
path.Anchored = true
path.Size = Vector3.new(PATH_WIDTH, PATH_THICKNESS, PATH_LENGTH)
path.Position = Vector3.new(0, 0, PATH_LENGTH / 2)
path.Material = Enum.Material.Asphalt
path.Color = Color3.fromRGB(54, 57, 63)
path.TopSurface = Enum.SurfaceType.Smooth
path.BottomSurface = Enum.SurfaceType.Smooth
path.Parent = world

local startLine = Instance.new("Part")
startLine.Name = "StartLine"
startLine.Anchored = true
startLine.CanCollide = false
startLine.Size = Vector3.new(PATH_WIDTH, 0.12, 3)
startLine.Position = Vector3.new(0, PATH_THICKNESS / 2 + 0.07, START_LINE_Z)
startLine.Material = Enum.Material.Neon
startLine.Color = Color3.fromRGB(255, 221, 64)
startLine.TopSurface = Enum.SurfaceType.Smooth
startLine.BottomSurface = Enum.SurfaceType.Smooth
startLine.Parent = world

local spawn = Instance.new("SpawnLocation")
spawn.Name = "StartSpawn"
spawn.Anchored = true
spawn.CanCollide = false
spawn.Transparency = 1
spawn.Size = Vector3.new(8, 1, 8)
spawn.CFrame = CFrame.lookAt(
	Vector3.new(0, PATH_THICKNESS / 2 + 1.5, SPAWN_Z),
	Vector3.new(0, PATH_THICKNESS / 2 + 1.5, SPAWN_Z + 1)
)
spawn.Neutral = true
spawn.Duration = 0
spawn.AllowTeamChangeOnTouch = false
spawn.Parent = world

print("[Server] Start line and path created")
