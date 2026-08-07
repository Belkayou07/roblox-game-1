local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local RUN_STARTED_ATTRIBUTE = "RunStarted"
local COMBAT_TARGET_ATTRIBUTE = "CombatTarget"

local ATTACK_INTERVAL = 0.48
local ATTACK_DAMAGE = 25
local ATTACK_HITBOX_SIZE = Vector3.new(8, 7, 10)
local ATTACK_FORWARD_OFFSET = 5.5

local REMOTES_FOLDER_NAME = "GameRemotes"
local ATTACK_EVENT_NAME = "AttackPulse"

local remotesFolder = ReplicatedStorage:FindFirstChild(REMOTES_FOLDER_NAME)
if not remotesFolder then
	remotesFolder = Instance.new("Folder")
	remotesFolder.Name = REMOTES_FOLDER_NAME
	remotesFolder.Parent = ReplicatedStorage
end

local attackEvent = remotesFolder:FindFirstChild(ATTACK_EVENT_NAME)
if not attackEvent then
	attackEvent = Instance.new("RemoteEvent")
	attackEvent.Name = ATTACK_EVENT_NAME
	attackEvent.Parent = remotesFolder
end

local lastAttackAt: {[Player]: number} = {}

local function getTargetModel(part: BasePart): Model?
	local model = part:FindFirstAncestorOfClass("Model")
	if not model or model:GetAttribute(COMBAT_TARGET_ATTRIBUTE) ~= true then
		return nil
	end

	return model
end

local function hasLineOfSight(attackerCharacter: Model, target: Model, targetRoot: BasePart): boolean
	local attackerRoot = attackerCharacter:FindFirstChild("HumanoidRootPart")
	if not attackerRoot or not attackerRoot:IsA("BasePart") then
		return false
	end

	local direction = targetRoot.Position - attackerRoot.Position
	if direction.Magnitude <= 0.01 then
		return true
	end

	local raycastParams = RaycastParams.new()
	raycastParams.FilterType = Enum.RaycastFilterType.Exclude
	raycastParams.FilterDescendantsInstances = {attackerCharacter}
	raycastParams.IgnoreWater = true

	local result = Workspace:Raycast(attackerRoot.Position, direction, raycastParams)
	return result == nil or result.Instance:IsDescendantOf(target)
end

local function performAttack(player: Player): boolean
	local character = player.Character
	if not character then
		return false
	end

	local humanoid = character:FindFirstChildOfClass("Humanoid")
	local root = character:FindFirstChild("HumanoidRootPart")
	if not humanoid or humanoid.Health <= 0 or not root or not root:IsA("BasePart") then
		return false
	end

	local overlapParams = OverlapParams.new()
	overlapParams.FilterType = Enum.RaycastFilterType.Exclude
	overlapParams.FilterDescendantsInstances = {character}
	overlapParams.MaxParts = 60

	local lookVector = root.CFrame.LookVector
	local hitboxCenter = root.Position + lookVector * ATTACK_FORWARD_OFFSET
	local hitboxCFrame = CFrame.lookAt(hitboxCenter, hitboxCenter + lookVector)
	local parts = Workspace:GetPartBoundsInBox(hitboxCFrame, ATTACK_HITBOX_SIZE, overlapParams)

	local damagedTargets: {[Model]: boolean} = {}
	local connected = false

	for _, part in parts do
		local target = getTargetModel(part)
		if target and not damagedTargets[target] and target ~= character then
			damagedTargets[target] = true

			local targetHumanoid = target:FindFirstChildOfClass("Humanoid")
			local targetRoot = target:FindFirstChild("HumanoidRootPart") or target.PrimaryPart
			if targetHumanoid and targetHumanoid.Health > 0 and targetRoot and targetRoot:IsA("BasePart") then
				if hasLineOfSight(character, target, targetRoot) then
					targetHumanoid:TakeDamage(ATTACK_DAMAGE)
					connected = true
				end
			end
		end
	end

	return connected
end

RunService.Heartbeat:Connect(function()
	local now = Workspace:GetServerTimeNow()

	for _, player in Players:GetPlayers() do
		if player:GetAttribute(RUN_STARTED_ATTRIBUTE) == true then
			local previousAttack = lastAttackAt[player] or 0
			if now - previousAttack >= ATTACK_INTERVAL then
				lastAttackAt[player] = now
				local connected = performAttack(player)
				attackEvent:FireClient(player, connected)
			end
		else
			lastAttackAt[player] = nil
		end
	end
end)

Players.PlayerRemoving:Connect(function(player)
	lastAttackAt[player] = nil
end)

print("[Combat] Automatic fist attacks initialized")
