from __future__ import annotations

import json, math, os
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(os.environ.get("SHATTERED_VEIL_OUTPUT", Path.cwd() / "TheShatteredVeil"))
OUT = ROOT / "Progress"


def material(name, color, rough=0.7, metal=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = color
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emission is not None:
        p.inputs["Emission Color"].default_value = emission
        p.inputs["Emission Strength"].default_value = strength
    return m


def finish(o, m, sub=1, bevel=0.0):
    if o.type == "MESH":
        if bevel > 0:
            b = o.modifiers.new("Bevel", "BEVEL")
            b.width = bevel
            b.segments = 2
            b.limit_method = "ANGLE"
        s = o.modifiers.new("Subd", "SUBSURF")
        s.levels = sub
        s.render_levels = sub
        for poly in o.data.polygons:
            poly.use_smooth = True
        if m:
            o.data.materials.append(m)
    elif o.type == "CURVE":
        if m:
            o.data.materials.append(m)
    return o


def cube(name, loc, scale, rot=(0,0,0), m=None, sub=1, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, m, sub=sub, bevel=bevel)


def sphere(name, loc, scale, m=None, sub=1):
    bpy.ops.mesh.primitive_uv_sphere_add(location=loc, segments=22, ring_count=12)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, m, sub=sub)


def cyl(name, loc, scale, rot=(0,0,0), m=None, sub=1):
    bpy.ops.mesh.primitive_cylinder_add(location=loc, rotation=rot, vertices=18)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, m, sub=sub)


def curve_piece(name, pts, thickness, m=None, resolution=8):
    c = bpy.data.curves.new(name, type="CURVE")
    c.dimensions = "3D"
    c.resolution_u = resolution
    spline = c.splines.new("BEZIER")
    spline.bezier_points.add(len(pts)-1)
    for bp, pt in zip(spline.bezier_points, pts):
        bp.co = Vector(pt)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    c.bevel_depth = thickness
    c.bevel_resolution = 4
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    return finish(o, m)


def tapered_panel(name, top, bottom, width_top, width_bottom, thickness, m=None):
    mesh = bpy.data.meshes.new(name)
    tx = width_top * 0.5
    bx = width_bottom * 0.5
    verts = [
        (-tx, 0, 0), (tx, 0, 0), (-bx, 0, -bottom), (bx, 0, -bottom),
        (-tx, thickness, 0), (tx, thickness, 0), (-bx, thickness, -bottom), (bx, thickness, -bottom),
    ]
    verts = [(v[0], v[1] + top.y, v[2] + top.z) for v in verts]
    faces = [
        (0,1,3,2),(4,6,7,5),(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    o.location.x = top.x
    return finish(o, m, sub=1, bevel=0.002)


def point_camera(cam, target):
    q = (target - cam.location).to_track_quat('-Z', 'Y')
    cam.rotation_euler = q.to_euler()


def camera(name, loc, target, ortho=None):
    d = bpy.data.cameras.new(name)
    if ortho is not None:
        d.type = 'ORTHO'
        d.ortho_scale = ortho
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    point_camera(o, target)
    return o


def light(name, loc, target, energy, size):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = energy
    d.shape = 'RECTANGLE'
    d.size = size
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    point_camera(o, target)
    return o


def shape_torso(o):
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(1.0, 0.82, 1.0))
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    zs = [v.co.z for v in o.data.vertices]
    zmin, zmax = min(zs), max(zs)
    for v in o.data.vertices:
        t = (v.co.z - zmin) / (zmax - zmin + 1e-6)
        if t > 0.72:
            v.co.x *= 0.86
            v.co.y *= 0.78
        elif t < 0.28:
            v.co.x *= 0.78
            v.co.y *= 0.72
        else:
            v.co.x *= 0.98
            v.co.y *= 0.84
    o.data.update()


def shape_head(o):
    for v in o.data.vertices:
        if v.co.z > 0:
            v.co.y *= 0.9
        if v.co.z < 0:
            v.co.x *= 0.95
    o.data.update()


def convert_curve_to_mesh(o):
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target='MESH')
    return bpy.context.object


