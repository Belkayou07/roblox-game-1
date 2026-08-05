"""Second-generation blank anime Roblox mannequin.

This file extends the stable v1 generator while correcting the first rendered
prototype: smoother anatomy, connected joints, shorter arms, readable hands and
feet, stronger blueprint colors, clean framing, hidden startup objects, and a
visible rig-overlay render.
"""
from __future__ import annotations

import importlib.util
import math
import traceback
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import bpy
from mathutils import Vector

BASE_PATH = Path(__file__).with_name("create_anime_roblox_base_mannequin.py")
SPEC = importlib.util.spec_from_file_location("base_mannequin_v1", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load base generator: {BASE_PATH}")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)

# Revised production constants. Total body height remains about 6.3 studs.
base.TAG = "anime_roblox_base_mannequin_v2"
base.SHOULDER_X = 0.86
base.ELBOW_X = 1.82
base.WRIST_X = 2.72
base.HAND_TIP_X = 3.17
base.HIP_X = 0.34
base.Z_ANKLE = 0.39
base.Z_KNEE = 1.82
base.Z_HIP = 3.30
base.WARNINGS.clear()

GENERATOR_PREFIX = "anime_roblox_base_mannequin_"
STARTED_FROM_UNSAVED_FILE = not bool(bpy.data.filepath)


def clean_previous_v2() -> None:
    """Remove only prior mannequin-generator data, including the v1 prototype."""
    base.object_mode()
    for obj in list(bpy.data.objects):
        if str(obj.get("generated_by", "")).startswith(GENERATOR_PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        if str(action.get("generated_by", "")).startswith(GENERATOR_PREFIX):
            bpy.data.actions.remove(action)
    for material in list(bpy.data.materials):
        if str(material.get("generated_by", "")).startswith(GENERATOR_PREFIX):
            bpy.data.materials.remove(material)
    for mesh in list(bpy.data.meshes):
        if str(mesh.get("generated_by", "")).startswith(GENERATOR_PREFIX) and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    for col in list(bpy.data.collections):
        if str(col.get("generated_by", "")).startswith(GENERATOR_PREFIX) and not col.objects and not col.children:
            bpy.data.collections.remove(col)


def build_materials_v2() -> Dict[str, bpy.types.Material]:
    """Use darker linear RGB values so the blueprint stays blue under studio lights."""
    return {
        "body": base.material("MAT_BlueprintBody", (0.075, 0.235, 0.36, 1.0), 0.88),
        "joint": base.material("MAT_BlueprintJoint", (0.045, 0.145, 0.22, 1.0), 0.91),
        "proxy": base.material("MAT_Proxy", (0.08, 0.42, 0.95, 0.16), 0.75),
        "rig": base.material("MAT_RigGuide", (1.0, 0.13, 0.025, 1.0), 0.38, 0.0, 1.6),
        "ground": base.material("MAT_Ground", (0.018, 0.023, 0.03, 1.0), 0.96),
    }


def rounded_loft(
    name: str,
    levels: Sequence[Tuple[float, float, float]],
    col: bpy.types.Collection,
    mat: bpy.types.Material,
    points: int = 16,
    exponent_x: float = 0.86,
    exponent_y: float = 0.90,
) -> bpy.types.Object:
    """Create a smooth stylized torso volume without the old eight-sided wedge look."""
    verts: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    for z, width, depth in levels:
        for index in range(points):
            angle = math.tau * index / points
            cx, sy = math.cos(angle), math.sin(angle)
            x = math.copysign(abs(cx) ** exponent_x, cx) * width * 0.5
            y = math.copysign(abs(sy) ** exponent_y, sy) * depth * 0.5
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
    return base.finish(obj, name, col, mat, bevel_width=0.022, subdivision=0)


def head_v2(col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=48,
        ring_count=32,
        location=(0, -0.012, base.Z_HEAD_CENTER),
    )
    obj = bpy.context.object
    obj.scale = (0.385, 0.405, 0.485)
    base.apply_rotation_scale(obj)
    for vertex in obj.data.vertices:
        co = vertex.co
        normalized_z = co.z / 0.485
        if normalized_z < 0.08:
            jaw_factor = 0.68 + 0.28 * ((normalized_z + 1.0) / 1.08)
            co.x *= jaw_factor
            co.y *= 0.92 + 0.08 * jaw_factor
        if normalized_z < -0.70:
            co.x *= 0.80
            co.y *= 0.92
        if co.y < -0.04:
            co.y *= 0.91
        if normalized_z > 0.46:
            co.x *= 1.035
            co.y *= 1.025
    return base.finish(obj, "HEAD_Base", col, mat, subdivision=1)


def hand_v2(side: str, col: bpy.types.Collection, mat: bpy.types.Material) -> bpy.types.Object:
    sign = -1.0 if side == "L" else 1.0
    wrist = base.WRIST_X
    parts: List[bpy.types.Object] = []
    parts.append(base.box(
        f"TMP_Palm_{side}",
        (sign * (wrist + 0.17), -0.005, 4.98),
        (0.34, 0.31, 0.18), col, mat, 0.07,
    ))
    finger_offsets = (-0.112, -0.038, 0.038, 0.112)
    finger_lengths = (0.185, 0.225, 0.215, 0.175)
    for index, (y, length) in enumerate(zip(finger_offsets, finger_lengths), 1):
        start_x = sign * (wrist + 0.30)
        end_x = sign * (wrist + 0.30 + length)
        parts.append(base.capsule(
            f"TMP_Finger{index}_{side}",
            (start_x, y, 4.985), (end_x, y, 4.985),
            0.038, 0.032, col, mat, 16,
        ))
    parts.append(base.capsule(
        f"TMP_Thumb_{side}",
        (sign * (wrist + 0.12), -0.105, 4.94),
        (sign * (wrist + 0.30), -0.12, 4.79),
        0.047, 0.034, col, mat, 16,
    ))
    return base.join_meshes(parts, f"BODY_Hand_{side}", col, mat)


def foot_v2(side: str, col: bpy.types.Collection, mat: bpy.types.Material):
    sign = -1.0 if side == "L" else 1.0
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=36, ring_count=24,
        location=(sign * base.HIP_X, -0.22, 0.18),
    )
    foot = bpy.context.object
    foot.scale = (0.225, 0.37, 0.17)
    base.apply_rotation_scale(foot)
    for vertex in foot.data.vertices:
        co = vertex.co
        if co.z < -0.135:
            co.z = -0.135
        front = max(0.0, min(1.0, (-co.y + 0.02) / 0.37))
        co.x *= 0.95 + 0.11 * front
        if co.y < -0.10:
            co.z *= 0.88
    foot = base.finish(foot, f"BODY_Foot_{side}", col, mat, subdivision=1)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=28, ring_count=18,
        location=(sign * base.HIP_X, -0.515, 0.145),
    )
    toes = bpy.context.object
    toes.scale = (0.225, 0.16, 0.105)
    base.apply_rotation_scale(toes)
    for vertex in toes.data.vertices:
        if vertex.co.z < -0.085:
            vertex.co.z = -0.085
    toes = base.finish(toes, f"BODY_Toes_{side}", col, mat, subdivision=1)
    return foot, toes


