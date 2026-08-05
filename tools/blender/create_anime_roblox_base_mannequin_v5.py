"""Fifth-generation blank anime Roblox mannequin.

V5 replaces the bridge-heavy v4 construction with a cleaner production
blueprint: one continuous torso/pelvis core, simple inset limbs, clean joint
gaps, a single-piece mitten hand, and a single-piece wedge foot. The result
remains bald, unclothed, neutral, modular, and reusable.
"""
from __future__ import annotations

import importlib.util
import math
import traceback
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import bpy
from mathutils import Vector

V4_PATH = Path(__file__).with_name("create_anime_roblox_base_mannequin_v4.py")
SPEC = importlib.util.spec_from_file_location("base_mannequin_v4", V4_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load v4 generator: {V4_PATH}")
v4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v4)
v3 = v4.v3
v2 = v4.v2
base = v4.base

base.TAG = "anime_roblox_base_mannequin_v5"
base.SHOULDER_X = 0.82
base.ELBOW_X = 1.82
base.WRIST_X = 2.75
base.HAND_TIP_X = 3.30
base.HIP_X = 0.30
base.Z_HIP = 3.16
base.Z_KNEE = 1.86
base.Z_ANKLE = 0.46
base.WARNINGS.clear()
base.REQUIRED_OBJECTS = (
    base.REQUIRED_OBJECTS
    - {"BODY_UpperTorso", "BODY_LowerTorso", "BODY_Pelvis"}
    | {"BODY_Core"}
)


def build_materials_v5() -> Dict[str, bpy.types.Material]:
    body = base.material("MAT_BlueprintBody", (0.070, 0.255, 0.405, 1.0), 0.90)
    return {
        "body": body,
        "joint": body,
        "proxy": base.material("MAT_Proxy", (0.08, 0.42, 0.95, 0.16), 0.75),
        "rig": base.material("MAT_RigGuide", (1.0, 0.13, 0.025, 1.0), 0.38, 0.0, 1.6),
        "ground": base.material("MAT_Ground", (0.018, 0.023, 0.030, 1.0), 0.96),
    }


