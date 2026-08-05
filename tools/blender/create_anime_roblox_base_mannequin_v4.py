"""Fourth-generation blank anime Roblox mannequin.

V4 keeps the reliable v3 Blender/FBX pipeline but changes the visible body
construction so the mannequin reads as a clean character basemesh rather than
an assembly of exposed primitive joints. It remains bald, unclothed, neutral,
and reusable for many derived Roblox characters.
"""
from __future__ import annotations

import importlib.util
import math
import traceback
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import bpy

V3_PATH = Path(__file__).with_name("create_anime_roblox_base_mannequin_v3.py")
SPEC = importlib.util.spec_from_file_location("base_mannequin_v3", V3_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load v3 generator: {V3_PATH}")
v3 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v3)
v2 = v3.v2
base = v3.base

base.TAG = "anime_roblox_base_mannequin_v4"
base.SHOULDER_X = 0.92
base.ELBOW_X = 1.88
base.WRIST_X = 2.88
base.HAND_TIP_X = 3.30
base.HIP_X = 0.34
base.Z_ANKLE = 0.43
base.Z_KNEE = 1.84
base.Z_HIP = 3.23
base.WARNINGS.clear()


def build_materials_v4() -> Dict[str, bpy.types.Material]:
    body = base.material("MAT_BlueprintBody", (0.070, 0.255, 0.405, 1.0), 0.90)
    return {
        "body": body,
        # Using one visual material prevents joints from reading as toy sockets.
        "joint": body,
        "proxy": base.material("MAT_Proxy", (0.08, 0.42, 0.95, 0.16), 0.75),
        "rig": base.material("MAT_RigGuide", (1.0, 0.13, 0.025, 1.0), 0.38, 0.0, 1.6),
        "ground": base.material("MAT_Ground", (0.018, 0.023, 0.030, 1.0), 0.96),
    }


def ellipsoid(
    name: str,
    location: Sequence[float],
    scale: Sequence[float],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    segments: int = 36,
    rings: int = 24,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        location=location,
    )
    obj = bpy.context.object
    obj.scale = scale
    return base.finish(obj, name, col, mat, subdivision=1)


