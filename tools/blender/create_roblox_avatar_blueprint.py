"""Generate a reusable Roblox-style avatar blueprint in Blender.

Run through Blender:
    blender --background --python tools/blender/create_roblox_avatar_blueprint.py

The generator creates:
- assets/generated/roblox_avatar_blueprint.blend
- assets/generated/roblox_avatar_blueprint.fbx

Coordinate convention inside Blender:
- X = width
- Y = depth
- Z = height
- 1 Blender unit = 1 Roblox stud
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import bpy


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "assets" / "generated"
BLEND_PATH = OUTPUT_DIR / "roblox_avatar_blueprint.blend"
FBX_PATH = OUTPUT_DIR / "roblox_avatar_blueprint.fbx"

BODY_COLLECTION_NAME = "Avatar_Geometry"
GUIDE_COLLECTION_NAME = "Blueprint_Guides"
RIG_COLLECTION_NAME = "Avatar_Rig"

BASE_MATERIAL = "MAT_BlueprintBody"
GUIDE_MATERIAL = "MAT_BlueprintGuide"
JOINT_MATERIAL = "MAT_JointGuide"

# Dimensions are expressed in Roblox studs as (width, depth, height).
PARTS: Dict[str, Dict[str, Tuple[float, float, float]]] = {
    "LowerTorso": {"size": (1.80, 1.00, 0.80), "location": (0.00, 0.00, 3.40)},
    "UpperTorso": {"size": (2.00, 1.00, 1.20), "location": (0.00, 0.00, 4.40)},
    "Head": {"size": (2.00, 1.00, 1.20), "location": (0.00, 0.00, 5.70)},

    "LeftUpperArm": {"size": (0.80, 0.80, 1.20), "location": (-1.45, 0.00, 4.40)},
    "LeftLowerArm": {"size": (0.70, 0.70, 1.10), "location": (-1.45, 0.00, 3.25)},
    "LeftHand": {"size": (0.75, 0.85, 0.45), "location": (-1.45, -0.05, 2.475)},

    "RightUpperArm": {"size": (0.80, 0.80, 1.20), "location": (1.45, 0.00, 4.40)},
    "RightLowerArm": {"size": (0.70, 0.70, 1.10), "location": (1.45, 0.00, 3.25)},
    "RightHand": {"size": (0.75, 0.85, 0.45), "location": (1.45, -0.05, 2.475)},

    "LeftUpperLeg": {"size": (0.90, 0.90, 1.30), "location": (-0.50, 0.00, 2.35)},
    "LeftLowerLeg": {"size": (0.80, 0.80, 1.20), "location": (-0.50, 0.00, 1.10)},
    "LeftFoot": {"size": (0.90, 1.20, 0.50), "location": (-0.50, -0.15, 0.25)},

    "RightUpperLeg": {"size": (0.90, 0.90, 1.30), "location": (0.50, 0.00, 2.35)},
    "RightLowerLeg": {"size": (0.80, 0.80, 1.20), "location": (0.50, 0.00, 1.10)},
    "RightFoot": {"size": (0.90, 1.20, 0.50), "location": (0.50, -0.15, 0.25)},
}

BONES = {
    "Root": {"head": (0.0, 0.0, 3.0), "tail": (0.0, 0.0, 3.35), "parent": None},
    "LowerTorso": {"head": (0.0, 0.0, 3.0), "tail": (0.0, 0.0, 3.8), "parent": "Root"},
    "UpperTorso": {"head": (0.0, 0.0, 3.8), "tail": (0.0, 0.0, 5.0), "parent": "LowerTorso"},
    "Head": {"head": (0.0, 0.0, 5.0), "tail": (0.0, 0.0, 6.3), "parent": "UpperTorso"},

    "LeftUpperArm": {"head": (-1.0, 0.0, 4.85), "tail": (-1.45, 0.0, 3.8), "parent": "UpperTorso"},
    "LeftLowerArm": {"head": (-1.45, 0.0, 3.8), "tail": (-1.45, 0.0, 2.7), "parent": "LeftUpperArm"},
    "LeftHand": {"head": (-1.45, 0.0, 2.7), "tail": (-1.45, 0.0, 2.25), "parent": "LeftLowerArm"},

    "RightUpperArm": {"head": (1.0, 0.0, 4.85), "tail": (1.45, 0.0, 3.8), "parent": "UpperTorso"},
    "RightLowerArm": {"head": (1.45, 0.0, 3.8), "tail": (1.45, 0.0, 2.7), "parent": "RightUpperArm"},
    "RightHand": {"head": (1.45, 0.0, 2.7), "tail": (1.45, 0.0, 2.25), "parent": "RightLowerArm"},

    "LeftUpperLeg": {"head": (-0.5, 0.0, 3.0), "tail": (-0.5, 0.0, 1.7), "parent": "LowerTorso"},
    "LeftLowerLeg": {"head": (-0.5, 0.0, 1.7), "tail": (-0.5, 0.0, 0.5), "parent": "LeftUpperLeg"},
    "LeftFoot": {"head": (-0.5, 0.0, 0.5), "tail": (-0.5, -0.45, 0.2), "parent": "LeftLowerLeg"},

    "RightUpperLeg": {"head": (0.5, 0.0, 3.0), "tail": (0.5, 0.0, 1.7), "parent": "LowerTorso"},
    "RightLowerLeg": {"head": (0.5, 0.0, 1.7), "tail": (0.5, 0.0, 0.5), "parent": "RightUpperLeg"},
    "RightFoot": {"head": (0.5, 0.0, 0.5), "tail": (0.5, -0.45, 0.2), "parent": "RightLowerLeg"},
}


def clear_scene() -> None:
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.armatures,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def get_or_create_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


def make_material(
    name: str,
    color: Tuple[float, float, float, float],
    metallic: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = color
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.72
        bsdf.inputs["Metallic"].default_value = metallic
    return material


def add_rounded_box(
    name: str,
    size: Tuple[float, float, float],
    location: Tuple[float, float, float],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    bevel: float = 0.08,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    bevel_modifier = obj.modifiers.new(name="Soft Roblox Edges", type="BEVEL")
    bevel_modifier.width = min(bevel, min(size) * 0.16)
    bevel_modifier.segments = 3
    bevel_modifier.limit_method = "ANGLE"

    weighted_normal = obj.modifiers.new(name="Weighted Normals", type="WEIGHTED_NORMAL")
    weighted_normal.keep_sharp = True

    obj.data.materials.append(material)
    obj["roblox_part_name"] = name
    obj["roblox_stud_size"] = list(size)
    obj["blueprint_version"] = 1
    move_to_collection(obj, collection)
    return obj


def create_armature(collection: bpy.types.Collection) -> bpy.types.Object:
    armature_data = bpy.data.armatures.new("RobloxAvatarBlueprint_Armature")
    armature = bpy.data.objects.new("RobloxAvatarBlueprint_Rig", armature_data)
    collection.objects.link(armature)
    armature.show_in_front = True
    armature.data.display_type = "OCTAHEDRAL"

    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = {}
    for bone_name, spec in BONES.items():
        bone = armature_data.edit_bones.new(bone_name)
        bone.head = spec["head"]
        bone.tail = spec["tail"]
        bone.use_deform = bone_name != "Root"
        edit_bones[bone_name] = bone

    for bone_name, spec in BONES.items():
        parent_name = spec["parent"]
        if parent_name:
            edit_bones[bone_name].parent = edit_bones[parent_name]
            edit_bones[bone_name].use_connect = False

    bpy.ops.object.mode_set(mode="OBJECT")
    armature.select_set(False)
    return armature


def parent_part_to_bone(
    obj: bpy.types.Object,
    armature: bpy.types.Object,
    bone_name: str,
) -> None:
    world_matrix = obj.matrix_world.copy()
    obj.parent = armature
    obj.parent_type = "BONE"
    obj.parent_bone = bone_name
    obj.matrix_world = world_matrix


def create_joint_guides(
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> None:
    joint_positions = {
        "NeckPivot": (0.0, 0.0, 5.0),
        "WaistPivot": (0.0, 0.0, 3.8),
        "LeftShoulderPivot": (-1.0, 0.0, 4.85),
        "RightShoulderPivot": (1.0, 0.0, 4.85),
        "LeftElbowPivot": (-1.45, 0.0, 3.8),
        "RightElbowPivot": (1.45, 0.0, 3.8),
        "LeftHipPivot": (-0.5, 0.0, 3.0),
        "RightHipPivot": (0.5, 0.0, 3.0),
        "LeftKneePivot": (-0.5, 0.0, 1.7),
        "RightKneePivot": (0.5, 0.0, 1.7),
    }
    for name, location in joint_positions.items():
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=20,
            ring_count=12,
            radius=0.11,
            location=location,
        )
        obj = bpy.context.active_object
        obj.name = name
        obj.data.materials.append(material)
        obj.display_type = "WIRE"
        obj.hide_render = True
        move_to_collection(obj, collection)


def create_height_ruler(
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> None:
    x_position = -3.0

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_position, 0.45, 3.25))
    ruler = bpy.context.active_object
    ruler.name = "HeightRuler_6_5_Studs"
    ruler.dimensions = (0.035, 0.035, 6.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ruler.data.materials.append(material)
    ruler.hide_render = True
    move_to_collection(ruler, collection)

    for index in range(7):
        bpy.ops.mesh.primitive_cube_add(
            size=1.0,
            location=(x_position + 0.13, 0.45, float(index)),
        )
        tick = bpy.context.active_object
        tick.name = f"HeightTick_{index}"
        tick.dimensions = (0.26, 0.035, 0.025)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        tick.data.materials.append(material)
        tick.hide_render = True
        move_to_collection(tick, collection)


def create_ground_guide(
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> None:
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    ground.name = "GroundGuide"
    ground.data.materials.append(material)
    ground.display_type = "WIRE"
    ground.hide_render = True
    move_to_collection(ground, collection)


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "NONE"
    scene.unit_settings.scale_length = 1.0
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene["unit_convention"] = "1 Blender unit = 1 Roblox stud"
    scene["avatar_blueprint_height_studs"] = 6.3
    scene["avatar_blueprint_type"] = "Roblox-style segmented block rig"

    if bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.clip_start = 0.01
                area.spaces.active.clip_end = 1000.0


def export_fbx(objects: Iterable[bpy.types.Object]) -> None:
    export_objects = list(objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in export_objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = next(
        obj for obj in export_objects if obj.type == "ARMATURE"
    )

    bpy.ops.export_scene.fbx(
        filepath=str(FBX_PATH),
        use_selection=True,
        object_types={"ARMATURE", "MESH"},
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        add_leaf_bones=False,
        bake_anim=False,
        use_armature_deform_only=False,
        mesh_smooth_type="FACE",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clear_scene()
    configure_scene()

    body_collection = get_or_create_collection(BODY_COLLECTION_NAME)
    rig_collection = get_or_create_collection(RIG_COLLECTION_NAME)
    guide_collection = get_or_create_collection(GUIDE_COLLECTION_NAME)

    body_material = make_material(BASE_MATERIAL, (0.54, 0.57, 0.61, 1.0))
    guide_material = make_material(
        GUIDE_MATERIAL,
        (0.10, 0.43, 0.80, 1.0),
        metallic=0.05,
    )
    joint_material = make_material(JOINT_MATERIAL, (0.95, 0.33, 0.18, 1.0))

    armature = create_armature(rig_collection)
    body_parts = []

    for part_name, spec in PARTS.items():
        bevel = 0.13 if part_name == "Head" else 0.07
        part = add_rounded_box(
            name=part_name,
            size=spec["size"],
            location=spec["location"],
            collection=body_collection,
            material=body_material,
            bevel=bevel,
        )
        parent_part_to_bone(part, armature, part_name)
        body_parts.append(part)

    create_ground_guide(guide_collection, guide_material)
    create_height_ruler(guide_collection, guide_material)
    create_joint_guides(guide_collection, joint_material)

    guide_collection.hide_render = True

    # Save the editable source first, then export a Roblox-friendly FBX copy.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    export_fbx([armature, *body_parts])
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))

    print("=" * 72)
    print("Roblox avatar blueprint generated successfully")
    print(f"Blend: {BLEND_PATH}")
    print(f"FBX:   {FBX_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()
