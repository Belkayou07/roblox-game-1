"""Sixth-generation blank anime Roblox mannequin.

V6 keeps the successful continuous-core direction from v5 and applies a focused
silhouette polish: sloped shoulders, deeper arm insertion, smaller articulation
gaps, shaped limbs, cleaner hands, and feet that reconnect at the ankle. The
asset remains bald, unclothed, neutral, modular, and reusable.
"""
from __future__ import annotations

import importlib.util
import math
import traceback
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import bpy

V5_PATH = Path(__file__).with_name("create_anime_roblox_base_mannequin_v5.py")
SPEC = importlib.util.spec_from_file_location("base_mannequin_v5", V5_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load v5 generator: {V5_PATH}")
v5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v5)
v4 = v5.v4
v3 = v5.v3
v2 = v5.v2
base = v5.base

base.TAG = "anime_roblox_base_mannequin_v6"
base.SHOULDER_X = 0.78
base.ELBOW_X = 1.76
base.WRIST_X = 2.72
base.HAND_TIP_X = 3.27
base.HIP_X = 0.30
base.Z_HIP = 3.15
base.Z_KNEE = 1.86
base.Z_ANKLE = 0.40
base.WARNINGS.clear()


def build_materials_v6() -> Dict[str, bpy.types.Material]:
    return v5.build_materials_v5()