def neck_v4(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    # Wider at both ends so it sinks naturally into the chest and skull.
    return v2.rounded_loft(
        "BODY_Neck",
        (
            (5.08, 0.44, 0.34),
            (5.17, 0.37, 0.30),
            (5.31, 0.31, 0.27),
            (5.44, 0.33, 0.28),
            (5.50, 0.38, 0.31),
        ),
        col,
        mat,
        points=18,
        exponent_x=0.90,
        exponent_y=0.94,
    )


def palm_v4(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=36,
        ring_count=24,
        location=(sign * (wrist + 0.18), -0.003, 4.98),
    )
    palm = bpy.context.object
    palm.scale = (0.205, 0.145, 0.100)
    base.apply_rotation_scale(palm)
    for vertex in palm.data.vertices:
        co = vertex.co
        local_x = sign * co.x
        # Narrow the fingertip side and slightly flatten the palm faces.
        if local_x > 0.02:
            co.y *= 0.92
            co.z *= 0.92
        if local_x < -0.10:
            co.y *= 0.86
        co.z *= 0.92
    return base.finish(palm, f"TMP_Palm_{side}", col, mat, subdivision=1)


def hand_v4(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    parts: List[bpy.types.Object] = [palm_v4(side, col, mat)]

    offsets = (-0.102, -0.034, 0.034, 0.102)
    lengths = (0.205, 0.270, 0.250, 0.195)
    z_offsets = (0.004, 0.010, 0.006, -0.003)
    for index, (y, length, zoff) in enumerate(zip(offsets, lengths, z_offsets), 1):
        root = wrist + 0.31
        first = root + length * 0.38
        second = root + length * 0.72
        tip = root + length
        radii = (0.032, 0.028, 0.023, 0.018)
        points = (root, first, second, tip)
        for segment in range(3):
            parts.append(base.capsule(
                f"TMP_Finger{index}_{segment + 1}_{side}",
                (sign * points[segment], y, 4.985 + zoff),
                (sign * points[segment + 1], y, 4.985 + zoff),
                radii[segment], radii[segment + 1], col, mat, 16,
            ))

    parts.append(ellipsoid(
        f"TMP_ThumbPad_{side}",
        (sign * (wrist + 0.09), -0.115, 4.94),
        (0.075, 0.065, 0.060), col, mat, 20, 14,
    ))
    parts.append(base.capsule(
        f"TMP_ThumbA_{side}",
        (sign * (wrist + 0.12), -0.13, 4.94),
        (sign * (wrist + 0.24), -0.21, 4.90),
        0.040, 0.033, col, mat, 16,
    ))
    parts.append(base.capsule(
        f"TMP_ThumbB_{side}",
        (sign * (wrist + 0.24), -0.21, 4.90),
        (sign * (wrist + 0.35), -0.26, 4.87),
        0.033, 0.025, col, mat, 16,
    ))
    return base.join_meshes(parts, f"BODY_Hand_{side}", col, mat)


def foot_shell_v4(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=44,
        ring_count=28,
        location=(sign * base.HIP_X, -0.28, 0.205),
    )
    foot = bpy.context.object
    foot.scale = (0.195, 0.405, 0.155)
    base.apply_rotation_scale(foot)
    for vertex in foot.data.vertices:
        co = vertex.co
        if co.z < -0.122:
            co.z = -0.122
        front = max(0.0, min(1.0, (-co.y + 0.02) / 0.40))
        heel = max(0.0, min(1.0, (co.y + 0.02) / 0.35))
        co.x *= 0.88 + 0.17 * front - 0.05 * heel
        if co.y < -0.12:
            co.z *= 0.80
        if co.y > 0.16:
            co.z *= 1.05
    return base.finish(foot, f"BODY_Foot_{side}", col, mat, subdivision=1)


def toes_v4(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    parts: List[bpy.types.Object] = []
    specs: Tuple[Tuple[float, float, float, float], ...] = (
        (-0.078, 0.100, 0.125, 0.078),
        (-0.025, 0.082, 0.112, 0.069),
        (0.030, 0.075, 0.102, 0.063),
        (0.080, 0.065, 0.090, 0.055),
    )
    for index, (xoff, sx, sy, sz) in enumerate(specs, 1):
        parts.append(ellipsoid(
            f"TMP_Toe{index}_{side}",
            (sign * (base.HIP_X + xoff), -0.615 + index * 0.006, 0.125 - index * 0.004),
            (sx, sy, sz), col, mat, 22, 14,
        ))
    return base.join_meshes(parts, f"BODY_Toes_{side}", col, mat)


def build_body_v4(cols, mats):
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

    neck = neck_v4(body_col, body_mat)
    objects.append(neck)
    weights[neck.name] = "Neck"

    upper = v2.rounded_loft(
        "BODY_UpperTorso",
        (
            (4.15, 1.04, 0.64),
            (4.34, 1.12, 0.69),
            (4.57, 1.34, 0.77),
            (4.80, 1.54, 0.84),
            (5.02, 1.72, 0.86),
            (5.18, 1.66, 0.80),
            (5.25, 1.42, 0.72),
        ),
        body_col, body_mat,
        points=20, exponent_x=0.86, exponent_y=0.92,
    )
    lower = v2.rounded_loft(
        "BODY_LowerTorso",
        (
            (3.68, 0.98, 0.59),
            (3.84, 0.91, 0.55),
            (4.00, 0.89, 0.54),
            (4.17, 0.95, 0.58),
        ),
        body_col, body_mat,
        points=18, exponent_x=0.88, exponent_y=0.94,
    )
    pelvis = v2.rounded_loft(
        "BODY_Pelvis",
        (
            (3.12, 0.96, 0.66),
            (3.25, 1.12, 0.72),
            (3.42, 1.20, 0.72),
            (3.58, 1.13, 0.66),
            (3.72, 1.00, 0.58),
        ),
        body_col, body_mat,
        points=20, exponent_x=0.86, exponent_y=0.90,
    )
    for obj, bone in ((upper, "Chest"), (lower, "Spine_01"), (pelvis, "Pelvis")):
        objects.append(obj)
        weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        # Chest-to-arm bridge replaces the exposed spherical shoulder socket.
        shoulder_blend = base.capsule(
            f"BODY_ShoulderBlend_{side}",
            (sign * 0.68, 0.0, 5.02),
            (sign * 1.02, 0.0, 4.98),
            0.285, 0.205, body_col, body_mat, 40,
        )
        upper_arm = base.capsule(
            f"BODY_UpperArm_{side}",
            (sign * 0.96, 0.0, 4.98),
            (sign * (base.ELBOW_X + 0.04), 0.0, 4.98),
            0.205, 0.155, body_col, body_mat, 40,
        )
        lower_arm = base.capsule(
            f"BODY_LowerArm_{side}",
            (sign * (base.ELBOW_X - 0.06), 0.0, 4.98),
            (sign * (base.WRIST_X + 0.03), 0.0, 4.98),
            0.165, 0.112, body_col, body_mat, 40,
        )
        elbow_cap = ellipsoid(
            f"BODY_ElbowGuide_{side}",
            (sign * base.ELBOW_X, -0.025, 4.98),
            (0.125, 0.145, 0.135), body_col, body_mat, 28, 18,
        )
        wrist_blend = base.capsule(
            f"BODY_WristBlend_{side}",
            (sign * (base.WRIST_X - 0.08), 0.0, 4.98),
            (sign * (base.WRIST_X + 0.10), 0.0, 4.98),
            0.115, 0.100, body_col, body_mat, 24,
        )
        hand = hand_v4(side, body_col, body_mat)
        for obj, bone in (
            (shoulder_blend, f"UpperArm_{side}"),
            (upper_arm, f"UpperArm_{side}"),
            (lower_arm, f"LowerArm_{side}"),
            (elbow_cap, f"LowerArm_{side}"),
            (wrist_blend, f"Hand_{side}"),
            (hand, f"Hand_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        # Pelvis-to-leg bridge hides the old cut hip seam.
        hip_blend = base.capsule(
            f"BODY_HipBlend_{side}",
            (sign * 0.31, 0.0, 3.34),
            (sign * base.HIP_X, -0.005, 3.08),
            0.245, 0.225, body_col, body_mat, 36,
        )
        upper_leg = base.capsule(
            f"BODY_UpperLeg_{side}",
            (sign * base.HIP_X, -0.005, 3.20),
            (sign * base.HIP_X, -0.015, base.Z_KNEE + 0.06),
            0.235, 0.175, body_col, body_mat, 40,
        )
        lower_leg = base.capsule(
            f"BODY_LowerLeg_{side}",
            (sign * base.HIP_X, -0.015, base.Z_KNEE - 0.055),
            (sign * base.HIP_X, 0.0, base.Z_ANKLE - 0.01),
            0.182, 0.115, body_col, body_mat, 40,
        )
        knee_cap = ellipsoid(
            f"BODY_KneeGuide_{side}",
            (sign * base.HIP_X, -0.070, base.Z_KNEE),
            (0.145, 0.115, 0.150), body_col, body_mat, 28, 18,
        )
        ankle_blend = base.capsule(
            f"BODY_AnkleBlend_{side}",
            (sign * base.HIP_X, 0.0, 0.50),
            (sign * base.HIP_X, -0.08, 0.28),
            0.115, 0.145, body_col, body_mat, 28,
        )
        foot = foot_shell_v4(side, body_col, body_mat)
        toes = toes_v4(side, body_col, body_mat)
        for obj, bone in (
            (hip_blend, f"UpperLeg_{side}"),
            (upper_leg, f"UpperLeg_{side}"),
            (lower_leg, f"LowerLeg_{side}"),
            (knee_cap, f"LowerLeg_{side}"),
            (ankle_blend, f"Foot_{side}"),
            (foot, f"Foot_{side}"),
            (toes, f"Toe_{side}"),
        ):
            objects.append(obj)
            weights[obj.name] = bone

    return objects, weights


def presentation_v4(cols, mats, rig):
    cameras, guides = v2.presentation_v2(cols, mats, rig)
    for name in ("front", "back", "side", "threequarter"):
        cameras[name].data.ortho_scale = 7.78
    cameras["side"].location = (11.5, -0.22, 3.18)
    base.point_at(cameras["side"], (0.0, -0.03, 3.18))
    cameras["threequarter"].location = (7.6, -8.8, 3.55)
    base.point_at(cameras["threequarter"], (0.0, -0.04, 3.18))
    return cameras, guides


def main_v4() -> None:
    base.log("Starting v4 blank anime Roblox base mannequin generation.")
    base.OUT.mkdir(parents=True, exist_ok=True)
    v2.clean_previous_v2()
    cols = {name: base.collection(name) for name in base.COLLECTIONS}
    mats = build_materials_v4()

    base.log("Building continuous-looking modular body geometry.")
    body, weights = build_body_v4(cols, mats)
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

    base.log("Creating v4 presentation scene.")
    cameras, guides = presentation_v4(cols, mats, rig)
    v2.hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    try:
        base.log("Rendering v4 preview images.")
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
    base.log("V4 generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main_v4()
    except Exception:
        traceback.print_exc()
        raise
