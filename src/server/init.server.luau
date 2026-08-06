local Players = game:GetService("Players")
local Workspace = game:GetService("Workspace")

local PATH_WIDTH = 60
local PATH_LENGTH = 2000
local PATH_THICKNESS = 2
local START_LINE_Z = 40
local SPAWN_Z = 15
local FORWARD_SPEED = 24
local STRAFE_SPEED = 20
local RUN_STARTED_ATTRIBUTE = "RunStarted"

local function preparePlayer(player: Player)
	player:SetAttribute(RUN_STARTED_ATTRIBUTE, false)

	player.CharacterAdded:Connect(function()
		player:SetAttribute(RUN_STARTED_ATTRIBUTE, false)
	end)
end

Players.PlayerAdded:Connect(preparePlayer)
for _, player in Players:GetPlayers() do
	preparePlayer(player)
end

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
world:SetAttribute("PathWidth", PATH_WIDTH)
world:SetAttribute("ForwardSpeed", FORWARD_SPEED)
world:SetAttribute("StrafeSpeed", STRAFE_SPEED)
world.Parent = Workspace

local path = Instance.new("Part")
path.Name = "Path"
path.Anchored = true
path.Size = Vector3.new(PATH_WIDTH, PATH_THICKNESS, PATH_LENGTH)
path.Position = Vector3.new(0, 0, PATH_LENGTH / 2)
path.Material = Enum.Material.Asphalt
path.Color = Color3.fromRGB(76, 175, 80)
path.TopSurface = Enum.SurfaceType.Smooth
path.BottomSurface = Enum.SurfaceType.Smooth
path.Parent = world

local startLine = Instance.new("Part")
startLine.Name = "StartLine"
startLine.Anchored = true
startLine.CanCollide = false
startLine.CanTouch = false
startLine.Size = Vector3.new(PATH_WIDTH, 0.12, 3)
startLine.Position = Vector3.new(0, PATH_THICKNESS / 2 + 0.07, START_LINE_Z)
startLine.Material = Enum.Material.Neon
startLine.Color = Color3.fromRGB(255, 221, 64)
startLine.TopSurface = Enum.SurfaceType.Smooth
startLine.BottomSurface = Enum.SurfaceType.Smooth
startLine.Parent = world

local startTrigger = Instance.new("Part")
startTrigger.Name = "StartTrigger"
startTrigger.Anchored = true
startTrigger.CanCollide = false
startTrigger.CanQuery = false
startTrigger.Transparency = 1
startTrigger.Size = Vector3.new(PATH_WIDTH, 8, 4)
startTrigger.Position = Vector3.new(0, 5, START_LINE_Z)
startTrigger.Parent = world

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

startTrigger.Touched:Connect(function(hit: BasePart)
	local character = hit:FindFirstAncestorOfClass("Model")
	if not character then
		return
	end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	if not humanoid or humanoid.Health <= 0 then
		return
	end

	local player = Players:GetPlayerFromCharacter(character)
	if not player or player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
		return
	end

	player:SetAttribute(RUN_STARTED_ATTRIBUTE, true)
end)

print("[Server] Start line, path, and run trigger created")