def continuous_core_v6(
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Create one core with a softer chest, narrower pelvis, and sloped shoulders."""
    levels: Sequence[Tuple[float, float, float, float, float]] = (
        (3.08, 0.74, 0.54, 0.018, 0.000),
        (3.20, 0.84, 0.59, 0.022, 0.000),
        (3.38, 0.94, 0.63, 0.024, 0.000),
        (3.55, 0.96, 0.61, 0.018, 0.000),
        (3.72, 0.88, 0.55, 0.008, 0.000),
        (3.90, 0.82, 0.52, -0.002, 0.000),
        (4.08, 0.85, 0.54, -0.012, 0.000),
        (4.28, 0.96, 0.60, -0.022, 0.000),
        (4.49, 1.12, 0.67, -0.032, 0.000),
        (4.70, 1.30, 0.73, -0.040, 0.000),
        (4.90, 1.46, 0.77, -0.042, 0.020),
        (5.08, 1.54, 0.76, -0.035, 0.055),
        (5.20, 1.48, 0.70, -0.020, 0.105),
    )
    points = 28
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []

    for z, width, depth, center_y, shoulder_drop in levels:
        for index in range(points):
            angle = math.tau * index / points
            cx, sy = math.cos(angle), math.sin(angle)
            x = math.copysign(abs(cx) ** 0.86, cx) * width * 0.5
            y = center_y + math.copysign(abs(sy) ** 0.92, sy) * depth * 0.5
            ring_z = z
            if shoulder_drop:
                edge = min(1.0, abs(x) / max(width * 0.5, 1e-6))
                ring_z -= shoulder_drop * edge ** 1.8
            if y < center_y and z > 4.40:
                y -= 0.018 * ((z - 4.40) / 0.80)
            if y > center_y and z < 3.65:
                y -= 0.008
            verts.append((x, y, ring_z))

    for level in range(len(levels) - 1):
        current = level * points
        following = (level + 1) * points
        for index in range(points):
            nxt = (index + 1) % points
            faces.append((current + index, current + nxt, following + nxt, following + index))
    faces.append(tuple(reversed(range(points))))
    top = (len(levels) - 1) * points
    faces.append(tuple(top + index for index in range(points)))

    mesh = bpy.data.meshes.new("BODY_Core_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("BODY_Core", mesh)
    col.objects.link(obj)
    return base.finish(obj, "BODY_Core", col, mat, bevel_width=0.010, subdivision=1)


def neck_v6(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    return v2.rounded_loft(
        "BODY_Neck",
        (
            (5.12, 0.42, 0.32),
            (5.22, 0.35, 0.29),
            (5.35, 0.30, 0.26),
            (5.48, 0.32, 0.27),
            (5.55, 0.37, 0.30),
        ),
        col,
        mat,
        points=20,
        exponent_x=0.91,
        exponent_y=0.95,
    )


def horizontal_limb(
    name: str,
    levels: Sequence[Tuple[float, float, float, float]],
    side: str,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Build a shaped arm segment along X with an oval cross-section."""
    sign = -1.0 if side == "L" else 1.0
    points = 18
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    for x, depth, height, center_z in levels:
        for index in range(points):
            angle = math.tau * index / points
            y = math.cos(angle) * depth * 0.5
            z = center_z + math.sin(angle) * height * 0.5
            verts.append((sign * x, y, z))
    for level in range(len(levels) - 1):
        current = level * points
        following = (level + 1) * points
        for index in range(points):
            nxt = (index + 1) % points
            faces.append((current + index, current + nxt, following + nxt, following + index))
    faces.append(tuple(reversed(range(points))))
    top = (len(levels) - 1) * points
    faces.append(tuple(top + index for index in range(points)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return base.finish(obj, name, col, mat, bevel_width=0.018, subdivision=1)


def vertical_limb(
    name: str,
    levels: Sequence[Tuple[float, float, float, float]],
    side: str,
    col: bpy.types.Collection,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    """Build a shaped leg segment with a controlled thigh or calf profile."""
    sign = -1.0 if side == "L" else 1.0
    points = 18
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    for z, width, depth, center_y in levels:
        for index in range(points):
            angle = math.tau * index / points
            x = sign * base.HIP_X + math.cos(angle) * width * 0.5
            y = center_y + math.sin(angle) * depth * 0.5
            verts.append((x, y, z))
    for level in range(len(levels) - 1):
        current = level * points
        following = (level + 1) * points
        for index in range(points):
            nxt = (index + 1) % points
            faces.append((current + index, current + nxt, following + nxt, following + index))
    faces.append(tuple(reversed(range(points))))
    top = (len(levels) - 1) * points
    faces.append(tuple(top + index for index in range(points)))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    return base.finish(obj, name, col, mat, bevel_width=0.016, subdivision=1)


def hand_v6(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    """Create a slimmer single-piece neutral hand with a restrained thumb wedge."""
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    local = (
        (0.00, 0.080),
        (0.11, 0.100),
        (0.31, 0.094),
        (0.46, 0.060),
        (0.50, 0.015),
        (0.47, -0.045),
        (0.29, -0.070),
        (0.23, -0.120),
        (0.18, -0.175),
        (0.10, -0.128),
        (0.00, -0.082),
    )
    polygon = tuple((sign * (wrist + x), 4.98 + z) for x, z in local)
    if side == "L":
        polygon = tuple(reversed(polygon))
    return v5.extruded_polygon(f"BODY_Hand_{side}", polygon, 0.205, col, mat)


def foot_v6(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    """Create a simple foot with an integrated ankle rise and softer forefoot taper."""
    sign = -1.0 if side == "L" else 1.0
    x_center = sign * base.HIP_X
    half_width = 0.165
    side_profile = (
        (0.09, 0.08),
        (0.09, 0.37),
        (-0.02, 0.39),
        (-0.13, 0.31),
        (-0.33, 0.23),
        (-0.55, 0.16),
        (-0.61, 0.105),
        (-0.58, 0.078),
        (0.08, 0.078),
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
    return base.finish(obj, f"BODY_Foot_{side}", col, mat, bevel_width=0.030, subdivision=1)


def build_body_v6(cols, mats):
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
            (0.062, 0.037, 0.108),
            head_col, body_mat, 24, 16,
        )
        objects.append(ear)
        weights[ear.name] = "Head"

    core = continuous_core_v6(body_col, body_mat)
    objects.append(core)

    neck = neck_v6(body_col, body_mat)
    objects.append(neck)
    weights[neck.name] = "Neck"

    for side in ("L", "R"):
        upper_arm = horizontal_limb(
            f"BODY_UpperArm_{side}",
            (
                (0.66, 0.46, 0.47, 4.98),
                (0.82, 0.43, 0.44, 4.98),
                (1.24, 0.38, 0.40, 4.98),
                (base.ELBOW_X - 0.022, 0.31, 0.33, 4.98),
            ),
            side, body_col, body_mat,
        )
        lower_arm = horizontal_limb(
            f"BODY_LowerArm_{side}",
            (
                (base.ELBOW_X + 0.022, 0.31, 0.33, 4.98),
                (2.10, 0.34, 0.35, 4.98),
                (2.45, 0.29, 0.31, 4.98),
                (base.WRIST_X + 0.015, 0.23, 0.25, 4.98),
            ),
            side, body_col, body_mat,
        )
        hand = hand_v6(side, body_col, body_mat)
        for obj, bone in (
            (upper_arm, f"UpperArm_{side}"),
            (lower_arm, f"LowerArm_{side}"),
            (hand, f"Hand_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    for side in ("L", "R"):
        upper_leg = vertical_limb(
            f"BODY_UpperLeg_{side}",
            (
                (3.17, 0.47, 0.45, -0.005),
                (2.75, 0.44, 0.42, -0.010),
                (2.28, 0.39, 0.39, -0.015),
                (base.Z_KNEE + 0.022, 0.33, 0.34, -0.020),
            ),
            side, body_col, body_mat,
        )
        lower_leg = vertical_limb(
            f"BODY_LowerLeg_{side}",
            (
                (base.Z_KNEE - 0.022, 0.32, 0.33, -0.025),
                (1.48, 0.36, 0.38, -0.015),
                (1.05, 0.31, 0.34, -0.005),
                (0.42, 0.23, 0.27, 0.000),
            ),
            side, body_col, body_mat,
        )
        foot = foot_v6(side, body_col, body_mat)
        for obj, bone in (
            (upper_leg, f"UpperLeg_{side}"),
            (lower_leg, f"LowerLeg_{side}"),
            (foot, f"Foot_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    return objects, weights, core


def presentation_v6(cols, mats, rig):
    cameras, guides = v2.presentation_v2(cols, mats, rig)
    for name in ("front", "back", "side", "threequarter"):
        cameras[name].data.ortho_scale = 7.48
    cameras["side"].location = (11.5, -0.05, 3.18)
    base.point_at(cameras["side"], (0.0, -0.02, 3.18))
    cameras["threequarter"].location = (7.6, -8.7, 3.48)
    base.point_at(cameras["threequarter"], (0.0, -0.03, 3.18))
    return cameras, guides


def main_v6() -> None:
    base.log("Starting v6 blank anime Roblox base mannequin generation.")
    base.OUT.mkdir(parents=True, exist_ok=True)
    v2.clean_previous_v2()
    cols = {name: base.collection(name) for name in base.COLLECTIONS}
    mats = build_materials_v6()

    base.log("Building polished continuous core, shaped limbs, hands, and feet.")
    body, weights, core = build_body_v6(cols, mats)
    base.log("Building humanoid armature and IK controls.")
    rig = base.build_rig(cols["00_RIG"])
    base.log("Applying modular limb skinning and smooth core weights.")
    base.skin(body, rig, weights)
    v5.smooth_skin_core(core, rig)
    base.log("Creating Roblox attachment references and root proxy.")
    base.build_attachments(cols["08_ROBLOX_ATTACHMENTS"], rig, mats["proxy"])
    base.log("Creating T-pose and A-pose actions.")
    base.create_actions(rig)
    base.log("Creating LOD1 body copy.")
    lod = base.build_lod(body, cols["13_LOD"])
    base.link(rig, cols["12_EXPORT"])
    for obj in body:
        base.link(obj, cols["12_EXPORT"])

    base.log("Creating v6 presentation scene.")
    cameras, guides = presentation_v6(cols, mats, rig)
    v2.hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    try:
        base.log("Rendering v6 preview images.")
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
    base.log("V6 generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main_v6()
    except Exception:
        traceback.print_exc()
        raise
