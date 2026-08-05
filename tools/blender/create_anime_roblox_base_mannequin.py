"""Generate a blank anime-style Roblox base mannequin in Blender 4.2+.

The mannequin is deliberately neutral: bald, unclothed, unbranded, and free of
character-specific facial details. One Blender unit equals one Roblox stud. The
mannequin faces -Y and finishes in a T-pose.
"""
from __future__ import annotations

import math
import traceback
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import bpy
from mathutils import Vector

TAG = "anime_roblox_base_mannequin_v1"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "generated" / "anime_roblox_base_mannequin"
BLEND = OUT / "anime_roblox_base_mannequin.blend"
FBX = OUT / "anime_roblox_base_mannequin.fbx"
RENDERS = {
    "front": OUT / "base_mannequin_front.png",
    "side": OUT / "base_mannequin_side.png",
    "back": OUT / "base_mannequin_back.png",
    "threequarter": OUT / "base_mannequin_threequarter.png",
    "rig": OUT / "base_mannequin_rig.png",
}

COLLECTIONS = (
    "00_RIG", "01_BODY", "02_HEAD", "03_FACE", "04_HAIR", "05_CLOTHING",
    "06_BOOTS", "07_ACCESSORIES", "08_ROBLOX_ATTACHMENTS",
    "09_PREVIEW_GUIDES", "10_CAMERAS", "11_LIGHTING", "12_EXPORT", "13_LOD",
)

REQUIRED_OBJECTS = {
    "HEAD_Base", "BODY_Neck", "BODY_UpperTorso", "BODY_LowerTorso",
    "BODY_Pelvis", "BODY_UpperArm_L", "BODY_UpperArm_R", "BODY_LowerArm_L",
    "BODY_LowerArm_R", "BODY_Hand_L", "BODY_Hand_R", "BODY_UpperLeg_L",
    "BODY_UpperLeg_R", "BODY_LowerLeg_L", "BODY_LowerLeg_R", "BODY_Foot_L",
    "BODY_Foot_R", "RIG_AnimeRoblox", "HumanoidRootPart",
}
REQUIRED_BONES = {
    "Root", "Pelvis", "Spine_01", "Spine_02", "Chest", "Neck", "Head",
    "Clavicle_L", "UpperArm_L", "LowerArm_L", "Hand_L", "Clavicle_R",
    "UpperArm_R", "LowerArm_R", "Hand_R", "UpperLeg_L", "LowerLeg_L",
    "Foot_L", "Toe_L", "UpperLeg_R", "LowerLeg_R", "Foot_R", "Toe_R",
    "Hand_IK_L", "Hand_IK_R", "Foot_IK_L", "Foot_IK_R", "KneePole_L",
    "KneePole_R", "ElbowPole_L", "ElbowPole_R",
}

Z_ANKLE = 0.40
Z_KNEE = 1.82
Z_HIP = 3.30
Z_CHEST = 5.16
Z_NECK = 5.38
Z_HEAD_TOP = 6.32
Z_HEAD_CENTER = (Z_NECK + Z_HEAD_TOP) * 0.5
SHOULDER_X = 0.92
ELBOW_X = 2.00
WRIST_X = 3.02
HAND_TIP_X = 3.50
HIP_X = 0.34
WARNINGS: List[str] = []


def log(message: str) -> None:
    print(f"[BaseMannequin] {message}")


def warn(message: str) -> None:
    WARNINGS.append(message)
    print(f"[BaseMannequin][WARNING] {message}")


def mark(block) -> None:
    block["generated_by"] = TAG


def object_mode() -> None:
    obj = bpy.context.object
    if obj and obj.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def active(obj: bpy.types.Object) -> None:
    object_mode()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
        mark(col)
    elif col not in list(bpy.context.scene.collection.children):
        try:
            bpy.context.scene.collection.children.link(col)
        except RuntimeError:
            pass
    return col