def build_body_v2(cols, mats):
    body_col, head_col = cols["01_BODY"], cols["02_HEAD"]
    body_mat, joint_mat = mats["body"], mats["joint"]
    objects: List[bpy.types.Object] = []
    weights: Dict[str, str] = {}

    head = head_v2(head_col, body_mat)
    objects.append(head); weights[head.name] = "Head"
    for side, sign in (("L", -1.0), ("R", 1.0)):
        ear = base.sphere(
            f"HEAD_Ear_{side}", (sign * 0.365, -0.005, 5.86),
            (0.068, 0.037, 0.115), head_col, body_mat, 24, 16,
        )
        objects.append(ear); weights[ear.name] = "Head"

    neck = base.capsule(
        "BODY_Neck", (0, 0, 5.08), (0, 0, 5.44),
        0.175, 0.155, body_col, joint_mat, 32,
    )
    objects.append(neck); weights[neck.name] = "Neck"

    upper = rounded_loft(
        "BODY_UpperTorso",
        ((4.22, 0.98, 0.46), (4.43, 1.10, 0.49), (4.66, 1.34, 0.54),
         (4.88, 1.50, 0.57), (5.08, 1.62, 0.55)),
        body_col, body_mat,
    )
    lower = rounded_loft(
        "BODY_LowerTorso",
        ((3.72, 1.00, 0.48), (3.92, 0.91, 0.44), (4.12, 0.93, 0.44),
         (4.30, 1.01, 0.47)),
        body_col, body_mat,
    )
    pelvis = rounded_loft(
        "BODY_Pelvis",
        ((3.22, 0.92, 0.50), (3.39, 1.04, 0.55), (3.58, 1.10, 0.57),
         (3.75, 1.03, 0.50), (3.84, 0.98, 0.47)),
        body_col, body_mat,
    )
    for obj, bone in ((upper, "Chest"), (lower, "Spine_01"), (pelvis, "Pelvis")):
        objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        shoulder = base.sphere(
            f"BODY_ShoulderGuide_{side}", (sign * 0.83, 0, 4.98),
            (0.265, 0.255, 0.26), body_col, joint_mat, 32, 20,
        )
        upper_arm = base.capsule(
            f"BODY_UpperArm_{side}", (sign * 0.78, 0, 4.98),
            (sign * base.ELBOW_X, 0, 4.98), 0.235, 0.19, body_col, body_mat, 40,
        )
        lower_arm = base.capsule(
            f"BODY_LowerArm_{side}", (sign * (base.ELBOW_X - 0.055), 0, 4.98),
            (sign * (base.WRIST_X + 0.02), 0, 4.98), 0.19, 0.14, body_col, body_mat, 40,
        )
        elbow = base.sphere(
            f"BODY_ElbowGuide_{side}", (sign * base.ELBOW_X, 0, 4.98),
            (0.195, 0.185, 0.185), body_col, joint_mat, 32, 20,
        )
        hand = hand_v2(side, body_col, body_mat)
        for obj, bone in (
            (shoulder, f"UpperArm_{side}"), (upper_arm, f"UpperArm_{side}"),
            (lower_arm, f"LowerArm_{side}"), (elbow, f"LowerArm_{side}"),
            (hand, f"Hand_{side}"),
        ):
            objects.append(obj); weights[obj.name] = bone

    for side, sign in (("L", -1.0), ("R", 1.0)):
        hip = base.sphere(
            f"BODY_HipGuide_{side}", (sign * base.HIP_X, 0, 3.32),
            (0.295, 0.285, 0.30), body_col, joint_mat, 32, 20,
        )
        upper_leg = base.capsule(
            f"BODY_UpperLeg_{side}", (sign * base.HIP_X, 0, 3.36),
            (sign * base.HIP_X, 0, base.Z_KNEE), 0.295, 0.225, body_col, body_mat, 40,
        )
        lower_leg = base.capsule(
            f"BODY_LowerLeg_{side}", (sign * base.HIP_X, 0, base.Z_KNEE + 0.045),
            (sign * base.HIP_X, 0, base.Z_ANKLE), 0.22, 0.155, body_col, body_mat, 40,
        )
        knee = base.sphere(
            f"BODY_KneeGuide_{side}", (sign * base.HIP_X, -0.018, base.Z_KNEE),
            (0.225, 0.21, 0.21), body_col, joint_mat, 32, 20,
        )
        foot, toes = foot_v2(side, body_col, body_mat)
        for obj, bone in (
            (hip, f"UpperLeg_{side}"), (upper_leg, f"UpperLeg_{side}"),
            (lower_leg, f"LowerLeg_{side}"), (knee, f"LowerLeg_{side}"),
            (foot, f"Foot_{side}"), (toes, f"Toe_{side}"),
        ):
            objects.append(obj); weights[obj.name] = bone

    return objects, weights


