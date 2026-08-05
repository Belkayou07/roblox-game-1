# Roblox Game 1 — Asset Workspace

This repository is the source workspace for Roblox-specific assets generated with Blender scripts.

## Current foundation: blank anime Roblox mannequin

The first production asset is a completely neutral base mannequin intended to support many different future characters. It contains the body, rig, poses, Roblox references, LOD, previews, and FBX preparation, but deliberately contains no hair, clothing, accessories, weapons, effects, logos, or character-specific identity.

Generate it on Windows by double-clicking:

```text
tools\blender\run_anime_roblox_base_mannequin_windows.bat
```

Main generator:

```text
tools\blender\create_anime_roblox_base_mannequin.py
```

Documentation:

```text
docs\anime-roblox-base-mannequin.md
```

## Workflow

1. Pull the latest repository changes.
2. Run the requested launcher from `tools/blender/`.
3. Blender generates local files inside `assets/generated/`.
4. Inspect the `.blend` source and import the generated FBX into Roblox Studio.
5. Build each final character as a derived asset rather than modifying the universal blueprint permanently.

## Structure

```text
assets/generated/   Local generated outputs; ignored by Git
docs/               Asset notes and Roblox import instructions
tools/blender/      Blender Python scripts and Windows launchers
```

Generated `.blend`, `.fbx`, preview renders, caches, and temporary files are not committed. The scripts and documentation are the source of truth.
