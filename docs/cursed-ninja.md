# Cursed Ninja character asset

This is the first original character built from the repository's blocky R15 avatar direction.

## Design implemented

- Tall, lean athletic humanoid proportions
- Broad shoulders, narrow waist and long legs
- Classic Roblox-readable block forms with R15 segmentation
- Face completely covered by three blindfold layers, hair and a high scarf
- Long irregular black hair made from individually editable strands
- Damaged black and charcoal ninja robes
- Dark-red sash, cloth tails and asymmetric accents
- Layered forearm and shin wraps
- Worn boots
- Broken chest and shoulder armor fragments
- Long broken crescent sword
- Short hooked sword
- Blackened cracked-metal material direction
- Nineteen standard Roblox attachment markers
- R15 body-part naming and hierarchy
- Extra spine, chest and clavicle posing controls
- Mobility test animation at frame 36

The swords are crossed on the back so the base model remains readable and easy to edit in a neutral pose.

## Generate on Windows

Pull the repository and double-click:

```text
tools\blender\run_cursed_ninja_windows.bat
```

Generated files:

```text
assets\generated\cursed_ninja\cursed_ninja.blend
assets\generated\cursed_ninja\cursed_ninja.fbx
```

Open the `.blend` file first. Use frame `1` for the neutral model and frame `36` to inspect articulation.

## Main source

```text
tools/blender/create_cursed_ninja.py
```

Generated `.blend` and `.fbx` files are disposable outputs. The Python generator is the source of truth.

## Current stage

This is a detailed procedural blockout. It is intended to establish the silhouette, component layout and rig structure before fine sculpting.

It is not yet a final Marketplace-ready avatar. Final work may still require:

- proportion corrections after visual review
- improved joint transitions and skin weights
- refined sword geometry
- proper hair and cloth deformation bones
- optimized topology
- UV maps and authored textures
- body cages and layered-clothing validation
- Roblox Studio Avatar Setup and import testing
