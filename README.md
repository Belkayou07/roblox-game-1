# Roblox Game 1 — Asset Workspace

This repository is the source workspace for Roblox-specific assets generated with Blender scripts.

## Workflow

1. Pull the latest repository changes.
2. Run the requested launcher from `tools/blender/`.
3. Blender generates local files inside `assets/generated/`.
4. Import the generated FBX or other supported output into Roblox Studio.

## Structure

```text
assets/generated/   Local generated outputs; ignored by Git
docs/               Asset notes and Roblox import instructions
tools/blender/      Blender Python scripts and Windows launchers
```

Generated `.blend`, `.fbx`, preview renders, caches, and temporary files are not committed. The scripts and documentation are the source of truth.
