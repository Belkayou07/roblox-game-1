local Config = {
	GameName = "Roblox Game 1",
	IsDevelopment = true,

	Runner = {
		LanePositions = { -8, 0, 8 },
		ForwardSpeed = 30,
		LaneChangeStrength = 11,
		MaxLaneSpeed = 50,

		TrackStartZ = 0,
		TrackLength = 720,
		TrackWidth = 30,
		TrackHeight = 1,
		TrackSegmentLength = 60,

		SpawnPosition = Vector3.new(0, 4, 12),
		FinishZ = 700,
		KillHeight = -20,
		DistanceUpdateInterval = 0.1,
		FinishRestartDelay = 4,
	},

	Camera = {
		Offset = Vector3.new(0, 9, -17),
		FocusOffset = Vector3.new(0, 3, 14),
		Responsiveness = 9,
	},
}

return table.freeze(Config)
