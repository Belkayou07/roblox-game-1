from __future__ import annotations
import math
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "generated" / "cursed_ninja"
BLEND = OUT / "cursed_ninja.blend"
FBX = OUT / "cursed_ninja.fbx"

PARTS = {
    "LowerTorso": ((1.55,.92,.82),(0,0,4.02)), "UpperTorso": ((2.30,1.02,1.48),(0,0,5.17)),
    "Head": ((1.62,1.02,1.48),(0,0,6.83)),
    "LeftUpperArm": ((.72,.78,1.45),(-1.58,0,5.25)), "LeftLowerArm": ((.62,.69,1.32),(-1.58,0,3.87)), "LeftHand": ((.66,.73,.55),(-1.58,-.02,2.93)),
    "RightUpperArm": ((.72,.78,1.45),(1.58,0,5.25)), "RightLowerArm": ((.62,.69,1.32),(1.58,0,3.87)), "RightHand": ((.66,.73,.55),(1.58,-.02,2.93)),
    "LeftUpperLeg": ((.78,.86,1.60),(-.44,0,2.83)), "LeftLowerLeg": ((.66,.75,1.50),(-.44,0,1.28)), "LeftFoot": ((.78,1.18,.50),(-.44,-.14,.28)),
    "RightUpperLeg": ((.78,.86,1.60),(.44,0,2.83)), "RightLowerLeg": ((.66,.75,1.50),(.44,0,1.28)), "RightFoot": ((.78,1.18,.50),(.44,-.14,.28)),
}
BONES = {
    "Root":((0,0,3.7),(0,0,4.02),None,False), "LowerTorso":((0,0,3.62),(0,0,4.43),"Root",True), "UpperTorso":((0,0,4.43),(0,0,5.91),"LowerTorso",True), "Head":((0,0,5.91),(0,0,7.57),"UpperTorso",True),
    "LeftUpperArm":((-1.15,0,5.70),(-1.58,0,4.53),"UpperTorso",True), "LeftLowerArm":((-1.58,0,4.53),(-1.58,0,3.21),"LeftUpperArm",True), "LeftHand":((-1.58,0,3.21),(-1.58,-.02,2.65),"LeftLowerArm",True),
    "RightUpperArm":((1.15,0,5.70),(1.58,0,4.53),"UpperTorso",True), "RightLowerArm":((1.58,0,4.53),(1.58,0,3.21),"RightUpperArm",True), "RightHand":((1.58,0,3.21),(1.58,-.02,2.65),"RightLowerArm",True),
    "LeftUpperLeg":((-.44,0,3.62),(-.44,0,2.03),"LowerTorso",True), "LeftLowerLeg":((-.44,0,2.03),(-.44,0,.53),"LeftUpperLeg",True), "LeftFoot":((-.44,0,.53),(-.44,-.48,.18),"LeftLowerLeg",True),
    "RightUpperLeg":((.44,0,3.62),(.44,0,2.03),"LowerTorso",True), "RightLowerLeg":((.44,0,2.03),(.44,0,.53),"RightUpperLeg",True), "RightFoot":((.44,0,.53),(.44,-.48,.18),"RightLowerLeg",True),
    "Spine":((0,0,4.43),(0,0,5.1),"UpperTorso",False), "Chest":((0,0,5.1),(0,0,5.78),"Spine",False),
    "LeftClavicle":((0,0,5.63),(-1.15,0,5.70),"Chest",False), "RightClavicle":((0,0,5.63),(1.15,0,5.70),"Chest",False),
}
ATT = {
 "HatAttachment":("Head",(0,0,7.54)), "HairAttachment":("Head",(0,.1,7.45)), "FaceFrontAttachment":("Head",(0,-.53,6.82)), "FaceCenterAttachment":("Head",(0,-.50,6.82)), "NeckAttachment":("Head",(0,0,6.08)),
 "BodyFrontAttachment":("UpperTorso",(0,-.53,5.15)), "BodyBackAttachment":("UpperTorso",(0,.53,5.15)), "LeftCollarAttachment":("UpperTorso",(-.9,0,5.75)), "RightCollarAttachment":("UpperTorso",(.9,0,5.75)),
 "WaistFrontAttachment":("LowerTorso",(0,-.48,4.02)), "WaistCenterAttachment":("LowerTorso",(0,0,4.02)), "WaistBackAttachment":("LowerTorso",(0,.48,4.02)),
 "LeftShoulderAttachment":("LeftUpperArm",(-1.58,0,5.94)), "RightShoulderAttachment":("RightUpperArm",(1.58,0,5.94)), "LeftGripAttachment":("LeftHand",(-1.58,-.38,2.92)), "RightGripAttachment":("RightHand",(1.58,-.38,2.92)),
 "LeftFootAttachment":("LeftFoot",(-.44,-.58,.28)), "RightFootAttachment":("RightFoot",(.44,-.58,.28)), "RootRigAttachment":("LowerTorso",(0,0,3.62)),
}