def build():
    char = material('Char_Dark', (.10,.11,.13,1), .78)
    char2 = material('Char_Mid', (.23,.24,.27,1), .74)
    cloth = material('Cloth_Grey', (.34,.35,.39,1), .86)
    red = material('Accent_Red', (.56,.14,.18,1), .78)
    red_soft = material('Accent_RedSoft', (.66,.24,.28,1), .82)
    metal = material('Blade_Metal', (.54,.56,.60,1), .28, .55)
    glow = material('Blade_Glow', (.40,.40,.42,1), .45, 0.0, (.90,.18,.22,1), .85)
    floor = material('Floor', (.10,.105,.115,1), .96)

    torso = cube('Torso', (0, 0, 1.46), (.22, .14, .33), m=char2, bevel=.012)
    shape_torso(torso)
    pelvis = cube('Pelvis', (0, -.005, .97), (.15, .10, .10), m=char, bevel=.01)
    chest_wrap = cube('ChestWrap', (0, -.01, 1.46), (.24, .155, .27), m=char, bevel=.008)
    shape_torso(chest_wrap)
    neck = cyl('Neck', (0, -.005, 1.82), (.07,.07,.06), m=char2)
    head = sphere('Head', (0, .0, 2.07), (.12,.13,.17), m=char2)
    shape_head(head)

    blindfold = cube('Blindfold', (0, -.015, 2.07), (.145, .075, .032), rot=(math.radians(2),0,0), m=cloth, bevel=.006)
    face_wrap = cube('FaceWrap', (0, -.025, 1.95), (.115,.085,.115), rot=(math.radians(10),0,0), m=char2, bevel=.01)
    nose_fall = tapered_panel('Face_Fall', Vector((0,-.10,2.00)), .20, .08, .04, .010, cloth)
    band_tail = curve_piece('BandTail', [(.16,.00,2.06),(.28,.05,1.96),(.37,.08,1.86)], .009, red_soft)

    l_sh = sphere('L_Shoulder', (.285,.00,1.58), (.085,.085,.085), char2)
    r_sh = sphere('R_Shoulder', (-.285,.00,1.58), (.085,.085,.085), char2)
    l_upper = cyl('L_UpperArm', (.47,-.03,1.39), (.055,.055,.17), rot=(math.radians(105),0,math.radians(18)), m=char)
    r_upper = cyl('R_UpperArm', (-.47,-.03,1.40), (.055,.055,.17), rot=(math.radians(105),0,math.radians(-16)), m=char)
    l_elbow = sphere('L_Elbow', (.62,-.07,1.18), (.043,.043,.043), char2)
    r_elbow = sphere('R_Elbow', (-.60,-.07,1.20), (.043,.043,.043), char2)
    l_fore = cyl('L_ForeArm', (.75,-.11,1.02), (.043,.043,.15), rot=(math.radians(106),0,math.radians(15)), m=char2)
    r_fore = cyl('R_ForeArm', (-.73,-.12,1.00), (.043,.043,.15), rot=(math.radians(106),0,math.radians(-12)), m=red_soft)
    l_wrist = sphere('L_Wrist', (.85,-.15,.86), (.032,.032,.032), char2)
    r_wrist = sphere('R_Wrist', (-.84,-.16,.85), (.032,.032,.032), char2)
    l_hand = cube('L_Hand', (.91,-.16,.80), (.055,.025,.028), rot=(math.radians(18),0,math.radians(8)), m=char2, bevel=.004)
    r_hand = cube('R_Hand', (-.90,-.16,.78), (.055,.025,.028), rot=(math.radians(18),0,math.radians(-10)), m=char2, bevel=.004)
    fore_guard = cube('L_ForearmGuard', (.76,-.10,1.00), (.04,.08,.03), rot=(math.radians(15),0,math.radians(8)), m=cloth, bevel=.004)
    shoulder_guard = cube('R_ShoulderGuard', (-.34,.03,1.57), (.10,.06,.025), rot=(math.radians(20),0,math.radians(-24)), m=cloth, bevel=.004)

    l_thigh = cyl('L_Thigh', (.11,-.01,.72), (.082,.075,.17), rot=(0,0,math.radians(1)), m=char)
    r_thigh = cyl('R_Thigh', (-.11,-.01,.70), (.079,.073,.17), rot=(0,0,math.radians(-1)), m=char)
    l_knee = sphere('L_Knee', (.11,-.01,.50), (.038,.038,.038), char2)
    r_knee = sphere('R_Knee', (-.11,-.01,.49), (.038,.038,.038), char2)
    l_shin = cyl('L_Shin', (.11,.00,.28), (.056,.05,.15), m=red)
    r_shin = cyl('R_Shin', (-.10,.00,.28), (.053,.048,.15), m=char)
    l_ankle = sphere('L_Ankle', (.11,.00,.09), (.028,.028,.028), char2)
    r_ankle = sphere('R_Ankle', (-.10,.00,.09), (.028,.028,.028), char2)
    l_foot = cube('L_Foot', (.11,.07,.035), (.08,.12,.03), rot=(math.radians(2),0,0), m=char2, bevel=.006)
    r_foot = cube('R_Foot', (-.10,.07,.035), (.08,.12,.03), rot=(math.radians(-2),0,0), m=char2, bevel=.006)

    hair_cap = sphere('HairCap', (0,.02,2.08), (.145,.16,.16), m=char, sub=1)
    hair_specs = [
        ('HairL1', [(.06,.06,2.12),(.19,.12,1.94),(.28,.16,1.68),(.36,.14,1.36)], .016, char),
        ('HairL2', [(.01,.08,2.14),(.06,.18,1.96),(.08,.24,1.64),(.10,.21,1.24)], .018, char2),
        ('HairL3', [(-.05,.06,2.12),(-.18,.12,1.95),(-.28,.15,1.70),(-.36,.12,1.40)], .016, char),
        ('HairF1', [(.10,-.01,2.10),(.08,-.05,1.96),(.05,-.06,1.82)], .010, cloth),
        ('HairF2', [(-.09,-.01,2.09),(-.08,-.05,1.95),(-.05,-.06,1.80)], .010, cloth),
        ('HairSideR', [(-.14,.04,2.09),(-.25,.11,1.94),(-.32,.13,1.66)], .013, red_soft),
    ]
    hair_objs=[]
    for n, pts, th, m in hair_specs:
        hair_objs.append(curve_piece(n, pts, th, m))

    robe = tapered_panel('Front_Robe', Vector((0,-.12,1.62)), .55, .34, .22, .014, cloth)
    robe.rotation_euler.x = math.radians(2)
    waist = cube('Waist_Sash', (0,-.005,1.03), (.23,.09,.05), m=red_soft, bevel=.005)
    front_main = tapered_panel('Front_Main_Cloth', Vector((0,-.095,1.02)), .68, .13, .07, .012, cloth)
    front_side_l = tapered_panel('Front_Side_L', Vector((.12,-.03,1.00)), .52, .09, .06, .010, cloth)
    front_side_l.rotation_euler = (math.radians(2), math.radians(8), math.radians(4))
    side_red = tapered_panel('Side_Red_Cloth', Vector((-.15,.05,1.01)), .60, .12, .08, .010, red)
    side_red.rotation_euler = (math.radians(-2), math.radians(-8), math.radians(-4))
    back_skirt = tapered_panel('Back_Skirt', Vector((0,.10,1.03)), .62, .22, .18, .010, char)
    back_skirt.rotation_euler.x = math.radians(4)
    hip_wrap_l = cube('HipWrapL', (.08,.01,.73), (.075,.07,.11), m=char, bevel=.006)
    hip_wrap_r = cube('HipWrapR', (-.08,.01,.73), (.075,.07,.11), m=char, bevel=.006)

    l_guard = cube('L_Guard', (.86,-.18,.77), (.048,.012,.028), rot=(math.radians(6),0,math.radians(10)), m=metal, bevel=.002)
    l_handle = cube('L_Handle', (.91,-.16,.80), (.014,.070,.014), rot=(math.radians(95),0,math.radians(12)), m=char2, bevel=.002)
    l_blade = curve_piece('L_BladeCurve', [(.92,-.18,.78),(1.00,-.32,.74),(1.09,-.51,.67),(1.18,-.72,.58)], .020, metal)
    l_glow = curve_piece('L_BladeGlow', [(.92,-.18,.785),(1.00,-.32,.745),(1.09,-.51,.675),(1.18,-.72,.585)], .0035, glow)

    r_guard = cube('R_Guard', (-.84,-.18,.75), (.060,.012,.030), rot=(math.radians(2),0,math.radians(-8)), m=metal, bevel=.002)
    r_handle = cube('R_Handle', (-.89,-.16,.78), (.015,.078,.015), rot=(math.radians(92),0,math.radians(-10)), m=char2, bevel=.002)
    r_blade = curve_piece('R_BladeCurve', [(-.90,-.18,.76),(-.99,-.36,.71),(-1.08,-.60,.58),(-1.20,-.82,.42)], .024, metal)
    r_glow = curve_piece('R_BladeGlow', [(-.90,-.18,.765),(-.99,-.36,.715),(-1.08,-.60,.585),(-1.20,-.82,.425)], .0035, glow)

    bpy.ops.mesh.primitive_plane_add(size=8, location=(0,0,0))
    floor_obj = bpy.context.object
    floor_obj.data.materials.append(floor)

    return [torso,pelvis,chest_wrap,neck,head,blindfold,face_wrap,nose_fall,band_tail,l_sh,r_sh,l_upper,r_upper,l_elbow,r_elbow,l_fore,r_fore,l_wrist,r_wrist,l_hand,r_hand,fore_guard,shoulder_guard,l_thigh,r_thigh,l_knee,r_knee,l_shin,r_shin,l_ankle,r_ankle,l_foot,r_foot,hair_cap,*hair_objs,robe,waist,front_main,front_side_l,side_red,back_skirt,hip_wrap_l,hip_wrap_r,l_guard,l_handle,l_blade,l_glow,r_guard,r_handle,r_blade,r_glow,floor_obj]