def move(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    for current in list(obj.users_collection):
        current.objects.unlink(obj)
    col.objects.link(obj)


def link(obj: bpy.types.Object, col: bpy.types.Collection) -> None:
    if col.objects.get(obj.name) is None:
        col.objects.link(obj)


def clean_previous() -> None:
    object_mode()
    for obj in list(bpy.data.objects):
        if obj.get("generated_by") == TAG:
            bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        if action.get("generated_by") == TAG:
            bpy.data.actions.remove(action)
    for material in list(bpy.data.materials):
        if material.get("generated_by") == TAG and material.users == 0:
            bpy.data.materials.remove(material)
    for mesh in list(bpy.data.meshes):
        if mesh.get("generated_by") == TAG and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for name in COLLECTIONS:
        col = bpy.data.collections.get(name)
        if col and not col.objects and not col.children:
            bpy.data.collections.remove(col)


def apply_rotation_scale(obj: bpy.types.Object) -> None:
    active(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def smooth(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    try:
        obj.data.set_sharp_from_angle(angle=math.radians(55.0))
    except AttributeError:
        pass


def bevel(obj: bpy.types.Object, width: float, segments: int = 3) -> None:
    mod = obj.modifiers.new("Production_Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(30.0)
    active(obj)
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError as exc:
        warn(f"Could not apply bevel on {obj.name}: {exc}")


def subdivide(obj: bpy.types.Object, levels: int) -> None:
    mod = obj.modifiers.new("Production_Subdivision", "SUBSURF")
    mod.subdivision_type = "CATMULL_CLARK"
    mod.levels = levels
    mod.render_levels = levels
    active(obj)
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError as exc:
        warn(f"Could not apply subdivision on {obj.name}: {exc}")


def smart_uv(obj: bpy.types.Object) -> None:
    if obj.type != "MESH" or not obj.data.polygons:
        return
    try:
        active(obj)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")
    except RuntimeError as exc:
        object_mode()
        warn(f"UV generation failed for {obj.name}: {exc}")


def finish(
    obj: bpy.types.Object,
    name: str,
    col: bpy.types.Collection,
    material: bpy.types.Material,
    bevel_width: float = 0.0,
    subdivision: int = 0,
    use_uv: bool = True,
) -> bpy.types.Object:
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    mark(obj)
    mark(obj.data)
    move(obj, col)
    apply_rotation_scale(obj)
    if bevel_width:
        bevel(obj, bevel_width)
    if subdivision:
        subdivide(obj, subdivision)
    smooth(obj)
    if not obj.data.materials:
        obj.data.materials.append(material)
    if use_uv:
        smart_uv(obj)
    return obj


def material(
    name: str,
    color: Tuple[float, float, float, float],
    roughness: float = 0.8,
    metallic: float = 0.0,
    emission: float = 0.0,
) -> bpy.types.Material:
    old = bpy.data.materials.get(name)
    if old and old.get("generated_by") == TAG:
        bpy.data.materials.remove(old)
    mat = bpy.data.materials.new(name)
    mark(mat)
    mat.use_nodes = True
    mat.diffuse_color = color
    node = mat.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = color
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    if emission:
        node.inputs["Emission Color"].default_value = color
        node.inputs["Emission Strength"].default_value = emission
    return mat


def build_materials() -> Dict[str, bpy.types.Material]:
    return {
        "body": material("MAT_BlueprintBody", (0.52, 0.66, 0.72, 1.0), 0.82),
        "joint": material("MAT_BlueprintJoint", (0.38, 0.52, 0.58, 1.0), 0.86),
        "proxy": material("MAT_Proxy", (0.20, 0.55, 0.95, 0.18), 0.7),
        "rig": material("MAT_RigGuide", (0.98, 0.38, 0.10, 1.0), 0.45, 0.0, 0.25),
        "ground": material("MAT_Ground", (0.055, 0.06, 0.07, 1.0), 0.95),
    }


def sphere(
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    segments: int = 40,
    rings: int = 24,
    subdivision: int = 0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, col, mat, subdivision=subdivision)


def box(
    name: str,
    location: Sequence[float],
    dimensions: Sequence[float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    bevel_width: float = 0.06,
    rotation: Sequence[float] = (0.0, 0.0, 0.0),
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.dimensions = dimensions
    return finish(obj, name, col, mat, bevel_width=bevel_width)


def capsule(
    name: str,
    start: Sequence[float],
    end: Sequence[float],
    radius_start: float,
    radius_end: float,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    vertices: int = 32,
) -> bpy.types.Object:
    a, b = Vector(start), Vector(end)
    direction = b - a
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius_start,
        radius2=radius_end,
        depth=direction.length,
        end_fill_type="NGON",
        location=(a + b) * 0.5,
    )
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    obj.rotation_mode = "XYZ"
    return finish(obj, name, col, mat, bevel_width=min(radius_start, radius_end) * 0.22)


def loft(
    name: str,
    levels: Sequence[Tuple[float, float, float]],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    bevel_width: float = 0.035,
    subdivision: int = 1,
) -> bpy.types.Object:
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    points = 8
    for z, width, depth in levels:
        for index in range(points):
            angle = math.tau * index / points
            cx, sy = math.cos(angle), math.sin(angle)
            x = math.copysign(abs(cx) ** 0.72, cx) * width * 0.5
            y = math.copysign(abs(sy) ** 0.78, sy) * depth * 0.5
            verts.append((x, y, z))
    for level in range(len(levels) - 1):
        base, next_base = level * points, (level + 1) * points
        for index in range(points):
            nxt = (index + 1) % points
            faces.append((base + index, base + nxt, next_base + nxt, next_base + index))
    faces.append(tuple(reversed(range(points))))
    top = (len(levels) - 1) * points
    faces.append(tuple(top + index for index in range(points)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return finish(obj, name, col, mat, bevel_width=bevel_width, subdivision=subdivision)


def head(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, location=(0, 0, Z_HEAD_CENTER))
    obj = bpy.context.object
    obj.scale = (0.38, 0.405, 0.49)
    apply_rotation_scale(obj)
    for vertex in obj.data.vertices:
        co = vertex.co
        nz = co.z / 0.49
        if nz < 0.05:
            factor = 0.72 + 0.24 * ((nz + 1.0) / 1.05)
            co.x *= factor
            co.y *= 0.92 + 0.08 * factor
        if nz < -0.72:
            co.x *= 0.82
            co.y *= 0.90
        if co.y < -0.08:
            co.y = max(co.y, -0.365) * 0.94
        if nz > 0.52:
            co.x *= 1.04
            co.y *= 1.02
    return finish(obj, "HEAD_Base", col, mat, subdivision=1)


def join_meshes(
    objects: Sequence[bpy.types.Object],
    name: str,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name
    obj.data.name = f"{name}_Mesh"
    mark(obj)
    mark(obj.data)
    move(obj, col)
    if not obj.data.materials:
        obj.data.materials.append(mat)
    smart_uv(obj)
    return obj


def hand(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    parts: List[bpy.types.Object] = []
    parts.append(box(
        f"TMP_Palm_{side}",
        (sign * (WRIST_X + 0.22), -0.01, 4.98),
        (0.44, 0.34, 0.18), col, mat, 0.075,
    ))
    for index, (y, length) in enumerate(zip((-0.125, -0.042, 0.042, 0.125), (0.29, 0.34, 0.33, 0.27)), 1):
        start_x = sign * (WRIST_X + 0.39)
        end_x = sign * (WRIST_X + 0.39 + length)
        parts.append(capsule(
            f"TMP_Finger{index}_{side}", (start_x, y, 4.98), (end_x, y, 4.98),
            0.046, 0.038, col, mat, 16,
        ))
    parts.append(capsule(
        f"TMP_Thumb_{side}",
        (sign * (WRIST_X + 0.18), -0.17, 4.96),
        (sign * (WRIST_X + 0.38), -0.31, 4.91),
        0.055, 0.038, col, mat, 16,
    ))
    return join_meshes(parts, f"BODY_Hand_{side}", col, mat)


def build_body(cols, mats):
    body_col, head_col = cols["01_BODY"], cols["02_HEAD"]
    body_mat, joint_mat = mats["body"], mats["joint"]
    objects: List[bpy.types.Object] = []
    weights: Dict[str, str] = {}

    h = head(head_col, body_mat)
    objects.append(h); weights[h.name] = "Head"
    for side, sign in (("L", -1.0), ("R", 1.0)):
        ear = sphere(f"HEAD_Ear_{side}", (sign * 0.37, -0.005, 5.86),
                     (0.075, 0.035, 0.13), head_col, body_mat, 24, 16)
        objects.append(ear); weights[ear.name] = "Head"

    neck = capsule("BODY_Neck", (0, 0, Z_CHEST - 0.04), (0, 0, Z_NECK + 0.05),
                   0.19, 0.17, body_col, joint_mat, 32)
    objects.append(neck); weights[neck.name] = "Neck"

    upper = loft("BODY_UpperTorso", ((4.28, 0.98, 0.48), (4.53, 1.26, 0.56),
                 (4.88, 1.58, 0.62), (5.12, 1.72, 0.60)), body_col, body_mat, 0.045, 2)
    lower = loft("BODY_LowerTorso", ((3.82, 1.04, 0.48), (4.04, 0.94, 0.45),
                 (4.30, 1.00, 0.48)), body_col, body_mat, 0.04, 2)
    pelvis = loft("BODY_Pelvis", ((3.28, 0.90, 0.52), (3.48, 1.10, 0.58),
                  (3.70, 1.16, 0.58), (3.88, 1.04, 0.50)), body_col, body_mat, 0.05, 2)
    for obj, bone in ((upper, "Chest"), (lower, "Spine_01"), (pelvis, "Pelvis")):
        objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        upper_arm = capsule(f"BODY_UpperArm_{side}", (sign * 0.86, 0, 4.98),
                            (sign * 2.02, 0, 4.98), 0.245, 0.205, body_col, body_mat, 40)
        lower_arm = capsule(f"BODY_LowerArm_{side}", (sign * 1.97, 0, 4.98),
                            (sign * 3.04, 0, 4.98), 0.205, 0.145, body_col, body_mat, 40)
        elbow = sphere(f"BODY_ElbowGuide_{side}", (sign * ELBOW_X, 0, 4.98),
                       (0.215, 0.20, 0.20), body_col, joint_mat, 32, 20)
        hand_obj = hand(side, body_col, body_mat)
        for obj, bone in ((upper_arm, f"UpperArm_{side}"), (lower_arm, f"LowerArm_{side}"),
                          (elbow, f"LowerArm_{side}"), (hand_obj, f"Hand_{side}")):
            objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        upper_leg = capsule(f"BODY_UpperLeg_{side}", (sign * HIP_X, 0, 3.40),
                            (sign * HIP_X, 0, Z_KNEE), 0.29, 0.235, body_col, body_mat, 40)
        lower_leg = capsule(f"BODY_LowerLeg_{side}", (sign * HIP_X, 0, Z_KNEE),
                            (sign * HIP_X, 0, Z_ANKLE), 0.235, 0.17, body_col, body_mat, 40)
        knee = sphere(f"BODY_KneeGuide_{side}", (sign * HIP_X, -0.025, Z_KNEE),
                      (0.245, 0.225, 0.225), body_col, joint_mat, 32, 20)
        foot = box(f"BODY_Foot_{side}", (sign * HIP_X, -0.20, 0.19),
                   (0.43, 0.72, 0.34), body_col, body_mat, 0.105)
        toe = box(f"BODY_ToeGuide_{side}", (sign * HIP_X, -0.50, 0.17),
                  (0.45, 0.28, 0.25), body_col, joint_mat, 0.09)
        for obj, bone in ((upper_leg, f"UpperLeg_{side}"), (lower_leg, f"LowerLeg_{side}"),
                          (knee, f"LowerLeg_{side}"), (foot, f"Foot_{side}"),
                          (toe, f"Toe_{side}")):
            objects.append(obj); weights[obj.name] = bone
    return objects, weights


def build_rig(col: bpy.types.Collection) -> bpy.types.Object:
    data = bpy.data.armatures.new("RIG_AnimeRoblox_Armature")
    rig = bpy.data.objects.new("RIG_AnimeRoblox", data)
    mark(data); mark(rig)
    col.objects.link(rig)
    rig.show_in_front = True
    rig.display_type = "WIRE"

    specs = {
        "Root": ((0, 0, 3.24), (0, 0, 3.54), None, False),
        "Pelvis": ((0, 0, 3.30), (0, 0, 3.84), "Root", True),
        "Spine_01": ((0, 0, 3.84), (0, 0, 4.28), "Pelvis", True),
        "Spine_02": ((0, 0, 4.28), (0, 0, 4.72), "Spine_01", True),
        "Chest": ((0, 0, 4.72), (0, 0, 5.14), "Spine_02", True),
        "Neck": ((0, 0, 5.14), (0, 0, 5.39), "Chest", True),
        "Head": ((0, 0, 5.39), (0, 0, 6.18), "Neck", True),
        "Clavicle_L": ((-0.10, 0, 5.02), (-SHOULDER_X, 0, 4.98), "Chest", True),
        "UpperArm_L": ((-SHOULDER_X, 0, 4.98), (-ELBOW_X, 0, 4.98), "Clavicle_L", True),
        "LowerArm_L": ((-ELBOW_X, 0, 4.98), (-WRIST_X, 0, 4.98), "UpperArm_L", True),
        "Hand_L": ((-WRIST_X, 0, 4.98), (-HAND_TIP_X, 0, 4.98), "LowerArm_L", True),
        "Clavicle_R": ((0.10, 0, 5.02), (SHOULDER_X, 0, 4.98), "Chest", True),
        "UpperArm_R": ((SHOULDER_X, 0, 4.98), (ELBOW_X, 0, 4.98), "Clavicle_R", True),
        "LowerArm_R": ((ELBOW_X, 0, 4.98), (WRIST_X, 0, 4.98), "UpperArm_R", True),
        "Hand_R": ((WRIST_X, 0, 4.98), (HAND_TIP_X, 0, 4.98), "LowerArm_R", True),
        "UpperLeg_L": ((-HIP_X, 0, 3.38), (-HIP_X, 0, Z_KNEE), "Pelvis", True),
        "LowerLeg_L": ((-HIP_X, 0, Z_KNEE), (-HIP_X, 0, Z_ANKLE), "UpperLeg_L", True),
        "Foot_L": ((-HIP_X, 0, Z_ANKLE), (-HIP_X, -0.48, 0.20), "LowerLeg_L", True),
        "Toe_L": ((-HIP_X, -0.48, 0.20), (-HIP_X, -0.72, 0.18), "Foot_L", True),
        "UpperLeg_R": ((HIP_X, 0, 3.38), (HIP_X, 0, Z_KNEE), "Pelvis", True),
        "LowerLeg_R": ((HIP_X, 0, Z_KNEE), (HIP_X, 0, Z_ANKLE), "UpperLeg_R", True),
        "Foot_R": ((HIP_X, 0, Z_ANKLE), (HIP_X, -0.48, 0.20), "LowerLeg_R", True),
        "Toe_R": ((HIP_X, -0.48, 0.20), (HIP_X, -0.72, 0.18), "Foot_R", True),
        "Hand_IK_L": ((-WRIST_X, 0, 4.98), (-HAND_TIP_X, 0, 4.98), "Root", False),
        "Hand_IK_R": ((WRIST_X, 0, 4.98), (HAND_TIP_X, 0, 4.98), "Root", False),
        "Foot_IK_L": ((-HIP_X, 0, Z_ANKLE), (-HIP_X, -0.48, 0.20), "Root", False),
        "Foot_IK_R": ((HIP_X, 0, Z_ANKLE), (HIP_X, -0.48, 0.20), "Root", False),
        "KneePole_L": ((-HIP_X, -1.15, Z_KNEE), (-HIP_X, -1.15, Z_KNEE + 0.22), "Root", False),
        "KneePole_R": ((HIP_X, -1.15, Z_KNEE), (HIP_X, -1.15, Z_KNEE + 0.22), "Root", False),
        "ElbowPole_L": ((-ELBOW_X, -0.92, 4.98), (-ELBOW_X, -0.92, 5.20), "Root", False),
        "ElbowPole_R": ((ELBOW_X, -0.92, 4.98), (ELBOW_X, -0.92, 5.20), "Root", False),
    }
    active(rig)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    for name, (bone_head, bone_tail, parent, deform) in specs.items():
        bone = data.edit_bones.new(name)
        bone.head, bone.tail, bone.use_deform = bone_head, bone_tail, deform
        made[name] = bone
    for name, (_, _, parent, _) in specs.items():
        if parent:
            made[name].parent = made[parent]
    bpy.ops.object.mode_set(mode="POSE")
    for side in ("L", "R"):
        arm_ik = rig.pose.bones[f"LowerArm_{side}"].constraints.new("IK")
        arm_ik.name = f"IK_Arm_{side}"
        arm_ik.target = rig
        arm_ik.subtarget = f"Hand_IK_{side}"
        arm_ik.pole_target = rig
        arm_ik.pole_subtarget = f"ElbowPole_{side}"
        arm_ik.chain_count = 2
        arm_ik.pole_angle = -math.pi * 0.5 if side == "L" else math.pi * 0.5
        leg_ik = rig.pose.bones[f"LowerLeg_{side}"].constraints.new("IK")
        leg_ik.name = f"IK_Leg_{side}"
        leg_ik.target = rig
        leg_ik.subtarget = f"Foot_IK_{side}"
        leg_ik.pole_target = rig
        leg_ik.pole_subtarget = f"KneePole_{side}"
        leg_ik.chain_count = 2
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def rigid_skin(obj: bpy.types.Object, rig: bpy.types.Object, bone: str) -> None:
    obj.parent = rig
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    group = obj.vertex_groups.get(bone) or obj.vertex_groups.new(name=bone)
    group.add(range(len(obj.data.vertices)), 1.0, "REPLACE")
    obj["primary_deform_bone"] = bone


def skin(objects, rig, weights) -> None:
    for obj in objects:
        if obj.name in weights:
            rigid_skin(obj, rig, weights[obj.name])


def attachment(name, location, col, rig, bone):
    empty = bpy.data.objects.new(name, None)
    mark(empty)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.075
    empty.location = location
    col.objects.link(empty)
    empty.parent = rig
    empty.parent_type = "BONE"
    empty.parent_bone = bone
    empty.matrix_parent_inverse = rig.matrix_world.inverted()
    return empty


def build_attachments(col, rig, proxy_mat):
    specs = {
        "RootAttachment": ((0, 0, 3.38), "Root"),
        "WaistRigAttachment": ((0, 0, 3.70), "Pelvis"),
        "NeckRigAttachment": ((0, 0, 5.25), "Neck"),
        "LeftShoulderRigAttachment": ((-SHOULDER_X, 0, 4.98), "Clavicle_L"),
        "RightShoulderRigAttachment": ((SHOULDER_X, 0, 4.98), "Clavicle_R"),
        "LeftGripAttachment": ((-3.32, -0.02, 4.98), "Hand_L"),
        "RightGripAttachment": ((3.32, -0.02, 4.98), "Hand_R"),
        "LeftFootAttachment": ((-HIP_X, -0.48, 0.18), "Foot_L"),
        "RightFootAttachment": ((HIP_X, -0.48, 0.18), "Foot_R"),
        "FaceFrontAttachment": ((0, -0.37, 5.90), "Head"),
        "HairAttachment": ((0, 0, 6.24), "Head"),
        "HatAttachment": ((0, 0, 6.31), "Head"),
    }
    for name, (location, bone) in specs.items():
        attachment(name, location, col, rig, bone)
    proxy = box("HumanoidRootPart", (0, 0, 3.64), (1.20, 0.62, 1.35), col, proxy_mat, 0.03)
    proxy.display_type = "WIRE"
    proxy.hide_render = True
    proxy.show_in_front = True
    proxy.parent = rig
    proxy.parent_type = "BONE"
    proxy.parent_bone = "Root"


def create_actions(rig):
    rig.animation_data_create()
    def clear():
        for pose_bone in rig.pose.bones:
            pose_bone.rotation_mode = "XYZ"
            pose_bone.location = (0, 0, 0)
            pose_bone.rotation_euler = (0, 0, 0)
            pose_bone.scale = (1, 1, 1)
    t_pose = bpy.data.actions.new("POSE_T_Pose"); mark(t_pose)
    rig.animation_data.action = t_pose
    clear()
    for name in ("Hand_IK_L", "Hand_IK_R", "Foot_IK_L", "Foot_IK_R"):
        rig.pose.bones[name].keyframe_insert("location", frame=1, group=name)
    a_pose = bpy.data.actions.new("POSE_A_Pose"); mark(a_pose)
    rig.animation_data.action = a_pose
    clear()
    rig.pose.bones["Hand_IK_L"].location = (0.33, 0, -0.92)
    rig.pose.bones["Hand_IK_R"].location = (-0.33, 0, -0.92)
    rig.pose.bones["ElbowPole_L"].location = (0, -0.18, -0.16)
    rig.pose.bones["ElbowPole_R"].location = (0, -0.18, -0.16)
    for name in ("Hand_IK_L", "Hand_IK_R", "ElbowPole_L", "ElbowPole_R"):
        rig.pose.bones[name].keyframe_insert("location", frame=1, group=name)
    rig.animation_data.action = t_pose
    bpy.context.scene.frame_set(1)


def build_lod(objects, col):
    result = []
    for source in objects:
        if source.type != "MESH":
            continue
        obj = source.copy()
        obj.data = source.data.copy()
        obj.animation_data_clear()
        obj.name = f"{source.name}_LOD1"
        obj.data.name = f"{obj.name}_Mesh"
        mark(obj); mark(obj.data)
        col.objects.link(obj)
        obj.parent = None
        obj.matrix_world = source.matrix_world.copy()
        for mod in list(obj.modifiers):
            obj.modifiers.remove(mod)
        for group in list(obj.vertex_groups):
            obj.vertex_groups.remove(group)
        decimate = obj.modifiers.new("LOD_Decimate", "DECIMATE")
        decimate.ratio = 0.55
        active(obj)
        try:
            bpy.ops.object.modifier_apply(modifier=decimate.name)
        except RuntimeError as exc:
            warn(f"LOD decimation failed for {obj.name}: {exc}")
        obj.hide_render = True
        obj.hide_set(True)
        result.append(obj)
    return result


def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def camera(name, location, target, col, ortho=True):
    data = bpy.data.cameras.new(f"{name}_Data")
    obj = bpy.data.objects.new(name, data)
    mark(data); mark(obj)
    col.objects.link(obj)
    obj.location = location
    point_at(obj, target)
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = 7.15
    else:
        data.type = "PERSP"
        data.lens = 58
    return obj


def light(name, location, energy, size, col):
    data = bpy.data.lights.new(f"{name}_Data", "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    mark(data); mark(obj)
    col.objects.link(obj)
    obj.location = location
    point_at(obj, (0, 0, 3.2))
    return obj


def rig_guides(rig, col, mat):
    guides = []
    for bone in rig.data.bones:
        if not bone.use_deform:
            continue
        start = rig.matrix_world @ bone.head_local
        end = rig.matrix_world @ bone.tail_local
        guide = capsule(f"PREVIEW_Bone_{bone.name}", start, end, 0.035, 0.025, col, mat, 12)
        joint = sphere(f"PREVIEW_Joint_{bone.name}", start, (0.065, 0.065, 0.065), col, mat, 12, 8)
        guide.hide_render = True
        joint.hide_render = True
        guides.extend((guide, joint))
    return guides


def presentation(cols, mats, rig):
    scene = bpy.context.scene
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    scene.unit_settings.system = "NONE"
    scene.unit_settings.scale_length = 1.0
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass
    if scene.world is None:
        scene.world = bpy.data.worlds.new("BaseMannequinWorld")
        mark(scene.world)
    scene.world.color = (0.025, 0.028, 0.032)
    if scene.world.use_nodes:
        background = scene.world.node_tree.nodes.get("Background")
        if background:
            background.inputs["Color"].default_value = (0.025, 0.028, 0.032, 1)
            background.inputs["Strength"].default_value = 0.42
    box("PREVIEW_Ground", (0, 0, -0.08), (9, 9, 0.12), cols["09_PREVIEW_GUIDES"], mats["ground"], 0.04)
    light("LIGHT_Key", (-4, -5, 7), 1150, 4, cols["11_LIGHTING"])
    light("LIGHT_Fill", (4.5, -2, 5), 650, 3.5, cols["11_LIGHTING"])
    light("LIGHT_Rim", (0, 4.5, 6.5), 950, 3, cols["11_LIGHTING"])
    cameras = {
        "front": camera("CAM_Front", (0, -11, 3.25), (0, 0, 3.25), cols["10_CAMERAS"]),
        "side": camera("CAM_Side", (11, 0, 3.25), (0, 0, 3.25), cols["10_CAMERAS"]),
        "back": camera("CAM_Back", (0, 11, 3.25), (0, 0, 3.25), cols["10_CAMERAS"]),
        "threequarter": camera("CAM_ThreeQuarter", (7.8, -7.8, 3.65), (0, 0, 3.25), cols["10_CAMERAS"]),
        "perspective": camera("CAM_Perspective", (6.8, -8.2, 4.2), (0, 0, 3.25), cols["10_CAMERAS"], False),
    }
    return cameras, rig_guides(rig, cols["09_PREVIEW_GUIDES"], mats["rig"])


def triangles(objects: Iterable[bpy.types.Object]) -> int:
    total = 0
    for obj in objects:
        if obj.type == "MESH":
            obj.data.calc_loop_triangles()
            total += len(obj.data.loop_triangles)
    return total


def bounds(objects):
    points = [obj.matrix_world @ Vector(corner) for obj in objects if obj.type == "MESH" for corner in obj.bound_box]
    if not points:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    minimum = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maximum = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return minimum, maximum


def validate_weights(objects):
    normalized, over_four = True, False
    for obj in objects:
        if obj.type != "MESH" or not obj.vertex_groups:
            continue
        for vertex in obj.data.vertices:
            values = [group.weight for group in vertex.groups if group.weight > 1e-5]
            over_four |= len(values) > 4
            if values and abs(sum(values) - 1.0) > 1e-3:
                normalized = False
    return normalized, over_four


def export_fbx(rig, objects):
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    try:
        bpy.ops.export_scene.fbx(
            filepath=str(FBX), use_selection=True, object_types={"ARMATURE", "MESH"},
            use_mesh_modifiers=True, add_leaf_bones=False, use_armature_deform_only=True,
            bake_anim=False, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
            axis_forward="-Z", axis_up="Y",
        )
    except TypeError:
        warn("Full FBX options unavailable; retrying with core Roblox axes.")
        bpy.ops.export_scene.fbx(
            filepath=str(FBX), use_selection=True, object_types={"ARMATURE", "MESH"},
            add_leaf_bones=False, bake_anim=False, axis_forward="-Z", axis_up="Y",
        )


def render(cameras, guides):
    scene = bpy.context.scene
    for guide in guides:
        guide.hide_render = True
    for view in ("front", "side", "back", "threequarter"):
        scene.camera = cameras[view]
        scene.render.filepath = str(RENDERS[view])
        bpy.ops.render.render(write_still=True)
        log(f"Rendered {view}: {RENDERS[view]}")
    for guide in guides:
        guide.hide_render = False
    scene.camera = cameras["front"]
    scene.render.filepath = str(RENDERS["rig"])
    bpy.ops.render.render(write_still=True)
    for guide in guides:
        guide.hide_render = True


def validation(rig, body, lod):
    generated = [obj for obj in bpy.data.objects if obj.get("generated_by") == TAG]
    meshes = [obj for obj in generated if obj.type == "MESH"]
    materials = [mat for mat in bpy.data.materials if mat.get("generated_by") == TAG]
    bones = list(rig.data.bones)
    deform = [bone for bone in bones if bone.use_deform]
    minimum, maximum = bounds(body)
    normalized, over_four = validate_weights(body)
    missing_objects = sorted(REQUIRED_OBJECTS.difference(bpy.data.objects.keys()))
    missing_bones = sorted(REQUIRED_BONES.difference(rig.data.bones.keys()))
    bad_transforms = [obj.name for obj in body if any(abs(value - 1) > 1e-4 for value in obj.scale)]
    duplicate_names = len({obj.name for obj in generated}) != len(generated)
    result = lambda condition: "PASS" if condition else "FAIL"
    print("\n========== BASE MANNEQUIN VALIDATION ==========")
    print(f"Generated objects: {len(generated)}")
    print(f"Generated meshes: {len(meshes)}")
    print(f"Bones: {len(bones)}")
    print(f"Deform bones: {len(deform)}")
    print(f"Materials: {len(materials)}")
    print(f"High-detail triangles: {triangles(body)}")
    print(f"LOD1 triangles: {triangles(lod)}")
    print(f"Character height: {maximum.z - minimum.z:.3f} studs")
    print(f"Required objects: {result(not missing_objects)} {missing_objects or ''}")
    print(f"Required bones: {result(not missing_bones)} {missing_bones or ''}")
    print(f"Applied body transforms: {result(not bad_transforms)} {bad_transforms or ''}")
    print(f"Weights normalized: {result(normalized)}")
    print(f"Maximum four influences: {result(not over_four)}")
    print(f"No duplicate generated object names: {result(not duplicate_names)}")
    print(f"Blend path: {BLEND}")
    print(f"FBX path: {FBX}")
    for name, path in RENDERS.items():
        print(f"Render {name}: {path}")
    if WARNINGS:
        print("Warnings:")
        for message in WARNINGS:
            print(f"  - {message}")
    else:
        print("Warnings: none")
    print("===============================================\n")


def main() -> None:
    log("Starting blank anime Roblox base mannequin generation.")
    OUT.mkdir(parents=True, exist_ok=True)
    clean_previous()
    cols = {name: collection(name) for name in COLLECTIONS}
    mats = build_materials()
    log("Building blank body geometry.")
    body, weights = build_body(cols, mats)
    log("Building humanoid armature and IK controls.")
    rig = build_rig(cols["00_RIG"])
    log("Applying stable modular skinning.")
    skin(body, rig, weights)
    log("Creating Roblox attachment references and root proxy.")
    build_attachments(cols["08_ROBLOX_ATTACHMENTS"], rig, mats["proxy"])
    log("Creating T-pose and A-pose actions.")
    create_actions(rig)
    log("Creating LOD1 body copy.")
    lod = build_lod(body, cols["13_LOD"])
    link(rig, cols["12_EXPORT"])
    for obj in body:
        link(obj, cols["12_EXPORT"])
    log("Creating neutral presentation scene.")
    cameras, guides = presentation(cols, mats, rig)
    log("Saving Blender source file.")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    try:
        log("Rendering preview images.")
        render(cameras, guides)
    except Exception as exc:
        warn(f"Preview rendering did not complete: {exc}")
        traceback.print_exc()
    try:
        log("Exporting Roblox-oriented FBX.")
        export_fbx(rig, body)
    except Exception as exc:
        warn(f"FBX export did not complete: {exc}")
        traceback.print_exc()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    validation(rig, body, lod)
    log("Generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