def continuous_core(
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Create one uninterrupted torso/pelvis mesh with a readable side profile."""
    levels: Sequence[Tuple[float, float, float, float]] = (
        (3.08, 0.78, 0.55, 0.018),
        (3.20, 0.88, 0.61, 0.022),
        (3.38, 1.00, 0.66, 0.025),
        (3.56, 1.02, 0.64, 0.020),
        (3.72, 0.92, 0.56, 0.010),
        (3.88, 0.82, 0.50, 0.000),
        (4.05, 0.83, 0.51, -0.008),
        (4.23, 0.94, 0.58, -0.016),
        (4.45, 1.12, 0.66, -0.026),
        (4.68, 1.34, 0.73, -0.036),
        (4.90, 1.54, 0.78, -0.042),
        (5.08, 1.66, 0.78, -0.036),
        (5.22, 1.64, 0.72, -0.020),
    )
    points = 24
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    for z, width, depth, center_y in levels:
        for index in range(points):
            angle = math.tau * index / points
            cx, sy = math.cos(angle), math.sin(angle)
            x = math.copysign(abs(cx) ** 0.84, cx) * width * 0.5
            y = center_y + math.copysign(abs(sy) ** 0.90, sy) * depth * 0.5
            if y < center_y and z > 4.35:
                y -= 0.018 * ((z - 4.35) / 0.87)
            if y > center_y and z < 3.70:
                y -= 0.010
            verts.append((x, y, z))
    for level in range(len(levels) - 1):
        current = level * points
        nxt_level = (level + 1) * points
        for index in range(points):
            nxt = (index + 1) % points
            faces.append((current + index, current + nxt, nxt_level + nxt, nxt_level + index))
    faces.append(tuple(reversed(range(points))))
    top = (len(levels) - 1) * points
    faces.append(tuple(top + index for index in range(points)))

    mesh = bpy.data.meshes.new("BODY_Core_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("BODY_Core", mesh)
    col.objects.link(obj)
    return base.finish(obj, "BODY_Core", col, mat, bevel_width=0.012, subdivision=1)


def neck_v5(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    return v2.rounded_loft(
        "BODY_Neck",
        (
            (5.14, 0.39, 0.31),
            (5.23, 0.34, 0.28),
            (5.36, 0.30, 0.26),
            (5.48, 0.32, 0.27),
            (5.54, 0.36, 0.29),
        ),
        col,
        mat,
        points=18,
        exponent_x=0.90,
        exponent_y=0.94,
    )


def extruded_polygon(
    name: str,
    polygon: Sequence[Tuple[float, float]],
    depth: float,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Extrude an X/Z silhouette through Y as one clean watertight mesh."""
    half = depth * 0.5
    count = len(polygon)
    verts = [(x, -half, z) for x, z in polygon] + [(x, half, z) for x, z in polygon]
    faces: List[Tuple[int, ...]] = []
    faces.append(tuple(reversed(range(count))))
    faces.append(tuple(count + index for index in range(count)))
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return base.finish(obj, name, col, mat, bevel_width=0.028, subdivision=1)


def hand_v5(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    """Create one neutral mitten hand with a restrained integrated thumb."""
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    local = (
        (0.00, 0.095),
        (0.19, 0.115),
        (0.43, 0.085),
        (0.52, 0.040),
        (0.52, -0.025),
        (0.31, -0.070),
        (0.22, -0.095),
        (0.30, -0.195),
        (0.21, -0.225),
        (0.10, -0.120),
        (0.00, -0.095),
    )
    polygon = tuple((sign * (wrist + x), 4.98 + z) for x, z in local)
    return extruded_polygon(f"BODY_Hand_{side}", polygon, 0.235, col, mat)


def foot_v5(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    """Create one wedge foot with no separate toe blobs."""
    sign = -1.0 if side == "L" else 1.0
    x_center = sign * base.HIP_X
    half_width = 0.175
    side_profile = (
        (0.10, 0.10),
        (0.08, 0.31),
        (-0.10, 0.34),
        (-0.30, 0.26),
        (-0.57, 0.18),
        (-0.62, 0.105),
        (-0.58, 0.075),
        (0.08, 0.075),
    )
    count = len(side_profile)
    left_x = x_center - half_width
    right_x = x_center + half_width
    verts = [(left_x, y, z) for y, z in side_profile] + [(right_x, y, z) for y, z in side_profile]
    faces: List[Tuple[int, ...]] = [tuple(reversed(range(count))), tuple(count + i for i in range(count))]
    for index in range(count):
        nxt = (index + 1) % count
        faces.append((index, nxt, count + nxt, count + index))
    mesh = bpy.data.meshes.new(f"BODY_Foot_{side}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(f"BODY_Foot_{side}", mesh)
    col.objects.link(obj)
    return base.finish(obj, f"BODY_Foot_{side}", col, mat, bevel_width=0.035, subdivision=1)


def build_body_v5(cols, mats):
    body_col, head_col = cols["01_BODY"], cols["02_HEAD"]
    body_mat = mats["body"]
    objects: List[bpy.types.Object] = []
    weights: Dict[str, str] = {}

    head = v2.head_v2(head_col, body_mat)
    objects.append(head)
    weights[head.name] = "Head"
    for side, sign in (("L", -1.0), ("R", 1.0)):
        ear = base.sphere(
            f"HEAD_Ear_{side}",
            (sign * 0.365, -0.005, 5.86),
            (0.064, 0.038, 0.110),
            head_col, body_mat, 24, 16,
        )
        objects.append(ear)
        weights[ear.name] = "Head"

    core = continuous_core(body_col, body_mat)
    objects.append(core)

    neck = neck_v5(body_col, body_mat)
    objects.append(neck)
    weights[neck.name] = "Neck"

    for side, sign in (("L", -1.0), ("R", 1.0)):
        upper_arm = base.capsule(
            f"BODY_UpperArm_{side}",
            (sign * 0.76, 0.0, 4.98),
            (sign * (base.ELBOW_X - 0.04), 0.0, 4.98),
            0.215, 0.165, body_col, body_mat, 40,
        )
        lower_arm = base.capsule(
            f"BODY_LowerArm_{side}",
            (sign * (base.ELBOW_X + 0.04), 0.0, 4.98),
            (sign * (base.WRIST_X + 0.02), 0.0, 4.98),
            0.165, 0.120, body_col, body_mat, 40,
        )
        hand = hand_v5(side, body_col, body_mat)
        for obj, bone in (
            (upper_arm, f"UpperArm_{side}"),
            (lower_arm, f"LowerArm_{side}"),
            (hand, f"Hand_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        upper_leg = base.capsule(
            f"BODY_UpperLeg_{side}",
            (sign * base.HIP_X, 0.0, 3.18),
            (sign * base.HIP_X, -0.012, base.Z_KNEE + 0.045),
            0.220, 0.175, body_col, body_mat, 40,
        )
        lower_leg = base.capsule(
            f"BODY_LowerLeg_{side}",
            (sign * base.HIP_X, -0.012, base.Z_KNEE - 0.045),
            (sign * base.HIP_X, 0.0, base.Z_ANKLE + 0.025),
            0.175, 0.120, body_col, body_mat, 40,
        )
        foot = foot_v5(side, body_col, body_mat)
        for obj, bone in (
            (upper_leg, f"UpperLeg_{side}"),
            (lower_leg, f"LowerLeg_{side}"),
            (foot, f"Foot_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    return objects, weights, core


def smooth_skin_core(core: bpy.types.Object, rig: bpy.types.Object) -> None:
    """Weight the single core across pelvis and spine bones with two influences max."""
    core.parent = rig
    mod = core.modifiers.new("Armature", "ARMATURE")
    mod.object = rig
    groups = {
        name: core.vertex_groups.new(name=name)
        for name in ("Pelvis", "Spine_01", "Spine_02", "Chest")
    }

    def weights_for_z(z: float) -> Dict[str, float]:
        if z <= 3.58:
            return {"Pelvis": 1.0}
        if z < 3.88:
            t = (z - 3.58) / 0.30
            return {"Pelvis": 1.0 - t, "Spine_01": t}
        if z <= 4.20:
            return {"Spine_01": 1.0}
        if z < 4.50:
            t = (z - 4.20) / 0.30
            return {"Spine_01": 1.0 - t, "Spine_02": t}
        if z <= 4.76:
            return {"Spine_02": 1.0}
        if z < 5.05:
            t = (z - 4.76) / 0.29
            return {"Spine_02": 1.0 - t, "Chest": t}
        return {"Chest": 1.0}

    for vertex in core.data.vertices:
        for name, value in weights_for_z(vertex.co.z).items():
            groups[name].add([vertex.index], value, "REPLACE")
    core["primary_deform_bone"] = "Spine_01"


def presentation_v5(cols, mats, rig):
    cameras, guides = v2.presentation_v2(cols, mats, rig)
    for name in ("front", "back", "side", "threequarter"):
        cameras[name].data.ortho_scale = 7.58
    cameras["side"].location = (11.5, -0.10, 3.18)
    base.point_at(cameras["side"], (0.0, -0.02, 3.18))
    cameras["threequarter"].location = (7.5, -8.8, 3.50)
    base.point_at(cameras["threequarter"], (0.0, -0.03, 3.18))
    return cameras, guides


def main_v5() -> None:
    base.log("Starting v5 blank anime Roblox base mannequin generation.")
    base.OUT.mkdir(parents=True, exist_ok=True)
    v2.clean_previous_v2()
    cols = {name: base.collection(name) for name in base.COLLECTIONS}
    mats = build_materials_v5()

    base.log("Building continuous torso core and simplified clean limbs.")
    body, weights, core = build_body_v5(cols, mats)
    base.log("Building humanoid armature and IK controls.")
    rig = base.build_rig(cols["00_RIG"])
    base.log("Applying modular limb skinning and smooth core weights.")
    base.skin(body, rig, weights)
    smooth_skin_core(core, rig)
    base.log("Creating Roblox attachment references and root proxy.")
    base.build_attachments(cols["08_ROBLOX_ATTACHMENTS"], rig, mats["proxy"])
    base.log("Creating T-pose and A-pose actions.")
    base.create_actions(rig)
    base.log("Creating LOD1 body copy.")
    lod = base.build_lod(body, cols["13_LOD"])
    base.link(rig, cols["12_EXPORT"])
    for obj in body:
        base.link(obj, cols["12_EXPORT"])

    base.log("Creating v5 presentation scene.")
    cameras, guides = presentation_v5(cols, mats, rig)
    v2.hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    try:
        base.log("Rendering v5 preview images.")
        v2.render_v2(cameras, guides)
    except Exception as exc:
        base.warn(f"Preview rendering did not complete: {exc}")
        traceback.print_exc()
    try:
        base.log("Exporting Roblox-oriented FBX.")
        base.export_fbx(rig, body)
    except Exception as exc:
        base.warn(f"FBX export did not complete: {exc}")
        traceback.print_exc()
    v2.hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    base.validation(rig, body, lod)
    base.log("V5 generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main_v5()
    except Exception:
        traceback.print_exc()
        raise
