# Phase 3 — Connected Character Pass

This pass replaces the failed detached silhouette build.

## Main corrections

- limbs are generated between shared joint coordinates
- hands and sword handles use the same attachment points
- sword blades are solid ribbon meshes rather than loose curves
- robe and waist cloth use shaped torn panels
- hair uses tapered locks
- cameras automatically aim at the character
- lighting uses dark neutral materials and controlled exposure

## Generate

```powershell
git pull
.\build-character.bat
```

## Outputs

Generated in `TheShatteredVeil/Progress/`:

- `Connected_Front.png`
- `Connected_Side.png`
- `Connected_Back.png`
- `Connected_ThreeQuarter.png`
- `Connected_Weapons.png`
- `Connected_Pass.blend`
- `Connected_Pass.glb`
- `Connected_Report.json`

## Still unfinished

This remains a modeling blockout. The next passes will cover hand grip refinement, better facial wrapping, clothing detail, sword damage, rigging, and Roblox import testing.