def clear():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def col(name):
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if not c.users: bpy.context.scene.collection.children.link(c)
    return c

def move(o,c):
    for x in list(o.users_collection): x.objects.unlink(o)
    c.objects.link(o)

def mat(name,color,metal=0,rough=.72):
    m=bpy.data.materials.new('CN_'+name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    if p: p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    return m

def bevel(o,w=.025):
    b=o.modifiers.new('CN_Bevel','BEVEL'); b.width=w; b.segments=2; b.limit_method='ANGLE'

def box(name,size,loc,c,m,rot=(0,0,0),bev=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=rot); o=bpy.context.object; o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m); move(o,c)
    if bev: bevel(o,min(bev,min(size)*.14))
    return o

def prism(name,bottom,top,h,loc,c,m,rot=(0,0,0),bev=.02):
    bw,bd=bottom[0]/2,bottom[1]/2; tw,td=top[0]/2,top[1]/2; z=h/2
    v=[(-bw,-bd,-z),(bw,-bd,-z),(bw,bd,-z),(-bw,bd,-z),(-tw,-td,z),(tw,-td,z),(tw,td,z),(-tw,td,z)]
    f=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); c.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m)
    if bev: bevel(o,bev)
    return o

def poly(name,pts,depth,loc,c,m,rot=(0,0,0),bev=.012):
    n=len(pts); y=depth/2; v=[(x,-y,z) for x,z in pts]+[(x,y,z) for x,z in pts]
    f=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); c.objects.link(o); o.location=loc; o.rotation_euler=rot; o.data.materials.append(m)
    if bev: bevel(o,bev)
    return o

def curve(name,pts,r,c,m):
    d=bpy.data.curves.new(name+'_Curve','CURVE'); d.dimensions='3D'; d.bevel_depth=r; d.bevel_resolution=1
    s=d.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,d); c.objects.link(o); d.materials.append(m); return o

def parent(o,rig,bone):
    w=o.matrix_world.copy(); o.parent=rig; o.parent_type='BONE'; o.parent_bone=bone; o.matrix_world=w

def rig(c):
    d=bpy.data.armatures.new('CursedNinja_Armature'); r=bpy.data.objects.new('CursedNinja_Rig',d); c.objects.link(r); r.show_in_front=True
    bpy.context.view_layer.objects.active=r; r.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); eb={}
    for n,(h,t,p,deform) in BONES.items(): b=d.edit_bones.new(n); b.head=h; b.tail=t; b.use_deform=deform; eb[n]=b
    for n,(_,_,p,_) in BONES.items():
        if p: eb[n].parent=eb[p]
    bpy.ops.object.mode_set(mode='OBJECT'); r.select_set(False); return r

def crescent(name,r1,r2,a1,a2,segments,c,m,broken=False):
    ang=[a1+(a2-a1)*i/segments for i in range(segments+1)]; outer=[]; inner=[]
    for i,a in enumerate(ang):
        rr=r1+((-0.13 if i%2 else .06) if broken and i>=segments-2 else 0); outer.append((math.cos(a)*rr,math.sin(a)*rr)); inner.append((math.cos(a)*r2,math.sin(a)*r2))
    return poly(name,outer+inner[::-1],.13,(0,0,0),c,m,bev=.018)

