local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)
local WorldBuilder = require(script.WorldBuilder)
local RunManager = require(script.RunManager)

WorldBuilder.build()
RunManager.start()

print(string.format("[Server] %s runner foundation initialized", Config.GameName))
