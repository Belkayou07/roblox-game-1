"""Third-generation blank anime Roblox mannequin.

Extends the tested v2 pipeline and refines only the mannequin anatomy:
neck flow, shoulder integration, pelvis/hips, hands, bare feet, and side depth.
The asset remains bald, unclothed, neutral, and character-agnostic.
"""
from __future__ import annotations

import importlib.util
import math
import traceback
from pathlib import Path
from typing import Dict, List, Tuple

import bpy

V2_PATH = Path(__file__).with_name("create_anime_roblox_base_mannequin_v2.py")
SPEC = importlib.util.spec_from_file_location("base_mannequin_v2", V2_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load v2 generator: {V2_PATH}")
v2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v2)
base = v2.base

# Maintain the same overall scale while improving silhouette and joint placement.
base.TAG = "anime_roblox_base_mannequin_v3"
base.SHOULDER_X = 0.90
base.ELBOW_X = 1.86
base.WRIST_X = 2.92
base.HAND_TIP_X = 3.30
base.HIP_X = 0.33
base.Z_ANKLE = 0.41
base.Z_KNEE = 1.83
base.Z_HIP = 3.24
base.WARNINGS.clear()


def build_materials_v3() -> Dict[str, bpy.types.Material]:
    return {
        "body": base.material("MAT_BlueprintBody", (0.075, 0.245, 0.39, 1.0), 0.88),
        "joint": base.material("MAT_BlueprintJoint", (0.050, 0.165, 0.26, 1.0), 0.91),
        "proxy": base.material("MAT_Proxy", (0.08, 0.42, 0.95, 0.16), 0.75),
        "rig": base.material("MAT_RigGuide", (1.0, 0.13, 0.025, 1.0), 0.38, 0.0, 1.6),
        "ground": base.material("MAT_Ground", (0.018, 0.023, 0.03, 1.0), 0.96),
    }


