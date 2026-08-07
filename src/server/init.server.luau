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

local LOBBY_WIDTH = 86
local LOBBY_BACK_Z = -30
local LOBBY_LENGTH = START_LINE_Z - LOBBY_BACK_Z
local LOBBY_CENTER_Z = LOBBY_BACK_Z + LOBBY_LENGTH / 2

local COLOR_LOBBY = Color3.fromRGB(45, 48, 54)
local COLOR_BORDER = Color3.fromRGB(27, 30, 35)
local COLOR_PATH = Color3.fromRGB(76, 175, 80)
local COLOR_START = Color3.fromRGB(255, 221, 64)

local function createPart(
	name: string,
	size: Vector3,
	position: Vector3,
	material: Enum.Material,
	color: Color3,
	parent: Instance
): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Anchored = true
	part.Size = size
	part.Position = position
	part.Material = material
	part.Color = color
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.Parent = parent
	return part
end

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

-- Main lobby before the run begins.
local lobby = Instance.new("Folder")
lobby.Name = "Lobby"
lobby.Parent = world

createPart(
	"LobbyFloor",
	Vector3.new(LOBBY_WIDTH, PATH_THICKNESS, LOBBY_LENGTH),
	Vector3.new(0, 0, LOBBY_CENTER_Z),
	Enum.Material.Concrete,
	COLOR_LOBBY,
	lobby
)

createPart(
	"LeftBorder",
	Vector3.new(3, 4, LOBBY_LENGTH - 8),
	Vector3.new(-(LOBBY_WIDTH / 2 - 1.5), 3, LOBBY_CENTER_Z - 4),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

createPart(
	"RightBorder",
	Vector3.new(3, 4, LOBBY_LENGTH - 8),
	Vector3.new(LOBBY_WIDTH / 2 - 1.5, 3, LOBBY_CENTER_Z - 4),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

createPart(
	"BackBorder",
	Vector3.new(LOBBY_WIDTH, 4, 3),
	Vector3.new(0, 3, LOBBY_BACK_Z + 1.5),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

-- Start gate framing the entrance to the green path.
createPart(
	"StartGateLeft",
	Vector3.new(4, 13, 4),
	Vector3.new(-(PATH_WIDTH / 2 + 3), 7.5, START_LINE_Z - 2.5),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

createPart(
	"StartGateRight",
	Vector3.new(4, 13, 4),
	Vector3.new(PATH_WIDTH / 2 + 3, 7.5, START_LINE_Z - 2.5),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

local gateBeam = createPart(
	"StartGateBeam",
	Vector3.new(PATH_WIDTH + 10, 4, 4),
	Vector3.new(0, 15, START_LINE_Z - 2.5),
	Enum.Material.Metal,
	COLOR_BORDER,
	lobby
)

local gateGui = Instance.new("SurfaceGui")
gateGui.Name = "StartSign"
gateGui.Face = Enum.NormalId.Front
gateGui.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
gateGui.PixelsPerStud = 35
gateGui.Parent = gateBeam

local gateText = Instance.new("TextLabel")
gateText.Name = "Text"
gateText.Size = UDim2.fromScale(1, 1)
gateText.BackgroundTransparency = 1
gateText.Font = Enum.Font.GothamBold
gateText.Text = "START"
gateText.TextColor3 = COLOR_START
gateText.TextScaled = true
gateText.Parent = gateGui

local startAccent = createPart(
	"StartGateAccent",
	Vector3.new(PATH_WIDTH + 2, 0.35, 0.45),
	Vector3.new(0, 12.8, START_LINE_Z - 4.55),
	Enum.Material.Neon,
	COLOR_START,
	lobby
)
startAccent.CanCollide = false

-- Green path begins only after the lobby/start line.
local runPathLength = PATH_LENGTH - START_LINE_Z
local path = createPart(
	"Path",
	Vector3.new(PATH_WIDTH, PATH_THICKNESS, runPathLength),
	Vector3.new(0, 0, START_LINE_Z + runPathLength / 2),
	Enum.Material.Asphalt,
	COLOR_PATH,
	world
)

local startLine = createPart(
	"StartLine",
	Vector3.new(PATH_WIDTH, 0.12, 3),
	Vector3.new(0, PATH_THICKNESS / 2 + 0.07, START_LINE_Z),
	Enum.Material.Neon,
	COLOR_START,
	world
)
startLine.CanCollide = false
startLine.CanTouch = false

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
spawn.Parent = lobby

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

print("[Server] Main lobby, start gate, and green run path created")
