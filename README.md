# Roblox Game 1

This repository contains script-generated Blender assets for the Roblox game.

## Current asset: Blocky R15 avatar blueprint

The current blueprint combines two ideas:

- the simple approximately five-stud silhouette of the classic R6 avatar
- the modern Roblox R15 humanoid structure required for much better articulation

It is therefore **not a six-part R6 rig**. It is a blocky, R6-looking character divided into the modern 15 Roblox body meshes.

### Included body meshes

The generator creates Roblox's required body-object names:

- `Head_Geo`
- `UpperTorso_Geo`
- `LowerTorso_Geo`
- left and right upper arms
- left and right lower arms
- left and right hands
- left and right upper legs
- left and right lower legs
- left and right feet

### Included rigging

The armature contains the standard hierarchy beginning with:

```text
Root
└── HumanoidRootNode
    └── LowerTorso
```

It also includes the standard limb bones plus optional higher-fidelity controls for:

- spine
- chest
- left and right clavicles
- head base

The separate arm, hand, leg, foot, head, and lower-torso meshes are weight-bound to their corresponding bones. The upper torso contains extra edge loops and blended weights so the spine, chest, and shoulder area can deform instead of moving as one completely rigid box.

The Blender file also contains a short movement preview:

- frame `1`: neutral pose
- frame `35`: articulated test pose
- frame `70`: neutral pose

### Attachments

The blueprint includes the 19 standard `_Att` avatar attachment markers for hats, hair, face items, collars, body accessories, waist accessories, grips, shoulders, and feet.

## Generate it on Windows

1. Pull the repository changes.
2. Make sure Blender 4.2 or newer is installed.
3. Double-click:

```text
tools\blender\run_avatar_blueprint_windows.bat
```

Generated files:

```text
assets\generated\blocky_r15_blueprint.blend
assets\generated\blocky_r15_blueprint.fbx
```

Open the `.blend` file and inspect frame `35` to verify the available movement.

## Run from a terminal

When Blender is available in PATH:

```powershell
blender --background --python tools/blender/create_roblox_avatar_blueprint.py
```

## Roblox Studio test import

1. Open Roblox Studio.
2. Open **3D Importer**.
3. Select `assets/generated/blocky_r15_blueprint.fbx`.
4. Use the default/classic rig scale when prompted.
5. Inspect all 15 `_Geo` meshes and the armature hierarchy.
6. Use **Avatar Setup** for further Roblox avatar processing and validation.

The optional spine, chest, clavicle, and head-base bones are higher-fidelity controls. Roblox Studio may require a `HumanoidRigDescription` configuration before those optional controls participate correctly in Roblox avatar animations.

## Main source file

```text
tools/blender/create_roblox_avatar_blueprint.py
```

The `PARTS`, `BONES`, and `ATTACHMENTS` tables are the main editable blueprint data. Generated `.blend` and `.fbx` files are disposable outputs and should not be treated as the source of truth.

## Current limitations

This is a strong modeling and rigging base, but it is not yet claimed to be Marketplace-ready. Final validation may still require Roblox's official cage templates, Avatar Setup, dynamic-head data, and Studio-side rig configuration depending on how the character will be used.
