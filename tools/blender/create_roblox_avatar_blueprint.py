"""Generate a classic blocky Roblox body on a modern R15-compatible rig.

Outputs:
  assets/generated/blocky_r15_blueprint.blend
  assets/generated/blocky_r15_blueprint.fbx

The visual proportions deliberately resemble the classic R6 body, while the
technical structure uses 15 body meshes, the standard R15 hierarchy, 19 avatar
attachment markers, rigid limb skinning, and optional spine/chest/clavicle bones.
Blender uses X width, Y depth, Z height; the character faces -Y. One unit is one stud.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "generated"
BLEND = OUT / "blocky_r15_blueprint.blend"
FBX = OUT / "blocky_r15_blueprint.fbx"

# size (X,Y,Z), world location, deform bone, bevel, flexible torso
PARTS = {
    "LowerTorso_Geo": ((2, 1, .82), (0, 0, 2.42), "LowerTorso", .045, False),
    "UpperTorso_Geo": ((2, 1, 1.22), (0, 0, 3.44), "UpperTorso", .045, True),
    "Head_Geo": ((2, 1, 1), (0, 0, 4.62), "Head", .06, False),
    "LeftUpperArm_Geo": ((1, 1, .78), (-1.5, 0, 3.65), "LeftUpperArm", .035, False),
    "LeftLowerArm_Geo": ((1, 1, .74), (-1.5, 0, 2.89), "LeftLowerArm", .035, False),
    "LeftHand_Geo": ((1, 1, .48), (-1.5, 0, 2.28), "LeftHand", .05, False),
    "RightUpperArm_Geo": ((1, 1, .78), (1.5, 0, 3.65), "RightUpperArm", .035, False),
    "RightLowerArm_Geo": ((1, 1, .74), (1.5, 0, 2.89), "RightLowerArm", .035, False),
    "RightHand_Geo": ((1, 1, .48), (1.5, 0, 2.28), "RightHand", .05, False),
    "LeftUpperLeg_Geo": ((1, 1, .78), (-.5, 0, 1.81), "LeftUpperLeg", .035, False),
    "LeftLowerLeg_Geo": ((1, 1, .74), (-.5, 0, 1.05), "LeftLowerLeg", .035, False),
    "LeftFoot_Geo": ((1, 1.18, .48), (-.5, -.09, .44), "LeftFoot", .05, False),
    "RightUpperLeg_Geo": ((1, 1, .78), (.5, 0, 1.81), "RightUpperLeg", .035, False),
    "RightLowerLeg_Geo": ((1, 1, .74), (.5, 0, 1.05), "RightLowerLeg", .035, False),
    "RightFoot_Geo": ((1, 1.18, .48), (.5, -.09, .44), "RightFoot", .05, False),
}

# head, tail, parent, deform. Root and LowerTorso begin at world origin as required.
BONES = {
    "Root": ((0, 0, 0), (0, 0, .25), None, False),
    "HumanoidRootNode": ((0, 0, 0), (0, 0, 2.01), "Root", False),
    "LowerTorso": ((0, 0, 0), (0, 0, 2.82), "HumanoidRootNode", True),
    "UpperTorso": ((0, 0, 2.82), (0, 0, 3.13), "LowerTorso", True),
    "Spine": ((0, 0, 3.13), (0, 0, 3.48), "UpperTorso", True),
    "Chest": ((0, 0, 3.48), (0, 0, 4.05), "Spine", True),
    "Head": ((0, 0, 4.05), (0, 0, 4.42), "Chest", True),
    "HeadBase": ((0, 0, 4.42), (0, 0, 5.12), "Head", True),
    "LeftClavicle": ((-.15, 0, 3.95), (-1, 0, 3.95), "Chest", True),
    "LeftUpperArm": ((-1, 0, 3.95), (-1.5, 0, 3.26), "LeftClavicle", True),
    "LeftLowerArm": ((-1.5, 0, 3.26), (-1.5, 0, 2.52), "LeftUpperArm", True),
    "LeftHand": ((-1.5, 0, 2.52), (-1.5, 0, 2.04), "LeftLowerArm", True),
    "RightClavicle": ((.15, 0, 3.95), (1, 0, 3.95), "Chest", True),
    "RightUpperArm": ((1, 0, 3.95), (1.5, 0, 3.26), "RightClavicle", True),
    "RightLowerArm": ((1.5, 0, 3.26), (1.5, 0, 2.52), "RightUpperArm", True),
    "RightHand": ((1.5, 0, 2.52), (1.5, 0, 2.04), "RightLowerArm", True),
    "LeftUpperLeg": ((-.5, 0, 2.01), (-.5, 0, 1.42), "LowerTorso", True),
    "LeftLowerLeg": ((-.5, 0, 1.42), (-.5, 0, .68), "LeftUpperLeg", True),
    "LeftFoot": ((-.5, 0, .68), (-.5, -.43, .31), "LeftLowerLeg", True),
    "RightUpperLeg": ((.5, 0, 2.01), (.5, 0, 1.42), "LowerTorso", True),
    "RightLowerLeg": ((.5, 0, 1.42), (.5, 0, .68), "RightUpperLeg", True),
    "RightFoot": ((.5, 0, .68), (.5, -.43, .31), "RightLowerLeg", True),
}

# location, parent bone, Euler rotation
ATTACHMENTS = {
    "FaceCenter_Att": ((0, -.51, 4.62), "Head", (0, 0, 0)),
    "FaceFront_Att": ((0, -.56, 4.62), "Head", (0, 0, 0)),
    "Hat_Att": ((0, 0, 5.12), "Head", (0, 0, 0)),
    "Hair_Att": ((0, .08, 5.05), "Head", (0, 0, 0)),
    "LeftCollar_Att": ((-.68, 0, 3.98), "Chest", (0, 0, 0)),
    "RightCollar_Att": ((.68, 0, 3.98), "Chest", (0, 0, 0)),
    "Neck_Att": ((0, 0, 4.05), "Chest", (0, 0, 0)),
    "BodyBack_Att": ((0, .51, 3.55), "Chest", (0, 0, 0)),
    "BodyFront_Att": ((0, -.51, 3.55), "Chest", (0, 0, 0)),
    "Root_Att": ((0, 0, 0), "LowerTorso", (0, 0, 0)),
    "WaistFront_Att": ((0, -.51, 2.42), "LowerTorso", (0, 0, 0)),
    "WaistBack_Att": ((0, .51, 2.42), "LowerTorso", (0, 0, 0)),
    "WaistCenter_Att": ((0, 0, 2.42), "LowerTorso", (0, 0, 0)),
    "LeftShoulder_Att": ((-1.98, 0, 3.65), "LeftUpperArm", (0, 0, 0)),
    "RightShoulder_Att": ((1.98, 0, 3.65), "RightUpperArm", (0, 0, 0)),
    "LeftGrip_Att": ((-1.5, -.52, 2.28), "LeftHand", (1.5708, 0, 0)),
    "RightGrip_Att": ((1.5, -.52, 2.28), "RightHand", (1.5708, 0, 0)),
    "LeftFoot_Att": ((-.5, -.42, .44), "LeftFoot", (0, 0, 0)),
    "RightFoot_Att": ((.5, -.42, .44), "RightFoot", (0, 0, 0)),
}


def clear_scene():
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def collection(name):
    value = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(value)
    return value


def move(obj, target):
    for owner in list(obj.users_collection):
        owner.objects.unlink(obj)
    target.objects.link(obj)


def material(name, color):
    value = bpy.data.materials.new(name)
    value.diffuse_color = color
    value.use_nodes = True
    shader = value.node_tree.nodes.get("Principled BSDF")
    if shader:
        shader.inputs["Base Color"].default_value = color
        shader.inputs["Roughness"].default_value = .72
    return value


def finish_block(obj, name, mat, bevel):
    obj.name = name
    obj.data.materials.append(mat)
    mod = obj.modifiers.new("Subtle Block Edge", "BEVEL")
    mod.width, mod.segments, mod.limit_method = bevel, 2, "ANGLE"
    normal = obj.modifiers.new("Weighted Normals", "WEIGHTED_NORMAL")
    normal.keep_sharp = True
    obj["roblox_body_part"] = name.removesuffix("_Geo")
    obj["roblox_scale"] = "Classic"
    obj["blueprint_version"] = 2
    return obj


def box(name, size, location, target, mat, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish_block(obj, name, mat, bevel)
    move(obj, target)
    return obj


def torso(name, size, location, target, mat, bevel):
    w, d, h = size
    x, y, z = location
    levels = [z - h / 2 + h * n / 4 for n in range(5)]
    vertices = []
    for level in levels:
        vertices += [(x-w/2, y-d/2, level), (x+w/2, y-d/2, level),
                     (x+w/2, y+d/2, level), (x-w/2, y+d/2, level)]
    faces = [(0, 3, 2, 1), (16, 17, 18, 19)]
    for ring in range(4):
        a, b = ring * 4, (ring + 1) * 4
        faces += [(a, a+1, b+1, b), (a+1, a+2, b+2, b+1),
                  (a+2, a+3, b+3, b+2), (a+3, a, b, b+3)]
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    target.objects.link(obj)
    return finish_block(obj, name, mat, bevel)


def armature(target):
    data = bpy.data.armatures.new("BlockyR15_Armature")
    rig = bpy.data.objects.new("BlockyR15_Rig", data)
    target.objects.link(rig)
    rig.show_in_front = True
    data.display_type = "OCTAHEDRAL"
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    for name, (head, tail, parent, deform) in BONES.items():
        bone = data.edit_bones.new(name)
        bone.head, bone.tail, bone.use_deform = head, tail, deform
        made[name] = bone
    for name, (_, _, parent, _) in BONES.items():
        if parent:
            made[name].parent = made[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.select_set(False)
    return rig


def armature_modifier(obj, rig):
    obj.parent = rig
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = rig


def rigid_weight(obj, rig, bone):
    armature_modifier(obj, rig)
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1, "REPLACE")


def torso_weights(obj, rig):
    armature_modifier(obj, rig)
    groups = {name: obj.vertex_groups.new(name=name) for name in
              ("UpperTorso", "Spine", "Chest", "LeftClavicle", "RightClavicle")}
    values = [vertex.co.z for vertex in obj.data.vertices]
    low, span = min(values), max(values) - min(values)
    for vertex in obj.data.vertices:
        t = (vertex.co.z - low) / span
        if t <= .25:
            weights = {"UpperTorso": 1}
        elif t <= .5:
            p = (t - .25) * 4
            weights = {"UpperTorso": 1-p, "Spine": p}
        elif t <= .75:
            p = (t - .5) * 4
            weights = {"Spine": 1-p, "Chest": p}
        else:
            weights = {"Chest": 1}
            edge = min(abs(vertex.co.x), 1)
            if edge > .55:
                amount = min((edge-.55)/.45*.35, .35)
                weights["Chest"] -= amount
                weights["LeftClavicle" if vertex.co.x < 0 else "RightClavicle"] = amount
        for name, weight in weights.items():
            if weight > 0:
                groups[name].add([vertex.index], weight, "REPLACE")


def head_weights(obj, rig):
    armature_modifier(obj, rig)
    head = obj.vertex_groups.new(name="Head")
    base = obj.vertex_groups.new(name="HeadBase")
    low = min(vertex.co.z for vertex in obj.data.vertices)
    high = max(vertex.co.z for vertex in obj.data.vertices)
    split = low + (high-low)*.22
    for vertex in obj.data.vertices:
        if vertex.co.z <= split:
            head.add([vertex.index], .75, "REPLACE")
            base.add([vertex.index], .25, "REPLACE")
        else:
            head.add([vertex.index], 1, "REPLACE")


def parent_bone(obj, rig, bone):
    world = obj.matrix_world.copy()
    obj.parent, obj.parent_type, obj.parent_bone = rig, "BONE", bone
    obj.matrix_world = world


def attachment_markers(target, rig, mat):
    result = []
    for name, (location, bone, rotation) in ATTACHMENTS.items():
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=.055, location=location)
        obj = bpy.context.active_object
        obj.name, obj.rotation_euler = name, rotation
        obj.data.materials.append(mat)
        obj.display_type, obj.hide_render = "WIRE", True
        obj["roblox_attachment"] = True
        move(obj, target)
        parent_bone(obj, rig, bone)
        result.append(obj)
    return result


def guides(target, guide_mat, joint_mat):
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, .18))
    ground = bpy.context.active_object
    ground.name, ground.display_type, ground.hide_render = "GUIDE_Ground", "WIRE", True
    ground.data.materials.append(guide_mat)
    move(ground, target)
    for name in BONES:
        if name in ("Root", "HumanoidRootNode"):
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=.06,
                                             location=BONES[name][0])
        point = bpy.context.active_object
        point.name, point.display_type, point.hide_render = "GUIDE_"+name, "WIRE", True
        point.data.materials.append(joint_mat)
        move(point, target)


def movement_preview(rig):
    action = bpy.data.actions.new("BlockyR15_MovementPreview")
    rig.animation_data_create()
    rig.animation_data.action = action
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 70
    names = [name for name in BONES if name not in ("Root", "HumanoidRootNode", "LowerTorso", "UpperTorso")]
    for frame in (1, 70):
        bpy.context.scene.frame_set(frame)
        for name in names:
            bone = rig.pose.bones.get(name)
            if bone:
                bone.rotation_mode = "XYZ"
                bone.rotation_euler = (0, 0, 0)
                bone.keyframe_insert("rotation_euler", frame=frame)
    pose = {
        "Spine": (.10, 0, .08), "Chest": (-.08, 0, -.12), "Head": (.05, 0, .18),
        "LeftClavicle": (0, 0, -.12), "RightClavicle": (0, 0, .12),
        "LeftUpperArm": (-.35, .10, -.30), "RightUpperArm": (-.50, -.10, .35),
        "LeftLowerArm": (-.65, 0, 0), "RightLowerArm": (-1.05, 0, 0),
        "LeftHand": (0, .18, 0), "RightHand": (0, -.22, 0),
        "LeftUpperLeg": (.32, 0, .08), "RightUpperLeg": (-.20, 0, -.05),
        "LeftLowerLeg": (-.58, 0, 0), "RightLowerLeg": (.18, 0, 0),
        "LeftFoot": (.25, 0, 0), "RightFoot": (-.12, 0, 0),
    }
    for name, rotation in pose.items():
        bone = rig.pose.bones.get(name)
        if bone:
            bone.rotation_mode, bone.rotation_euler = "XYZ", rotation
            bone.keyframe_insert("rotation_euler", frame=35)
    bpy.context.scene.frame_set(1)


def export(objects: Iterable[bpy.types.Object]):
    objects = list(objects)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.hide_set(False)
        obj.select_set(True)
    rig = next(obj for obj in objects if obj.type == "ARMATURE")
    bpy.context.view_layer.objects.active = rig
    bpy.ops.export_scene.fbx(filepath=str(FBX), use_selection=True,
        object_types={"ARMATURE", "MESH"}, apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
        add_leaf_bones=False, bake_anim=False, use_armature_deform_only=False,
        mesh_smooth_type="FACE")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    clear_scene()
    scene = bpy.context.scene
    scene.unit_settings.system, scene.unit_settings.scale_length = "NONE", 1
    scene["avatar_style"] = "Classic R6 silhouette with modern R15 articulation"
    scene["body_meshes"], scene["attachment_markers"], scene["blueprint_version"] = 15, 19, 2

    body_col, rig_col = collection("01_Body_Geometry"), collection("02_Rig")
    att_col, guide_col = collection("03_Attachments"), collection("04_Blueprint_Guides")
    body_mat = material("MAT_BlockyBlueprint", (.58, .61, .66, 1))
    att_mat = material("MAT_AttachmentGuide", (.97, .40, .12, 1))
    guide_mat = material("MAT_BlueprintGuide", (.08, .40, .90, 1))
    joint_mat = material("MAT_JointGuide", (.90, .10, .22, 1))

    rig = armature(rig_col)
    geometry = []
    for name, (size, location, bone, bevel, flexible) in PARTS.items():
        obj = torso(name, size, location, body_col, body_mat, bevel) if flexible else \
              box(name, size, location, body_col, body_mat, bevel)
        if flexible:
            torso_weights(obj, rig)
        elif name == "Head_Geo":
            head_weights(obj, rig)
        else:
            rigid_weight(obj, rig, bone)
        geometry.append(obj)

    attachments = attachment_markers(att_col, rig, att_mat)
    guides(guide_col, guide_mat, joint_mat)
    movement_preview(rig)
    guide_col.hide_render = True

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    export([rig, *geometry, *attachments])
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print(f"Generated {BLEND}")
    print(f"Generated {FBX}")
    print("Frame 35 contains a movement preview pose.")


if __name__ == "__main__":
    main()
