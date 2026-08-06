local Players = game:GetService("Players")

local RunnerHud = {}

local player = Players.LocalPlayer

local function createLabel(
	parent: Instance,
	name: string,
	size: UDim2,
	position: UDim2,
	text: string,
	textSize: number
): TextLabel
	local label = Instance.new("TextLabel")
	label.Name = name
	label.Size = size
	label.Position = position
	label.AnchorPoint = Vector2.new(0.5, 0.5)
	label.BackgroundColor3 = Color3.fromRGB(20, 23, 30)
	label.BackgroundTransparency = 0.18
	label.BorderSizePixel = 0
	label.Text = text
	label.TextColor3 = Color3.fromRGB(245, 247, 252)
	label.TextSize = textSize
	label.Font = Enum.Font.GothamBold
	label.Parent = parent

	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = label

	local stroke = Instance.new("UIStroke")
	stroke.Color = Color3.fromRGB(91, 104, 128)
	stroke.Transparency = 0.35
	stroke.Thickness = 1
	stroke.Parent = label

	return label
end

function RunnerHud.start()
	local playerGui = player:WaitForChild("PlayerGui")
	local oldGui = playerGui:FindFirstChild("RunnerHud")
	if oldGui then
		oldGui:Destroy()
	end

	local screenGui = Instance.new("ScreenGui")
	screenGui.Name = "RunnerHud"
	screenGui.ResetOnSpawn = false
	screenGui.IgnoreGuiInset = true
	screenGui.DisplayOrder = 10
	screenGui.Parent = playerGui

	local distanceLabel = createLabel(
		screenGui,
		"Distance",
		UDim2.fromOffset(250, 46),
		UDim2.fromScale(0.5, 0.06),
		"DISTANCE  0",
		22
	)

	local statusLabel = createLabel(
		screenGui,
		"Status",
		UDim2.fromOffset(250, 38),
		UDim2.fromScale(0.5, 0.115),
		"PREPARING",
		18
	)

	local controlsLabel = createLabel(
		screenGui,
		"Controls",
		UDim2.fromOffset(430, 42),
		UDim2.fromScale(0.5, 0.94),
		"Q / A / ←    CHANGE LANE    D / →",
		16
	)
	controlsLabel.BackgroundTransparency = 0.28

	local function updateDistance()
		local distance = player:GetAttribute("RunDistance") or 0
		distanceLabel.Text = string.format("DISTANCE  %d", distance)
	end

	local function updateStatus()
		local status = player:GetAttribute("RunStatus") or "Preparing"
		statusLabel.Text = string.upper(status)

		if status == "Running" then
			statusLabel.TextColor3 = Color3.fromRGB(118, 205, 255)
		elseif status == "Complete" then
			statusLabel.Text = "RUN COMPLETE — RESTARTING"
			statusLabel.TextColor3 = Color3.fromRGB(112, 244, 150)
		elseif status == "Defeated" then
			statusLabel.TextColor3 = Color3.fromRGB(255, 112, 112)
		else
			statusLabel.TextColor3 = Color3.fromRGB(245, 247, 252)
		end
	end

	player:GetAttributeChangedSignal("RunDistance"):Connect(updateDistance)
	player:GetAttributeChangedSignal("RunStatus"):Connect(updateStatus)

	updateDistance()
	updateStatus()
end

return RunnerHud
