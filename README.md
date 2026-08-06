# Roblox Game 1

Current prototype:

- One wide, long path
- One yellow start line
- Normal Roblox movement before the start line
- Crossing the line locks the camera behind the player
- The player then runs forward nonstop at a constant speed
- Smooth left and right steering
- Camera follows the player's sideways movement

## Recommended update workflow

Live Rojo syncing is not required.

After the updater exists locally, double-click:

```text
UPDATE-GAME.bat
```

It will automatically:

1. Pull the latest changes from GitHub.
2. Build a fresh place at `build/RobloxGame1-Latest.rbxlx`.
3. Open that fresh place in Roblox Studio.

The Rojo Studio plugin can stay disconnected and `rojo serve` does not need to be running.

## Controls after crossing

```text
Q / A / Left Arrow = move left
D / Right Arrow     = move right
```

Mobile left/right buttons are also created automatically.