def rig_guides_v2(rig, col, mat):
    guides = []
    front_offset = Vector((0.0, -0.40, 0.0))
    for bone in rig.data.bones:
        if not bone.use_deform:
            continue
        start = rig.matrix_world @ bone.head_local + front_offset
        end = rig.matrix_world @ bone.tail_local + front_offset
        guide = base.capsule(
            f"PREVIEW_Bone_{bone.name}", start, end,
            0.052, 0.036, col, mat, 14,
        )
        joint = base.sphere(
            f"PREVIEW_Joint_{bone.name}", start,
            (0.085, 0.085, 0.085), col, mat, 16, 10,
        )
        guide.hide_render = True
        joint.hide_render = True
        guides.extend((guide, joint))
    return guides


def presentation_v2(cols, mats, rig):
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
        scene.view_settings.exposure = -0.35
    except (TypeError, AttributeError):
        pass
    if scene.world is None:
        scene.world = bpy.data.worlds.new("BaseMannequinWorld")
        base.mark(scene.world)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    if background:
        background.inputs["Color"].default_value = (0.009, 0.013, 0.019, 1.0)
        background.inputs["Strength"].default_value = 0.26

    ground = base.box(
        "PREVIEW_Ground", (0, 0, -0.055), (8.5, 8.5, 0.08),
        cols["09_PREVIEW_GUIDES"], mats["ground"], 0.025,
    )
    ground.hide_select = True
    base.light("LIGHT_Key", (-4.2, -5.0, 7.2), 520, 4.2, cols["11_LIGHTING"])
    base.light("LIGHT_Fill", (4.0, -2.2, 5.0), 190, 3.8, cols["11_LIGHTING"])
    base.light("LIGHT_Rim", (0, 4.2, 6.6), 390, 3.2, cols["11_LIGHTING"])

    cameras = {
        "front": base.camera("CAM_Front", (0, -11.5, 3.18), (0, 0, 3.18), cols["10_CAMERAS"]),
        "side": base.camera("CAM_Side", (11.5, -1.6, 3.18), (0, 0, 3.18), cols["10_CAMERAS"]),
        "back": base.camera("CAM_Back", (0, 11.5, 3.18), (0, 0, 3.18), cols["10_CAMERAS"]),
        "threequarter": base.camera("CAM_ThreeQuarter", (8.1, -8.1, 3.55), (0, 0, 3.18), cols["10_CAMERAS"]),
        "perspective": base.camera("CAM_Perspective", (6.8, -8.6, 4.0), (0, 0, 3.18), cols["10_CAMERAS"], False),
    }
    for name in ("front", "side", "back", "threequarter"):
        cameras[name].data.ortho_scale = 7.55
    return cameras, rig_guides_v2(rig, cols["09_PREVIEW_GUIDES"], mats["rig"])


