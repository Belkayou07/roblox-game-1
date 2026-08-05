# Anime Roblox Base Mannequin

This asset is a deliberately blank character-production blueprint. It is bald, unclothed, unbranded, and contains no character-specific face, accessories, weapons, effects, or identity-defining details.

The proportions are inspired by the supplied anime Roblox production sheets while excluding their hair, clothing, boots, and final-character styling. The mannequin exists only as a reusable body, rig, scale, and modular-production foundation.

## Included

- Neutral stylized head with no authored identity
- One continuous torso-and-pelvis core mesh
- Separate neck, upper arms, lower arms, neutral hands, upper legs, lower legs, and bare feet
- Clean elbow and knee articulation gaps
- Smooth multi-bone weighting across the body core
- Stable rigid weighting for modular limbs
- Full humanoid armature named `RIG_AnimeRoblox`
- Non-deforming hand/foot IK and pole control bones
- `POSE_T_Pose` and `POSE_A_Pose` actions
- Roblox attachment-reference empties
- Non-rendered `HumanoidRootPart` reference proxy
- LOD1 body copy
- Neutral preview cameras, lighting, renders, `.blend`, and `.fbx` outputs

## Explicitly excluded

- Hair
- Eyebrows, eyelashes, irises, or authored expressions
- Clothing
- Boots or armor
- Accessories
- Weapons
- Aura or combat effects
- Logos and symbols
- Character-specific body modifications

The empty `04_HAIR`, `05_CLOTHING`, `06_BOOTS`, and `07_ACCESSORIES` collections remain available for future derived-character generators.

## Current generator

The Windows launcher runs:

```text
tools\blender\create_anime_roblox_base_mannequin_v6.py
```

Version 6 keeps the successful V5 structure and applies a focused silhouette polish:

- shoulder slope is shaped directly into the continuous body core
- the chest is less triangular and the pelvis is slightly narrower
- upper arms begin deeper inside the torso to reduce the disconnected shoulder look
- elbow and knee gaps are smaller and more deliberate
- arms use shaped oval sections instead of simple straight cones
- thighs and calves have subtle volume changes for a cleaner neutral leg silhouette
- hands are slimmer single-piece forms with restrained thumb definition
- feet include an ankle rise and a softer forefoot taper
- lower legs now finish close to the feet instead of appearing suspended above them
- side and three-quarter framing is tightened for easier silhouette review

The V1–V5 files remain in the repository as shared implementation and earlier working stages.

## Generate on Windows

1. Install Blender 4.2 or newer.
2. Pull the latest repository changes.
3. Double-click:

```text
tools\blender\run_anime_roblox_base_mannequin_windows.bat
```

Terminal alternative:

```powershell
blender --background --python tools/blender/create_anime_roblox_base_mannequin_v6.py
```

## Generated output

```text
assets\generated\anime_roblox_base_mannequin\
├── anime_roblox_base_mannequin.blend
├── anime_roblox_base_mannequin.fbx
├── base_mannequin_front.png
├── base_mannequin_side.png
├── base_mannequin_back.png
├── base_mannequin_threequarter.png
└── base_mannequin_rig.png
```

Running the launcher replaces the previous generated files. Generated outputs are ignored by Git; the Python generator remains the source of truth.

## Roblox Studio import

1. Open Roblox Studio.
2. Open **3D Importer**.
3. Select `anime_roblox_base_mannequin.fbx`.
4. Confirm that the armature and named body meshes appear.
5. Inspect scale and orientation before adding game-specific Humanoid configuration.
6. Keep the `.blend` file as the editable source for derived characters.

## Design purpose

1. Keep this clean generator and output as the master blueprint.
2. Duplicate the generated `.blend` for each new character.
3. Add character-specific head edits, hair, clothing, accessories, textures, and secondary rigging only in a derived file or generator.

## Current limitations

- The torso core is continuous, but limbs remain separate modular meshes for predictable Roblox-oriented production.
- Hands and feet are intentionally simplified blueprint forms, not close-up anatomy sculpts.
- The blank head intentionally has no facial edge-loop system or facial rig.
- Version 6 passes Python syntax validation but still requires local Blender rendering and Roblox Studio FBX import testing.
- Roblox avatar publication may require Avatar Setup work, cages, body-part conventions, and Studio-side configuration depending on final use.
