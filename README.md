# Roblox Game 1

This repository contains script-generated Blender assets for the Roblox game.

## Anime Roblox basemodel

The modular anime basemodel is an original neutral male NPC foundation designed for reusable Roblox characters. It includes stylized body geometry, face parts, chunky modular hair, training clothes, boots, a humanoid armature, attachments, pose actions, LOD meshes, preview outlines, cameras, lighting, renders, and FBX preparation.

Generate it on Windows by pulling the repository and double-clicking:

```text
tools\blender\run_anime_roblox_basemodel_windows.bat
```

Or run it from a terminal when Blender is available in PATH:

```powershell
blender --background --python tools/blender/create_anime_roblox_basemodel.py
```

Generated files are written to:

```text
assets\generated\anime_roblox_basemodel\anime_roblox_basemodel.blend
assets\generated\anime_roblox_basemodel\anime_roblox_basemodel.fbx
assets\generated\anime_roblox_basemodel\anime_basemodel_front.png
assets\generated\anime_roblox_basemodel\anime_basemodel_side.png
assets\generated\anime_roblox_basemodel\anime_basemodel_back.png
assets\generated\anime_roblox_basemodel\anime_basemodel_threequarter.png
assets\generated\anime_roblox_basemodel\anime_basemodel_rig.png
```

The main source is:

```text
tools\blender\create_anime_roblox_basemodel.py
```

The script targets Blender 4.2 or newer, uses one Blender unit per Roblox stud, is safe to rerun, and prints a validation report after generation.

## Blocky R15 avatar blueprint

The earlier blueprint combines the simple silhouette of a classic R6 avatar with a modern R15-style articulated structure. Generate it by double-clicking:

```text
tools\blender\run_avatar_blueprint_windows.bat
```

Generated files:

```text
assets\generated\blocky_r15_blueprint.blend
assets\generated\blocky_r15_blueprint.fbx
```

The source file is:

```text
tools\blender\create_roblox_avatar_blueprint.py
```

## Cursed Ninja character

The first original character built on the project is a tall cursed ninja with obscured face, torn black-and-red robes, long hair, broken armor, and two asymmetric curved swords.

Generate it by double-clicking:

```text
tools\blender\run_cursed_ninja_windows.bat
```

Generated files:

```text
assets\generated\cursed_ninja\cursed_ninja.blend
assets\generated\cursed_ninja\cursed_ninja.fbx
```

Design notes are in:

```text
docs\cursed-ninja.md
```

## Roblox Studio import

1. Open Roblox Studio.
2. Open **3D Importer**.
3. Select the generated `.fbx` file.
4. Inspect the mesh names and armature hierarchy.
5. Use **Avatar Setup** when the asset needs avatar-specific validation or conversion.

## Current limitations

These generated assets are modeling and rigging foundations, not guaranteed Marketplace-ready packages. Roblox may still require official cage templates, Avatar Setup, dynamic-head data, Studio-side rig configuration, texture refinement, topology optimization, or animation retargeting depending on the final use case.
