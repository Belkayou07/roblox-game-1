local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)
local RunnerController = require(script.RunnerController)
local RunnerHud = require(script.RunnerHud)

RunnerHud.start()
RunnerController.start()

print(string.format("[Client] %s runner foundation initialized", Config.GameName))
