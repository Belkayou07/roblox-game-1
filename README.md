# Roblox Game 1

Current development task: build the original Roblox boss character **The Shattered Veil**.

## Generate the Blender blockout

1. Open PowerShell inside this repository.
2. Pull the latest files:

```powershell
git pull
```

3. Run the one-click builder:

```powershell
.\build-character.bat
```

The launcher finds the installed Blender executable, restores the generator, runs Blender in the background, and creates:

```text
TheShatteredVeil/
├── TheShatteredVeil.blend
├── TheShatteredVeil_Roblox.fbx
├── TheShatteredVeil_Roblox.glb
├── PREVIEW_FRONT.png
├── PREVIEW_BACK.png
├── PREVIEW_THREE_QUARTER.png
├── PREVIEW_WEAPONS.png
└── BUILD_REPORT.json
```

This is the first real Blender silhouette blockout, not the final production model. Review the four previews before detailed sculpting, topology, final materials, and Roblox testing.

## Iteration workflow

After each build, send the four preview images or a screenshot of Blender. The next repository update will refine the actual model rather than replacing the project manually.
