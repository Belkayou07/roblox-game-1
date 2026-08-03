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
    if emission:
        p.inputs["Emission Color"].default_value = emission
        p.inputs["Emission Strength"].default_value = strength
    return m


def finish(o, m, sub=1, bevel=0.0):
    o.data.materials.append(m)
    if o.type == "MESH":
        for p in o.data.polygons:
            p.use_smooth = True
        if bevel:
            b = o.modifiers.new("Bevel", "BEVEL"); b.width = bevel; b.segments = 2
        if sub:
            s = o.modifiers.new("Subd", "SUBSURF"); s.levels = sub; s.render_levels = sub
    return o


def ellipsoid(name, loc, scale, m):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, m, 1)


def box(name, loc, scale, m, rot=(0,0,0), bevel=0.01):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, m, 1, bevel)


def segment(name, a, b, r1, r2, m):
    d = b-a; length = d.length
    bpy.ops.mesh.primitive_cone_add(vertices=18, radius1=r1, radius2=r2, depth=length, location=(a+b)/2)
    o = bpy.context.object; o.name = name
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = d.to_track_quat("Z","Y"); o.rotation_mode = "XYZ"
    return finish(o, m, 1)


def curve(name, pts, radii, m, depth):
    data = bpy.data.curves.new(name, "CURVE"); data.dimensions = "3D"; data.bevel_depth = depth; data.bevel_resolution = 2
    sp = data.splines.new("BEZIER"); sp.bezier_points.add(len(pts)-1)
    for bp, p, r in zip(sp.bezier_points, pts, radii):
        bp.co = p; bp.radius = r; bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, data); bpy.context.scene.collection.objects.link(o); o.data.materials.append(m)
    return o


def panel(name, pts, y1, y2, m):
    n = len(pts); verts = [(x,y1,z) for x,z in pts] + [(x,y2,z) for x,z in pts]
    faces = [tuple(range(n)), tuple(reversed(range(n,2*n)))]
    for i in range(n):
        j=(i+1)%n; faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(o)
    return finish(o,m,0,0.006)


