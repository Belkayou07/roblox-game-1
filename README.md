# Roblox Game 1

A forward-running Roblox combat game where the player changes lanes, chooses gates, grows stronger, fights enemy waves, and tries to complete each world.

## Current stage: runner foundation

Implemented:

- Generated straight three-lane prototype track
- Automatic constant-speed forward movement
- Smooth left and right lane switching
- Scripted chase camera
- Distance tracking on the server
- Run completion and automatic prototype restart
- Basic desktop, controller, and touch controls

Not implemented yet:

- Gates and gate effects
- Enemies and combat
- Allied soldiers
- Obstacles
- Rewards, upgrades, worlds, trophies, or data saving

## Controls

```text
Left:  Q, A, Left Arrow, or controller L1
Right: D, Right Arrow, or controller R1
```

Touch buttons are created automatically on mobile.

## Run the project

```powershell
rokit install
rojo serve
```

Open Roblox Studio, connect through the Rojo plugin, and press **Play**.

The player should spawn on a three-lane track and immediately begin running forward. Change lanes before reaching the finish arch. The prototype automatically starts another run several seconds after completion.

## Project structure

```text
src/
├── client/
│   ├── init.client.luau
│   ├── RunnerController.luau
│   └── RunnerHud.luau
├── server/
│   ├── init.server.luau
│   ├── RunManager.luau
│   └── WorldBuilder.luau
└── shared/
    └── Config.luau
```

## Architecture rules

- The server creates the course and owns run state, distance, completion, and future rewards.
- The client handles responsive lane movement, camera presentation, input, and interface.
- Future combat, currency, upgrades, gate rewards, trophies, and saving must be validated by the server.
- The generated prototype world is disposable and will later be replaced by proper world content.

## Previous asset workspace

The previous Blender mannequin generators remain recoverable through Git history but are not part of the active game project.
