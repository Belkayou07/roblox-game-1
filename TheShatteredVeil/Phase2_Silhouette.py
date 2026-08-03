from __future__ import annotations

import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

OUT_ROOT = Path(os.environ.get("SHATTERED_VEIL_OUTPUT", Path.cwd() / "TheShatteredVeil"))
PROGRESS = OUT_ROOT / "Progress"


def clean():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def mat(name, color, rough=0.7, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = emit
        p.inputs["Emission Strength"].default_value = emit_strength
    return m


def smooth(obj):
    if hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = True
        sub = obj.modifiers.new("Subd", "SUBSURF")
        sub.levels = 1
        sub.render_levels = 1
    return obj


def cube(name, loc, scale, rot=(0, 0, 0), material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        b = o.modifiers.new("Bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
    smooth(o)
    if material:
        o.data.materials.append(material)
    return o


def sphere(name, loc, scale, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, segments=20, ring_count=10)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(o)
    if material:
        o.data.materials.append(material)
    return o


def cyl(name, loc, scale, rot=(0, 0, 0), material=None):
    bpy.ops.mesh.primitive_cylinder_add(location=loc, rotation=rot, vertices=18)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(o)
    if material:
        o.data.materials.append(material)
    return o


def curve_piece(name, points, thickness, material=None):
    c = bpy.data.curves.new(name, type="CURVE")
    c.dimensions = "3D"
    spline = c.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, pt in zip(spline.bezier_points, points):
        bp.co = Vector(pt)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    c.bevel_depth = thickness
    c.bevel_resolution = 4
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    if material:
        o.data.materials.append(material)
    return o


def setup_scene():
    s = bpy.context.scene
    s.render.engine = "BLENDER_EEVEE_NEXT"
    s.render.resolution_x = 1200
    s.render.resolution_y = 1400
    s.render.image_settings.file_format = "PNG"
    s.world.color = (0.16, 0.16, 0.18)
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    floor = bpy.context.object
    floor.data.materials.append(mat("Floor", (0.82, 0.82, 0.84, 1), 0.95))

    target = Vector((0, 0, 1.2))
    for name, loc, energy, size in [
        ("Key", (3, -3, 3.5), 4200, 3.0),
        ("Fill", (-2.5, -2.2, 2.6), 1700, 3.0),
        ("Rim", (0, 3, 3.0), 1400, 2.0),
    ]:
        d = bpy.data.lights.new(name, "AREA")
        d.energy = energy
        d.shape = "RECTANGLE"
        d.size = size
        o = bpy.data.objects.new(name, d)
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        q = (target - o.location).to_track_quat("-Z", "Y")
        o.rotation_euler = q.to_euler()


def camera(name, loc, rot, ortho=None):
    d = bpy.data.cameras.new(name)
    if ortho:
        d.type = "ORTHO"
        d.ortho_scale = ortho
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return o


def build_character():
    base = mat("Base", (0.72, 0.72, 0.74, 1), 0.78)
    accent = mat("Accent", (0.52, 0.52, 0.56, 1), 0.82)
    metal = mat("Metal", (0.63, 0.63, 0.67, 1), 0.34, 0.7)
    glow = mat("Glow", (0.62, 0.62, 0.66, 1), 0.5, 0, (0.95, 0.25, 0.28, 1), 0.5)

    cube("Torso", (0, 0, 1.42), (0.24, 0.16, 0.34), material=base, bevel=0.02)
    cube("Pelvis", (0, 0, 0.98), (0.18, 0.12, 0.12), material=base, bevel=0.02)
    cyl("Neck", (0, 0, 1.78), (0.08, 0.08, 0.07), material=base)
    sphere("Head", (0, 0.0, 2.03), (0.13, 0.14, 0.18), material=base)

    for side in (1, -1):
        sphere(f"Shoulder_{side}", (0.34 * side, 0, 1.58), (0.10, 0.10, 0.10), base)
        cyl(f"UpperArm_{side}", (0.54 * side, -0.04, 1.36), (0.07, 0.07, 0.20), (math.radians(104), 0, math.radians(18 * side)), base)
        cyl(f"Forearm_{side}", (0.79 * side, -0.10, 1.12), (0.055, 0.055, 0.18), (math.radians(104), 0, math.radians(10 * side)), base)
        sphere(f"Wrist_{side}", (0.97 * side, -0.14, 0.94), (0.05, 0.05, 0.05), base)
        cube(f"Hand_{side}", (1.08 * side, -0.15, 0.88), (0.05, 0.028, 0.02), (0, math.radians(10 * side), math.radians(8 * side)), base, 0.004)

    for side in (1, -1):
        cyl(f"Thigh_{side}", (0.16 * side, -0.01, 0.72), (0.10, 0.10, 0.22), (0, 0, math.radians(2 * side)), base)
        sphere(f"Knee_{side}", (0.17 * side, -0.01, 0.48), (0.06, 0.055, 0.05), base)
        cyl(f"Shin_{side}", (0.16 * side, 0.0, 0.24), (0.06, 0.06, 0.18), (0, 0, math.radians(1 * side)), base)
        sphere(f"Ankle_{side}", (0.16 * side, 0.01, 0.06), (0.045, 0.04, 0.035), base)
        cube(f"Foot_{side}", (0.16 * side, 0.08, 0.03), (0.09, 0.16, 0.04), (math.radians(3), 0, 0), base, 0.01)

    cube("Blindfold", (0, -0.03, 2.05), (0.16, 0.09, 0.04), material=accent, bevel=0.01)
    cube("Scarf", (0, -0.02, 1.92), (0.15, 0.10, 0.085), (math.radians(6), 0, 0), accent, 0.012)
    cyl("BlindfoldTail_L", (0.24, -0.10, 1.90), (0.012, 0.012, 0.14), (math.radians(110), math.radians(10), math.radians(-18)), base)
    cyl("BlindfoldTail_R", (-0.24, -0.10, 1.89), (0.012, 0.012, 0.13), (math.radians(110), math.radians(-10), math.radians(18)), base)

    sphere("HairCap", (0, 0.02, 2.05), (0.18, 0.19, 0.17), base)
    cyl("HairFront_L", (0.12, -0.10, 1.90), (0.025, 0.025, 0.18), (math.radians(100), math.radians(5), math.radians(-20)), base)
    cyl("HairFront_R", (-0.12, -0.10, 1.91), (0.025, 0.025, 0.18), (math.radians(100), math.radians(-5), math.radians(20)), base)
    cyl("HairSide_L", (0.30, -0.07, 1.84), (0.03, 0.03, 0.22), (math.radians(96), math.radians(-8), math.radians(-30)), accent)
    cyl("HairSide_R", (-0.30, -0.07, 1.84), (0.03, 0.03, 0.22), (math.radians(96), math.radians(8), math.radians(30)), base)
    cyl("HairBack", (0, 0.16, 1.74), (0.10, 0.08, 0.28), (math.radians(5), 0, 0), base)
    curve_piece("HairLock_L", [(0.02, 0.12, 2.05), (0.18, 0.22, 1.86), (0.34, 0.24, 1.55), (0.48, 0.18, 1.24)], 0.018, base)
    curve_piece("HairLock_C", [(0, 0.12, 2.04), (0, 0.30, 1.82), (-0.02, 0.32, 1.48), (-0.02, 0.28, 1.16)], 0.018, accent)
    curve_piece("HairLock_R", [(-0.02, 0.12, 2.05), (-0.18, 0.22, 1.86), (-0.34, 0.24, 1.55), (-0.48, 0.18, 1.24)], 0.018, base)

    cube("InnerWrap", (0, 0.0, 1.40), (0.25, 0.17, 0.31), material=base, bevel=0.015)
    cube("OuterRobe", (0, 0.01, 1.42), (0.31, 0.19, 0.35), material=base, bevel=0.015)
    cube("Sash", (0, -0.01, 1.02), (0.26, 0.12, 0.07), material=accent, bevel=0.008)
    cube("TrouserMass", (0, 0.0, 0.70), (0.27, 0.15, 0.23), material=base, bevel=0.012)
    for name, loc, scale, rot, m in [
        ("ClothFront", (0, -0.14, 0.82), (0.09, 0.016, 0.34), (math.radians(8), 0, 0), base),
        ("ClothBack", (0, 0.16, 0.85), (0.10, 0.016, 0.38), (math.radians(-10), 0, 0), base),
        ("ClothLeft", (0.16, 0.0, 0.84), (0.05, 0.016, 0.42), (math.radians(6), math.radians(10), math.radians(14)), accent),
        ("ClothRight", (-0.16, 0.0, 0.88), (0.05, 0.016, 0.34), (math.radians(7), math.radians(-8), math.radians(-12)), base),
    ]:
        cube(name, loc, scale, rot, m, 0.003)
    cube("ShoulderGuard", (0.42, -0.02, 1.58), (0.10, 0.06, 0.03), (math.radians(15), 0, math.radians(18)), accent, 0.006)
    cube("ForearmGuard", (-0.84, -0.11, 1.10), (0.035, 0.08, 0.025), (math.radians(10), 0, math.radians(-8)), accent, 0.006)
    cyl("LegWrap_L", (0.16, 0.0, 0.20), (0.07, 0.05, 0.06), material=accent)
    cyl("LegWrap_R", (-0.16, 0.0, 0.20), (0.07, 0.05, 0.06), material=accent)
    cube("ShoeWrap_L", (0.16, 0.08, 0.03), (0.10, 0.17, 0.05), (math.radians(3), 0, 0), base, 0.008)
    cube("ShoeWrap_R", (-0.16, 0.08, 0.03), (0.10, 0.17, 0.05), (math.radians(3), 0, 0), base, 0.008)

    curve_piece("BladeLong", [(1.02, -0.20, 0.84), (1.10, -0.40, 0.80), (1.20, -0.62, 0.72), (1.34, -0.86, 0.58)], 0.028, metal)
    curve_piece("BladeLongGlow", [(1.02, -0.20, 0.85), (1.10, -0.40, 0.81), (1.20, -0.62, 0.73), (1.34, -0.86, 0.59)], 0.005, glow)
    cube("HandleLong", (0.96, -0.15, 0.88), (0.022, 0.09, 0.022), (math.radians(90), 0, math.radians(18)), metal, 0.004)
    cube("GuardLong", (0.98, -0.24, 0.88), (0.06, 0.012, 0.04), (math.radians(90), 0, math.radians(18)), metal, 0.004)

    curve_piece("BladeShort", [(-1.00, -0.18, 0.82), (-1.08, -0.34, 0.79), (-1.18, -0.48, 0.70), (-1.28, -0.56, 0.58)], 0.028, metal)
    curve_piece("BladeShortGlow", [(-1.00, -0.18, 0.83), (-1.08, -0.34, 0.80), (-1.18, -0.48, 0.71), (-1.28, -0.56, 0.59)], 0.005, glow)
    cube("HandleShort", (-0.96, -0.15, 0.86), (0.022, 0.08, 0.022), (math.radians(90), 0, math.radians(-18)), metal, 0.004)
    cube("GuardShort", (-0.98, -0.22, 0.86), (0.06, 0.012, 0.04), (math.radians(90), 0, math.radians(-18)), metal, 0.004)


def render_outputs():
    cams = {
        "Silhouette_Front.png": camera("CamFront", (0, -4.5, 1.25), (math.radians(90), 0, 0), 2.25),
        "Silhouette_Side.png": camera("CamSide", (4.3, 0, 1.25), (math.radians(90), 0, math.radians(90)), 2.25),
        "Silhouette_Back.png": camera("CamBack", (0, 4.4, 1.25), (math.radians(90), 0, math.radians(180)), 2.25),
        "Silhouette_ThreeQuarter.png": camera("CamThree", (3.6, -4.0, 1.55), (math.radians(78), 0, math.radians(40))),
        "Silhouette_Weapons.png": camera("CamWeapons", (0, -3.1, 0.82), (math.radians(86), 0, 0), 2.4),
    }
    PROGRESS.mkdir(parents=True, exist_ok=True)
    for filename, cam in cams.items():
        bpy.context.scene.camera = cam
        bpy.context.scene.render.filepath = str(PROGRESS / filename)
        bpy.ops.render.render(write_still=True)
    blend = PROGRESS / "Silhouette_Pass.blend"
    glb = PROGRESS / "Silhouette_Pass.glb"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), copy=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True)
    report = {
        "phase": "silhouette_pass",
        "files": [str(PROGRESS / n) for n in cams] + [str(blend), str(glb)],
        "notes": [
            "Silhouette validation build.",
            "Neutral materials only.",
            "Roblox custom-mesh direction, not a default avatar.",
        ],
    }
    (PROGRESS / "Silhouette_Report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


def main():
    clean()
    setup_scene()
    build_character()
    render_outputs()


if __name__ == "__main__":
    main()
