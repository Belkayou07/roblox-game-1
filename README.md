# Roblox Game 1

This repository includes script-generated Blender assets for the Roblox game.

## Current asset: Roblox avatar blueprint

The first asset is a blank Roblox-style segmented character body for designing future characters, clothing, armor, weapons, and accessories.

It includes:

- head
- upper and lower torso
- upper and lower arms
- hands
- upper and lower legs
- feet
- a simple named armature
- joint-position guides
- a height ruler
- one-Blender-unit-per-Roblox-stud scaling

The body is intentionally neutral and simple. It is a modeling blueprint, not a finished Roblox player character.

## Generate it on Windows

1. Pull the latest repository changes.
2. Make sure Blender 4.2 or newer is installed.
3. Double-click:

```text
tools\blender\run_avatar_blueprint_windows.bat
```

The generated files appear here:

```text
assets\generated\roblox_avatar_blueprint.blend
assets\generated\roblox_avatar_blueprint.fbx
```

Open the `.blend` file to continue modeling in Blender. The `.fbx` file is the export copy intended for Roblox Studio testing.

## Run from a terminal

When `blender.exe` is available in PATH:

```powershell
blender --background --python tools/blender/create_roblox_avatar_blueprint.py
```

## Roblox Studio import

In Roblox Studio:

1. Open the **Avatar** or **Home** tab.
2. Open **3D Importer**.
3. Select `assets/generated/roblox_avatar_blueprint.fbx`.
4. Inspect the scale and hierarchy before importing.

This first version is only the body blueprint. Roblox-specific attachments, cages, skinning refinements, textures, and final avatar validation will be added only when the actual character design requires them.

## Main source file

```text
tools/blender/create_roblox_avatar_blueprint.py
```

Edit its `PARTS` table to adjust body dimensions or positions, then run the launcher again. Generated files are disposable outputs and should not be edited as the main source of truth.