def neck_v3(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    return v2.rounded_loft(
        "BODY_Neck",
        ((5.10, 0.36, 0.29), (5.20, 0.33, 0.27),
         (5.34, 0.30, 0.25), (5.46, 0.31, 0.26)),
        col, mat, points=16, exponent_x=0.88, exponent_y=0.92,
    )


def hand_v3(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    parts: List[bpy.types.Object] = []

    parts.append(base.box(
        f"TMP_Palm_{side}",
        (sign * (wrist + 0.17), -0.005, 4.98),
        (0.34, 0.285, 0.18), col, mat, 0.055,
    ))

    offsets = (-0.105, -0.035, 0.035, 0.105)
    lengths = (0.205, 0.255, 0.238, 0.19)
    for index, (y, length) in enumerate(zip(offsets, lengths), 1):
        root = wrist + 0.29
        middle = root + length * 0.52
        tip = root + length
        parts.append(base.capsule(
            f"TMP_Finger{index}A_{side}",
            (sign * root, y, 4.99), (sign * middle, y, 4.99),
            0.034, 0.029, col, mat, 16,
        ))
        parts.append(base.capsule(
            f"TMP_Finger{index}B_{side}",
            (sign * middle, y, 4.99), (sign * tip, y, 4.99),
            0.029, 0.023, col, mat, 16,
        ))

    parts.append(base.sphere(
        f"TMP_ThumbRoot_{side}",
        (sign * (wrist + 0.105), -0.125, 4.94),
        (0.052, 0.050, 0.050), col, mat, 18, 12,
    ))
    parts.append(base.capsule(
        f"TMP_ThumbA_{side}",
        (sign * (wrist + 0.13), -0.14, 4.94),
        (sign * (wrist + 0.25), -0.22, 4.89),
        0.038, 0.031, col, mat, 16,
    ))
    parts.append(base.capsule(
        f"TMP_ThumbB_{side}",
        (sign * (wrist + 0.25), -0.22, 4.89),
        (sign * (wrist + 0.36), -0.27, 4.86),
        0.031, 0.025, col, mat, 16,
    ))
    return base.join_meshes(parts, f"BODY_Hand_{side}", col, mat)


def foot_v3(side: str, col: bpy.types.Collection, mat: bpy.types.Material):
    sign = -1.0 if side == "L" else 1.0

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=40, ring_count=26,
        location=(sign * base.HIP_X, -0.235, 0.18),
    )
    foot = bpy.context.object
    foot.scale = (0.205, 0.355, 0.155)
    base.apply_rotation_scale(foot)
    for vertex in foot.data.vertices:
        co = vertex.co
        if co.z < -0.125:
            co.z = -0.125
        front = max(0.0, min(1.0, (-co.y + 0.04) / 0.36))
        co.x *= 0.91 + 0.10 * front
        if co.y > 0.12:
            co.x *= 0.92
        if co.y < -0.10:
            co.z *= 0.86
    foot = base.finish(foot, f"BODY_Foot_{side}", col, mat, subdivision=1)

    toe_parts: List[bpy.types.Object] = []
    toe_specs = (
        (-0.075, -0.535, 0.13, 0.090, 0.120, 0.075),
        (0.000, -0.570, 0.125, 0.083, 0.110, 0.069),
        (0.075, -0.545, 0.118, 0.072, 0.095, 0.060),
    )
    for index, (xoff, y, z, sx, sy, sz) in enumerate(toe_specs, 1):
        toe_parts.append(base.sphere(
            f"TMP_Toe{index}_{side}",
            (sign * (base.HIP_X + xoff), y, z),
            (sx, sy, sz), col, mat, 22, 14,
        ))
    toes = base.join_meshes(toe_parts, f"BODY_Toes_{side}", col, mat)
    return foot, toes


def build_body_v3(cols, mats):
    body_col, head_col = cols["01_BODY"], cols["02_HEAD"]
    body_mat, joint_mat = mats["body"], mats["joint"]
    objects: List[bpy.types.Object] = []
    weights: Dict[str, str] = {}

    head = v2.head_v2(head_col, body_mat)
    objects.append(head); weights[head.name] = "Head"
    for side, sign in (("L", -1.0), ("R", 1.0)):
        ear = base.sphere(
            f"HEAD_Ear_{side}", (sign * 0.365, -0.005, 5.86),
            (0.066, 0.038, 0.112), head_col, body_mat, 24, 16,
        )
        objects.append(ear); weights[ear.name] = "Head"

    neck = neck_v3(body_col, joint_mat)
    objects.append(neck); weights[neck.name] = "Neck"

    upper = v2.rounded_loft(
        "BODY_UpperTorso",
        ((4.18, 1.08, 0.60), (4.38, 1.16, 0.65),
         (4.62, 1.36, 0.72), (4.86, 1.54, 0.78),
         (5.07, 1.62, 0.77), (5.17, 1.56, 0.72)),
        body_col, body_mat, points=18, exponent_x=0.84, exponent_y=0.90,
    )
    lower = v2.rounded_loft(
        "BODY_LowerTorso",
        ((3.70, 0.98, 0.55), (3.86, 0.91, 0.51),
         (4.02, 0.89, 0.50), (4.20, 0.94, 0.53)),
        body_col, body_mat, points=16, exponent_x=0.86, exponent_y=0.92,
    )
    pelvis = v2.rounded_loft(
        "BODY_Pelvis",
        ((3.18, 0.94, 0.61), (3.33, 1.05, 0.65),
         (3.49, 1.13, 0.64), (3.63, 1.08, 0.59),
         (3.74, 1.00, 0.54)),
        body_col, body_mat, points=18, exponent_x=0.84, exponent_y=0.88,
    )
    for obj, bone in ((upper, "Chest"), (lower, "Spine_01"), (pelvis, "Pelvis")):
        objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        shoulder = base.sphere(
            f"BODY_ShoulderGuide_{side}", (sign * 0.89, 0, 4.98),
            (0.205, 0.225, 0.225), body_col, joint_mat, 32, 20,
        )
        upper_arm = base.capsule(
            f"BODY_UpperArm_{side}", (sign * 0.88, 0, 4.98),
            (sign * base.ELBOW_X, 0, 4.98),
            0.205, 0.158, body_col, body_mat, 40,
        )
        lower_arm = base.capsule(
            f"BODY_LowerArm_{side}", (sign * (base.ELBOW_X - 0.035), 0, 4.98),
            (sign * (base.WRIST_X + 0.015), 0, 4.98),
            0.158, 0.112, body_col, body_mat, 40,
        )
        elbow = base.sphere(
            f"BODY_ElbowGuide_{side}", (sign * base.ELBOW_X, 0, 4.98),
            (0.145, 0.14, 0.14), body_col, joint_mat, 28, 18,
        )
        hand = hand_v3(side, body_col, body_mat)
        for obj, bone in (
            (shoulder, f"UpperArm_{side}"), (upper_arm, f"UpperArm_{side}"),
            (lower_arm, f"LowerArm_{side}"), (elbow, f"LowerArm_{side}"),
            (hand, f"Hand_{side}"),
        ):
            objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        hip = base.sphere(
            f"BODY_HipGuide_{side}", (sign * base.HIP_X, 0, 3.22),
            (0.175, 0.195, 0.19), body_col, joint_mat, 28, 18,
        )
        upper_leg = base.capsule(
            f"BODY_UpperLeg_{side}", (sign * base.HIP_X, 0, 3.20),
            (sign * base.HIP_X, -0.01, base.Z_KNEE),
            0.235, 0.178, body_col, body_mat, 40,
        )
        lower_leg = base.capsule(
            f"BODY_LowerLeg_{side}", (sign * base.HIP_X, -0.01, base.Z_KNEE + 0.025),
            (sign * base.HIP_X, 0, base.Z_ANKLE),
            0.178, 0.115, body_col, body_mat, 40,
        )
        knee = base.sphere(
            f"BODY_KneeGuide_{side}", (sign * base.HIP_X, -0.012, base.Z_KNEE),
            (0.145, 0.14, 0.14), body_col, joint_mat, 28, 18,
        )
        foot, toes = foot_v3(side, body_col, body_mat)
        for obj, bone in (
            (hip, f"UpperLeg_{side}"), (upper_leg, f"UpperLeg_{side}"),
            (lower_leg, f"LowerLeg_{side}"), (knee, f"LowerLeg_{side}"),
            (foot, f"Foot_{side}"), (toes, f"Toe_{side}"),
        ):
            objects.append(obj); weights[obj.name] = bone

    return objects, weights


def presentation_v3(cols, mats, rig):
    cameras, guides = v2.presentation_v2(cols, mats, rig)
    cameras["front"].data.ortho_scale = 7.72
    cameras["back"].data.ortho_scale = 7.72
    cameras["side"].data.ortho_scale = 7.72
    cameras["threequarter"].data.ortho_scale = 7.72
    cameras["side"].location = (11.5, -0.75, 3.18)
    base.point_at(cameras["side"], (0, -0.05, 3.18))
    return cameras, guides


def main_v3() -> None:
    base.log("Starting v3 blank anime Roblox base mannequin generation.")
    base.OUT.mkdir(parents=True, exist_ok=True)
    v2.clean_previous_v2()
    cols = {name: base.collection(name) for name in base.COLLECTIONS}
    mats = build_materials_v3()

    base.log("Building refined neutral body geometry.")
    body, weights = build_body_v3(cols, mats)
    base.log("Building humanoid armature and IK controls.")
    rig = base.build_rig(cols["00_RIG"])
    base.log("Applying stable modular skinning.")
    base.skin(body, rig, weights)
    base.log("Creating Roblox attachment references and root proxy.")
    base.build_attachments(cols["08_ROBLOX_ATTACHMENTS"], rig, mats["proxy"])
    base.log("Creating T-pose and A-pose actions.")
    base.create_actions(rig)
    base.log("Creating LOD1 body copy.")
    lod = base.build_lod(body, cols["13_LOD"])
    base.link(rig, cols["12_EXPORT"])
    for obj in body:
        base.link(obj, cols["12_EXPORT"])

    base.log("Creating v3 neutral presentation scene.")
    cameras, guides = presentation_v3(cols, mats, rig)
    v2.hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    try:
        base.log("Rendering v3 preview images.")
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
    base.log("V3 generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main_v3()
    except Exception:
        traceback.print_exc()
        raise
