# Roblox Game 1

Current development task: rebuild the original Roblox boss character **The Shattered Veil** from scratch.

The abandoned primitive mannequin is not used as a base. Development now follows gated modeling phases so anatomy and silhouette are approved before hair, clothing, weapons, materials, rigging or VFX are added.

## Active phase

**Phase 1 — Body proportions and anatomy**

Run from PowerShell inside this repository:

```powershell
git pull
.\build-character.bat
```

The current build creates only these review outputs:

```text
TheShatteredVeil/Progress/
├── Phase1_Body_Front.png
├── Phase1_Body_Side.png
├── Phase1_Body.blend
├── Phase1_Body.glb
└── Phase1_Report.json
```

Send the front and side PNG files for review. Phase 2 will not begin until the body proportions are accepted or corrected.

See `TheShatteredVeil/README_PHASE1.md` for the precise scope and approval gate.