def blade(name, path, widths, thick, m):
    left=[]; right=[]
    for i,p in enumerate(path):
        t=(path[min(i+1,len(path)-1)]-path[max(i-1,0)])
        t=Vector((t.x,0,t.z)).normalized(); n=Vector((-t.z,0,t.x))
        left.append(p+n*widths[i]); right.append(p-n*widths[i])
    verts=[]
    for y in (-thick/2,thick/2):
        for l,r in zip(left,right): verts += [(l.x,l.y+y,l.z),(r.x,r.y+y,r.z)]
    s=len(path)*2; faces=[]
    for layer in range(2):
        off=layer*s
        for i in range(len(path)-1):
            a=off+i*2; q=(a,a+1,a+3,a+2); faces.append(q if layer==0 else tuple(reversed(q)))
    for i in range(len(path)-1):
        a=i*2; faces += [(a,a+2,s+a+2,s+a),(a+1,s+a+1,s+a+3,a+3)]
    faces += [(0,s,s+1,1),(s-2,s-1,2*s-1,2*s-2)]
    mesh=bpy.data.meshes.new(name+"Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(o)
    return finish(o,m,0,0.004)


def camera(name, loc, target, scale):
    d=bpy.data.cameras.new(name); d.type="ORTHO"; d.ortho_scale=scale
    o=bpy.data.objects.new(name,d); bpy.context.scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(target-loc).to_track_quat("-Z","Y").to_euler(); return o


def light(name, loc, target, energy, size):
    d=bpy.data.lights.new(name,"AREA"); d.energy=energy; d.shape="DISK"; d.size=size
    o=bpy.data.objects.new(name,d); bpy.context.scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(target-loc).to_track_quat("-Z","Y").to_euler()


def build():
    skin=material("Skin",(0.075,0.07,0.075,1),0.82)
    inner=material("Inner",(0.018,0.02,0.025,1),0.88)
    outer=material("Outer",(0.045,0.047,0.055,1),0.93)
    red=material("Crimson",(0.18,0.015,0.025,1),0.86)
    hair=material("Hair",(0.008,0.009,0.012,1),0.55)
    metal=material("Metal",(0.08,0.085,0.095,1),0.42,0.72)
    glow=material("Glow",(0.35,0.01,0.018,1),0.5,0,(0.65,0.015,0.025,1),1.0)
    objs=[]

    torso=box("Body_Torso",Vector((0,-0.035,1.43)),(0.23,0.15,0.32),skin,rot=(math.radians(-3),0,0),bevel=0.055)
    pelvis=box("Body_Pelvis",Vector((0,0,1.00)),(0.18,0.13,0.12),skin,bevel=0.045)
    neck=segment("Body_Neck",Vector((0,-0.05,1.68)),Vector((0,-0.075,1.84)),0.085,0.075,skin)
    head=ellipsoid("Body_Head",Vector((0,-0.095,2.03)),(0.135,0.12,0.18),skin)
    objs += [torso,pelvis,neck,head]

    j={
      "LS":Vector((.29,-.05,1.62)),"LE":Vector((.49,-.12,1.32)),"LW":Vector((.64,-.18,1.04)),"LH":Vector((.68,-.19,.93)),
      "RS":Vector((-.29,-.04,1.62)),"RE":Vector((-.49,.02,1.35)),"RW":Vector((-.66,.07,1.13)),"RH":Vector((-.70,.08,1.02)),
      "LHIPP":Vector((.14,-.01,.98)),"LK":Vector((.18,-.06,.56)),"LA":Vector((.20,-.09,.15)),
      "RHIPP":Vector((-.14,.02,.98)),"RK":Vector((-.17,.07,.57)),"RA":Vector((-.18,.11,.15)),
    }
    for s in ("L","R"):
        S,E,W,H=j[s+"S"],j[s+"E"],j[s+"W"],j[s+"H"]
        objs += [ellipsoid("Body_"+s+"Shoulder",S,(.10,.10,.105),skin),segment("Body_"+s+"UpperArm",S,E,.088,.064,skin),ellipsoid("Body_"+s+"Elbow",E,(.062,.06,.065),skin),segment("Body_"+s+"Forearm",E,W,.064,.045,skin),ellipsoid("Body_"+s+"Wrist",W,(.045,.043,.047),skin),ellipsoid("Body_"+s+"Hand",H,(.055,.038,.078),skin)]
        objs += [segment("Cloth_"+s+"Sleeve",S,E,.098,.072,inner),segment("Cloth_"+s+"ArmWrap",E,W,.071,.052,red if s=="L" else inner)]
    for s in ("L","R"):
        H,K,A=j[s+"HIPP"],j[s+"K"],j[s+"A"]
        objs += [segment("Body_"+s+"Thigh",H,K,.12,.082,skin),ellipsoid("Body_"+s+"Knee",K,(.072,.068,.072),skin),segment("Body_"+s+"Shin",K,A,.082,.052,skin),ellipsoid("Body_"+s+"Ankle",A,(.05,.046,.046),skin)]
        objs += [segment("Cloth_"+s+"Trouser",H,K,.135,.096,inner),segment("Cloth_"+s+"LegWrap",K,A,.091,.061,inner if s=="L" else red)]
        fy=-.04 if s=="L" else .15
        objs += [box("Body_"+s+"Foot",Vector((A.x,fy,.075)),(.09,.17,.052),skin,rot=(math.radians(4),0,math.radians(2 if s=="L" else -2)),bevel=.018),box("Cloth_"+s+"Footwear",Vector((A.x,fy,.075)),(.102,.18,.06),inner,rot=(math.radians(4),0,math.radians(2 if s=="L" else -2)),bevel=.016)]

    objs += [box("Cloth_InnerTorso",Vector((0,-.04,1.43)),(.245,.165,.33),inner,rot=(math.radians(-3),0,0),bevel=.055)]
    objs += [panel("Cloth_RobeFront",[(-.29,1.70),(.27,1.70),(.25,1.20),(.17,1.09),(.08,1.17),(.01,1.06),(-.08,1.15),(-.17,1.07),(-.25,1.16)],-.225,-.175,outer)]
    objs += [panel("Cloth_RobeBack",[(-.27,1.68),(.28,1.68),(.24,1.13),(.15,1.02),(.06,1.11),(-.03,1.00),(-.12,1.10),(-.22,1.03)],.105,.165,outer)]
    objs += [box("Cloth_Sash",Vector((0,-.01,1.04)),(.255,.18,.055),red,bevel=.025)]
    objs += [panel("Cloth_WaistFront",[(-.10,1.03),(.11,1.03),(.12,.47),(.05,.34),(-.02,.41),(-.09,.30)],-.21,-.17,outer),panel("Cloth_WaistBack",[(-.12,1.03),(.13,1.03),(.11,.38),(.02,.26),(-.07,.36),(-.12,.28)],.14,.18,outer),panel("Cloth_WaistLeft",[(.09,1.03),(.23,1.02),(.29,.48),(.20,.31),(.14,.43)],-.02,.02,red),panel("Cloth_WaistRight",[(-.23,1.02),(-.09,1.03),(-.13,.45),(-.20,.33),(-.29,.47)],-.01,.03,outer)]

    objs += [box("Face_Blindfold",Vector((0,-.205,2.075)),(.15,.035,.047),inner,rot=(math.radians(2),0,0),bevel=.012),box("Face_WrapL",Vector((.13,-.135,2.065)),(.045,.08,.04),inner,rot=(0,math.radians(12),math.radians(-6)),bevel=.01),box("Face_WrapR",Vector((-.13,-.135,2.065)),(.045,.08,.04),inner,rot=(0,math.radians(-12),math.radians(6)),bevel=.01),box("Face_Scarf",Vector((0,-.17,1.91)),(.15,.07,.09),inner,rot=(math.radians(5),0,0),bevel=.025)]
    objs += [curve("Face_TailL",[Vector((.10,-.02,2.08)),Vector((.25,.02,1.98)),Vector((.38,0,1.80))],[1,.7,.15],red,.022),curve("Face_TailR",[Vector((-.10,-.02,2.07)),Vector((-.24,.04,1.95)),Vector((-.34,.01,1.79))],[1,.65,.15],inner,.022)]

    objs += [ellipsoid("Hair_Main",Vector((0,0,2.09)),(.16,.15,.17),hair)]
    locks=[
      ("Hair_FringeL",[(.03,-.19,2.17),(.10,-.23,2.04),(.15,-.23,1.89)],[1,.65,.12],.026),
      ("Hair_FringeR",[(-.02,-.19,2.18),(-.09,-.23,2.05),(-.14,-.22,1.91)],[1,.65,.12],.026),
      ("Hair_SideL",[(.12,-.08,2.17),(.24,-.06,1.99),(.32,-.03,1.72)],[1,.75,.18],.032),
      ("Hair_SideR",[(-.12,-.08,2.17),(-.25,-.04,1.98),(-.34,0,1.70)],[1,.74,.18],.032),
      ("Hair_BackC",[(0,.02,2.18),(0,.15,1.90),(.02,.19,1.50),(.04,.18,1.22)],[1,.95,.56,.10],.038),
      ("Hair_BackL1",[(.05,.01,2.17),(.18,.15,1.94),(.31,.18,1.61),(.48,.12,1.35)],[1,.85,.5,.1],.038),
      ("Hair_BackL2",[(.08,.02,2.14),(.27,.12,1.90),(.45,.12,1.61),(.58,.03,1.42)],[.9,.75,.42,.08],.034),
      ("Hair_BackR1",[(-.05,.01,2.17),(-.18,.15,1.94),(-.31,.18,1.60),(-.46,.12,1.32)],[1,.85,.5,.1],.038),
      ("Hair_BackR2",[(-.08,.02,2.14),(-.27,.12,1.90),(-.44,.10,1.62),(-.57,0,1.40)],[.9,.75,.42,.08],.034),
    ]
    for name,pts,rs,d in locks: objs.append(curve(name,[Vector(p) for p in pts],rs,hair,d))

    objs += [box("Accessory_ShoulderGuard",Vector((.31,-.065,1.64)),(.13,.10,.035),metal,rot=(math.radians(12),math.radians(-8),math.radians(10)),bevel=.012),box("Accessory_ForearmGuard",j["RW"].lerp(j["RE"],.48),(.065,.05,.11),metal,rot=(math.radians(-8),math.radians(7),math.radians(-25)),bevel=.01)]

    la=j["LH"]; lh1=la+Vector((-.005,-.005,.08)); lh2=la+Vector((.035,-.015,-.12))
    objs += [segment("Weapon_LongHandle",lh1,lh2,.027,.024,red),box("Weapon_LongGuard",lh2,(.09,.025,.018),metal,rot=(0,math.radians(8),math.radians(-7)),bevel=.006)]
    lp=[lh2+Vector((0,-.005,-.015)),Vector((.82,-.20,.69)),Vector((.97,-.18,.49)),Vector((1.14,-.15,.30)),Vector((1.26,-.12,.20))]
    objs += [blade("Weapon_LongBlade",lp,[.065,.082,.076,.055,.012],.032,metal),curve("Weapon_LongCrack",[lp[0]+Vector((.02,-.02,0)),lp[2]+Vector((0,-.02,.01)),lp[3]+Vector((-.015,-.02,0))],[.75,.55,.12],glow,.006)]

    ra=j["RH"]; rh1=ra+Vector((.005,-.005,.07)); rh2=ra+Vector((-.03,-.015,-.11))
    objs += [segment("Weapon_ShortHandle",rh1,rh2,.029,.025,red),box("Weapon_ShortGuard",rh2,(.082,.027,.022),metal,rot=(0,math.radians(-8),math.radians(8)),bevel=.006)]
    rp=[rh2+Vector((0,0,-.015)),Vector((-.81,.045,.82)),Vector((-.94,.035,.67)),Vector((-1.06,.02,.52)),Vector((-1.15,0,.44))]
    objs += [blade("Weapon_ShortBlade",rp,[.075,.085,.080,.060,.015],.036,metal),curve("Weapon_ShortCrack",[rp[0]+Vector((-.015,-.025,0)),rp[2]+Vector((.015,-.025,0)),rp[3]+Vector((0,-.025,-.005))],[.75,.5,.1],glow,.006)]
    return objs


def main():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene; scene.render.engine="BLENDER_EEVEE_NEXT"; scene.render.resolution_x=1000; scene.render.resolution_y=1200; scene.render.image_settings.file_format="PNG"; scene.world.color=(.018,.019,.023); scene.view_settings.exposure=-.65
    try: scene.view_settings.look="AgX - Medium High Contrast"
    except Exception: pass
    floor=material("Floor",(.08,.082,.09,1),.96); bpy.ops.mesh.primitive_plane_add(size=8); bpy.context.object.data.materials.append(floor)
    target=Vector((0,-.02,1.14)); light("Key",Vector((2.8,-3,3.2)),target,820,2.8); light("Fill",Vector((-2.2,-2.2,2.4)),target,270,3); light("Rim",Vector((.4,2.8,2.8)),target,520,2)
    objs=build()
    for o in list(objs):
        if o.type=="CURVE":
            bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active=o; bpy.ops.object.convert(target="MESH")
    cams={"Connected_Front.png":camera("Front",Vector((0,-5,1.2)),target,2.55),"Connected_Side.png":camera("Side",Vector((5,0,1.2)),target,2.55),"Connected_Back.png":camera("Back",Vector((0,5,1.2)),target,2.55),"Connected_ThreeQuarter.png":camera("ThreeQuarter",Vector((3.7,-4.2,1.55)),target,2.65),"Connected_Weapons.png":camera("Weapons",Vector((0,-4,.72)),Vector((0,-.05,.75)),1.65)}
    OUT.mkdir(parents=True,exist_ok=True)
    for fn,c in cams.items(): scene.camera=c; scene.render.filepath=str(OUT/fn); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"Connected_Pass.blend"),copy=True)
    bpy.ops.object.select_all(action="DESELECT"); export=[o for o in bpy.context.scene.objects if o.type=="MESH" and not o.name.startswith("Preview")]
    for o in export: o.select_set(True)
    bpy.context.view_layer.objects.active=export[0]; bpy.ops.export_scene.gltf(filepath=str(OUT/"Connected_Pass.glb"),export_format="GLB",use_selection=True,export_apply=True)
    (OUT/"Connected_Report.json").write_text(json.dumps({"phase":"connected_pass","renders":[str(OUT/x) for x in cams],"limitations":["Blockout only","No production rig yet","Hands simplified"]},indent=2),encoding="utf-8")


if __name__=="__main__": main()