def pose(r):
    sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=72; act=bpy.data.actions.new('CursedNinja_MobilityTest'); r.animation_data_create(); r.animation_data.action=act
    mid={"LowerTorso":(0,0,-.14),"UpperTorso":(.12,-.15,.19),"Head":(-.12,.28,-.07),"LeftUpperArm":(.31,-.14,-.73),"LeftLowerArm":(-1.08,0,-.14),"RightUpperArm":(-.24,.17,.59),"RightLowerArm":(-.84,0,.17),"LeftUpperLeg":(.56,-.17,-.12),"LeftLowerLeg":(-.98,0,0),"RightUpperLeg":(-.31,.10,.09),"RightLowerLeg":(-.42,0,0)}
    for frame,data in ((1,{}),(36,mid),(72,{})):
        sc.frame_set(frame)
        for b in r.pose.bones: b.rotation_mode='XYZ'; b.rotation_euler=(0,0,0)
        for n,rot in data.items(): r.pose.bones[n].rotation_euler=rot
        for b in r.pose.bones: b.keyframe_insert('rotation_euler',frame=frame,group=b.name)
    sc.frame_set(1)

def main():
    OUT.mkdir(parents=True,exist_ok=True); clear(); sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE_NEXT'; sc['unit_convention']='1 Blender unit = 1 Roblox stud'; sc['character']='Original Cursed Ninja'
    C={n:col('CN_'+n) for n in ('Body','Outfit','Hair','Weapons','Rig','Attachments','Guides')}
    M={
      'skin':mat('SkinShadow',(.07,.055,.052)), 'black':mat('RobeBlack',(.015,.018,.023)), 'char':mat('RobeCharcoal',(.04,.043,.05)), 'edge':mat('RobeEdge',(.075,.078,.088)),
      'red':mat('CursedRed',(.28,.01,.018)), 'darkred':mat('CursedRedDark',(.10,.004,.008)), 'wrap':mat('WrapGrey',(.12,.115,.12)), 'hair':mat('HairBlack',(.004,.005,.008)),
      'armor':mat('ArmorBlack',(.02,.022,.027),.72,.34), 'metal':mat('MetalBlack',(.014,.016,.02),.82,.28), 'crack':mat('MetalCrack',(.40,.018,.025),.25,.42), 'guide':mat('Guide',(.1,.42,.82))}
    R=rig(C['Rig']); export=[]
    for n,(size,loc) in PARTS.items():
        o=prism(n,(1.6,.9),(2.3,1.02),size[2],loc,C['Body'],M['skin'],bev=.04) if n=='UpperTorso' else box(n,size,loc,C['Body'],M['skin'],bev=.04 if n=='Head' else .025)
        o['roblox_body_part']=n; parent(o,R,n); export.append(o)
    for args in [
      ('Outfit_UpperRobe',(1.74,1.02),(2.48,1.16),1.54,(0,0,5.16),'UpperTorso','black'), ('Outfit_LowerRobe',(1.72,1.06),(1.70,1.03),.88,(0,0,4.02),'LowerTorso','char')]:
        n,b,t,h,l,bone,ma=args; o=prism(n,b,t,h,l,C['Outfit'],M[ma],bev=.03); parent(o,R,bone); export.append(o)
    panels=[('FrontLeft',(-.47,-.55,3.30),(.68,.10,1.55),(.06,-.08,.03),'black'),('FrontRight',(.38,-.57,3.35),(.72,.10,1.38),(-.03,.09,-.02),'char'),('BackLong',(.15,.56,3.18),(1.15,.10,1.78),(.05,-.05,.02),'black'),('SideLeft',(-.88,.03,3.42),(.12,.82,1.35),(.02,.06,-.06),'edge')]
    for n,l,s,r,ma in panels: o=box('Outfit_RaggedPanel_'+n,s,l,C['Outfit'],M[ma],r,.015); parent(o,R,'LowerTorso'); export.append(o)
    for bone,(size,loc) in PARTS.items():
        if bone in ('Head','UpperTorso','LowerTorso','LeftHand','RightHand','LeftFoot','RightFoot'): continue
        shell=box('Outfit_'+bone,tuple(x+(.07 if i<2 else .05) for i,x in enumerate(size)),loc,C['Outfit'],M['black' if 'Right' in bone else 'char'],bev=.022); parent(shell,R,bone); export.append(shell)
    for side,x in [('Left',-1.58),('Right',1.58)]:
        for i,z in enumerate((4.24,3.91,3.58)):
            o=box(f'Wrap_{side}Forearm_{i}',(.75,.83,.12),(x,0,z),C['Outfit'],M['wrap'],(0,0,(.10 if side=='Left' else -.10)*(i+1)),.012); parent(o,R,side+'LowerArm'); export.append(o)
    for side,x in [('Left',-.44),('Right',.44)]:
        for i,z in enumerate((1.65,1.32,.99)):
            o=box(f'Wrap_{side}Shin_{i}',(.79,.88,.12),(x,0,z),C['Outfit'],M['wrap'],(0,0,(.07 if side=='Left' else -.07)*(i+1)),.012); parent(o,R,side+'LowerLeg'); export.append(o)
        o=prism('Boot_'+side,(.88,1.34),(.78,.95),.62,(x,-.14,.31),C['Outfit'],M['armor'],bev=.028); parent(o,R,side+'Foot'); export.append(o)
    o=box('Head_HoodBack',(1.78,1.12,1.54),(0,.06,6.84),C['Outfit'],M['black'],bev=.07); parent(o,R,'Head'); export.append(o)
    for n,l,s,r,ma in [('Core',(0,-.58,6.95),(1.82,.13,.43),(.02,0,.02),'black'),('Upper',(-.03,-.60,7.10),(1.86,.12,.27),(-.02,0,-.04),'char'),('Lower',(.04,-.61,6.78),(1.80,.12,.26),(.04,0,.05),'edge')]:
        o=box('Blindfold_'+n,s,l,C['Outfit'],M[ma],r,.02); parent(o,R,'Head'); export.append(o)
    o=prism('Scarf_HighCollar',(1.8,1.18),(1.68,1.10),.72,(0,0,6.2),C['Outfit'],M['char'],(.02,0,0),.03); parent(o,R,'Head'); export.append(o)
    for n,l,s,r,ma in [('Long',(.48,.55,5.55),(.30,.11,1.48),(.14,-.18,-.10),'black'),('Red',(-.48,.57,5.68),(.23,.10,1.16),(-.08,.20,.16),'darkred'),('Short',(.04,.62,5.82),(.34,.10,.82),(.10,.02,-.08),'edge')]:
        o=box('Scarf_TornTail_'+n,s,l,C['Outfit'],M[ma],r,.014); parent(o,R,'Head'); export.append(o)
    o=prism('Hair_CrownMass',(1.76,1.10),(1.38,.96),.72,(0,.05,7.48),C['Hair'],M['hair'],bev=.05); parent(o,R,'Head'); export.append(o)
    paths=[ [(-.72,.20,7.55),(-.98,.32,6.85),(-1.08,.40,5.90),(-.88,.46,4.98)], [(-.48,.44,7.62),(-.70,.58,6.76),(-.62,.65,5.78),(-.48,.62,4.82)], [(-.15,.54,7.66),(-.22,.72,6.82),(-.08,.76,5.72),(.04,.70,4.74)], [(.20,.53,7.64),(.35,.70,6.80),(.48,.75,5.70),(.56,.60,4.92)], [(.53,.40,7.60),(.78,.52,6.88),(.92,.54,6.05),(.78,.45,5.22)], [(.73,.12,7.52),(1,.10,6.92),(1.12,.08,6.22),(.98,.04,5.52)], [(-.64,-.34,7.52),(-.82,-.55,7.05),(-.72,-.62,6.48)], [(.52,-.40,7.56),(.70,-.58,7.12),(.60,-.64,6.50)] ]
    for i,p in enumerate(paths): o=curve(f'Hair_Strand_{i}',p,.08+(i%3)*.012,C['Hair'],M['hair']); parent(o,R,'Head'); export.append(o)
    for i,(x,z,w,t) in enumerate([(-.58,7.18,.28,-.32),(-.24,7.22,.23,.18),(.18,7.20,.25,-.12),(.55,7.17,.27,.30)]):
        o=prism(f'Hair_Fringe_{i}',(w*.48,.12),(w,.15),.78,(x,-.66,z),C['Hair'],M['hair'],(t,0,.06*(-1 if i%2 else 1)),.014); parent(o,R,'Head'); export.append(o)
    o=poly('Armor_BrokenChestPlate',[(-.84,-.54),(.72,-.48),(.93,.38),(.32,.67),(-.62,.58),(-.96,.16)],.12,(0,-.59,5.20),C['Outfit'],M['armor'],(0,0,-.035),.022); parent(o,R,'UpperTorso'); export.append(o)
    for side,l,s,r in [('Left',(-1.45,-.02,5.78),(.88,1,.28),(.02,-.12,-.20)),('Right',(1.42,.02,5.72),(.68,.88,.22),(-.04,.18,.16))]:
        o=box('Armor_'+side+'BrokenShoulder',s,l,C['Outfit'],M['armor'],r,.03); parent(o,R,side+'UpperArm'); export.append(o)
    o=box('Accent_RedWaistSash',(1.92,1.12,.28),(0,0,3.92),C['Outfit'],M['darkred'],(0,0,-.04),.02); parent(o,R,'LowerTorso'); export.append(o)
    for n,l,s,r in [('Long',(-.58,.48,3.10),(.24,.10,1.50),(.12,-.18,.12)),('Short',(.56,-.45,3.34),(.20,.10,1.10),(-.08,.16,-.14))]:
        o=box('Accent_RedSashTail_'+n,s,l,C['Outfit'],M['red'],r,.012); parent(o,R,'LowerTorso'); export.append(o)
    long=crescent('Weapon_LongBrokenCrescent_Blade',2.15,1.66,math.radians(-66),math.radians(64),10,C['Weapons'],M['metal'],True); long.location=(-.52,.70,5.30); long.rotation_euler=(math.radians(78),math.radians(8),math.radians(-28)); parent(long,R,'UpperTorso'); export.append(long)
    short=crescent('Weapon_ShortHooked_Blade',1.42,1.04,math.radians(-82),math.radians(48),8,C['Weapons'],M['metal']); short.location=(.62,.78,5.08); short.rotation_euler=(math.radians(82),math.radians(-8),math.radians(31)); parent(short,R,'UpperTorso'); export.append(short)
    for n,l,s,r,ma in [('Long',(-.84,.78,4.34),(.26,.26,1.18),(math.radians(78),math.radians(8),math.radians(-28)),'wrap'),('Short',(.83,.82,4.25),(.24,.24,.92),(math.radians(82),math.radians(-8),math.radians(31)),'darkred')]:
        o=box('Weapon_'+n+'_Handle',s,l,C['Weapons'],M[ma],r,.02); parent(o,R,'UpperTorso'); export.append(o)
    for n,(bone,l) in ATT.items():
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.07,location=l); o=bpy.context.object; o.name=n; o.data.materials.append(M['guide']); o.display_type='WIRE'; o.hide_render=True; move(o,C['Attachments']); parent(o,R,bone); export.append(o)
    bpy.ops.mesh.primitive_plane_add(size=9,location=(0,0,0)); g=bpy.context.object; g.name='CN_GroundGuide'; g.data.materials.append(M['guide']); g.display_type='WIRE'; g.hide_render=True; move(g,C['Guides'])
    pose(R); bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    bpy.ops.object.select_all(action='DESELECT')
    for o in export: o.select_set(True)
    R.select_set(True); bpy.context.view_layer.objects.active=R
    bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'ARMATURE','MESH','OTHER'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=False,mesh_smooth_type='FACE')
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND)); print('Cursed Ninja generated:',BLEND,FBX)

if __name__=='__main__': main()
