# Anime Roblox Base Mannequin

This asset is a deliberately blank character-production blueprint. It is bald, unclothed, unbranded, and does not contain character-specific facial styling, accessories, weapons, effects, or identity-defining details.

The proportions are inspired by the supplied anime Roblox production sheets, while excluding their hair, outfit, boots, face styling, and other final-character features. The supplied specification is treated as the technical basis, with the mannequin scope narrowed to reusable body and rig fundamentals.

## Included

- Neutral stylized head with no authored identity
- Neck, upper torso, lower torso, and pelvis
- Separate upper arms, lower arms, hands, upper legs, lower legs, feet, and joint guides
- Simplified five-digit hands
- Full humanoid armature named `RIG_AnimeRoblox`
- Non-deforming hand/foot IK and pole control bones
- Stable modular rigid weighting for the first blueprint version
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

The empty `04_HAIR`, `05_CLOTHING`, `06_BOOTS`, and `07_ACCESSORIES` collections remain available so future character generators can add those layers without changing the base structure.

## Generate on Windows

1. Install Blender 4.2 or newer.
2. Pull the latest repository changes.
3. Double-click:

```text
tools\blender\run_anime_roblox_base_mannequin_windows.bat
```

The launcher searches for Blender in `PATH` and under the standard Blender Foundation installation folder.

Terminal alternative:

```powershell
blender --background --python tools/blender/create_anime_roblox_base_mannequin.py
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

Generated files are intentionally ignored by Git. The Python generator remains the source of truth.

## Roblox Studio import

1. Open Roblox Studio.
2. Open **3D Importer**.
3. Select `anime_roblox_base_mannequin.fbx`.
4. Confirm that the armature and named body meshes appear.
5. Inspect the scale and orientation before adding game-specific Humanoid configuration.
6. Keep the `.blend` file as the editable source for derived characters.

## Design purpose

Do not edit this asset into a single permanent character and then reuse that changed file as the universal source. Instead:

1. Keep this generator and its clean output as the master blueprint.
2. Duplicate the generated `.blend` for each new character.
3. Add character-specific head edits, hair, clothing, accessories, textures, and secondary rigging only in the derived file or in a new derived generator.

## Current limitations

- The modular body uses deliberately stable, mostly rigid per-part weighting rather than a final seamless deformation basemesh.
- Hands are assembled from clean procedural mesh islands; they are suitable as a readable blueprint but are not a finished close-up hand sculpt.
- The blank head has no production facial edge-loop system or facial rig yet because this version intentionally avoids defining a face identity.
- Blender execution has been statically checked as Python, but the final generated geometry still needs to be run and visually tested in Blender and imported into Roblox Studio.
- Roblox avatar publication may require additional Avatar Setup work, cages, body-part conventions, and Studio-side configuration depending on the final use case.