def main():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.image_settings.file_format = 'PNG'
    scene.world.color = (.018,.019,.022)
    scene.view_settings.exposure = -0.45
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass

    target = Vector((0,-.02,1.18))
    light('Key', Vector((2.8,-3.2,3.3)), target, 920, 2.8)
    light('Fill', Vector((-2.2,-2.2,2.4)), target, 240, 3.0)
    light('Rim', Vector((.4,2.8,2.7)), target, 460, 2.0)

    objs = build()
    for o in list(objs):
        if o.type == 'CURVE':
            convert_curve_to_mesh(o)

    cams = {
        'Refined_Front.png': camera('Front', Vector((0,-4.85,1.23)), target, 2.35),
        'Refined_Side.png': camera('Side', Vector((4.85,0,1.18)), target, 2.35),
        'Refined_Back.png': camera('Back', Vector((0,4.75,1.22)), target, 2.35),
        'Refined_ThreeQuarter.png': camera('ThreeQuarter', Vector((3.6,-4.0,1.5)), target, 2.5),
        'Refined_Weapons.png': camera('Weapons', Vector((0,-4.2,.74)), Vector((0,-.06,.72)), 1.60),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    for fn, cam in cams.items():
        scene.camera = cam
        scene.render.filepath = str(OUT / fn)
        bpy.ops.render.render(write_still=True)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'Refined_Pass.blend'), copy=True)
    bpy.ops.object.select_all(action='DESELECT')
    export = [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.name.startswith('Front') and not o.name.startswith('Side') and not o.name.startswith('Back') and not o.name.startswith('ThreeQuarter') and not o.name.startswith('Weapons')]
    for o in export:
        o.select_set(True)
    bpy.context.view_layer.objects.active = export[0]
    bpy.ops.export_scene.gltf(filepath=str(OUT / 'Refined_Pass.glb'), export_format='GLB', use_selection=True, export_apply=True)
    report = {
        'phase': 'refined_pass',
        'renders': [str(OUT / x) for x in cams],
        'notes': [
            'Refined blockout pass.',
            'Improved torso taper, face covering, cloth layering, and swords.',
            'Still not final rig or final topology.'
        ]
    }
    (OUT / 'Refined_Report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