def hide_startup_objects() -> None:
    if not STARTED_FROM_UNSAVED_FILE:
        return
    for name in ("Cube", "Camera", "Light"):
        obj = bpy.data.objects.get(name)
        if obj and not obj.get("generated_by"):
            obj.hide_render = True
            obj.hide_set(True)


def render_v2(cameras, guides):
    scene = bpy.context.scene
    unrelated_states = {}
    for obj in bpy.data.objects:
        if obj.get("generated_by") != base.TAG:
            unrelated_states[obj.name] = obj.hide_render
            obj.hide_render = True
    try:
        for guide in guides:
            guide.hide_render = True
        for view in ("front", "side", "back", "threequarter"):
            scene.camera = cameras[view]
            scene.render.filepath = str(base.RENDERS[view])
            bpy.ops.render.render(write_still=True)
            base.log(f"Rendered {view}: {base.RENDERS[view]}")
        for guide in guides:
            guide.hide_render = False
        scene.camera = cameras["front"]
        scene.render.filepath = str(base.RENDERS["rig"])
        bpy.ops.render.render(write_still=True)
        base.log(f"Rendered rig overlay: {base.RENDERS['rig']}")
    finally:
        for guide in guides:
            guide.hide_render = True
        for name, state in unrelated_states.items():
            obj = bpy.data.objects.get(name)
            if obj:
                obj.hide_render = state
        hide_startup_objects()


def main_v2() -> None:
    base.log("Starting improved blank anime Roblox base mannequin generation.")
    base.OUT.mkdir(parents=True, exist_ok=True)
    clean_previous_v2()
    cols = {name: base.collection(name) for name in base.COLLECTIONS}
    mats = build_materials_v2()

    base.log("Building smoother connected blank body geometry.")
    body, weights = build_body_v2(cols, mats)
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

    base.log("Creating corrected neutral presentation scene.")
    cameras, guides = presentation_v2(cols, mats, rig)
    hide_startup_objects()
    base.log("Saving Blender source file.")
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    try:
        base.log("Rendering corrected preview images.")
        render_v2(cameras, guides)
    except Exception as exc:
        base.warn(f"Preview rendering did not complete: {exc}")
        traceback.print_exc()
    try:
        base.log("Exporting Roblox-oriented FBX.")
        base.export_fbx(rig, body)
    except Exception as exc:
        base.warn(f"FBX export did not complete: {exc}")
        traceback.print_exc()
    hide_startup_objects()
    bpy.ops.wm.save_as_mainfile(filepath=str(base.BLEND))
    base.validation(rig, body, lod)
    base.log("Improved generation complete. The saved rest state is the T-pose.")


if __name__ == "__main__":
    try:
        main_v2()
    except Exception:
        traceback.print_exc()
        raise
