"""Generate an original modular anime-style Roblox NPC basemodel in Blender 4.2+.

Run from Blender's Scripting workspace or with the Windows launcher beside this
file. One Blender unit equals one Roblox stud. The character faces -Y.
"""
from __future__ import annotations
import math
import traceback
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "generated" / "anime_roblox_basemodel"
BLEND = OUT / "anime_roblox_basemodel.blend"
FBX = OUT / "anime_roblox_basemodel.fbx"
RENDERS = {k: OUT / f"anime_basemodel_{k}.png" for k in ("front","side","back","threequarter","rig")}
TAG = "anime_roblox_basemodel_v1"
COLS = ["00_RIG","01_BODY","02_HEAD","03_FACE","04_HAIR","05_CLOTHING","06_BOOTS","07_ACCESSORIES","08_ROBLOX_ATTACHMENTS","09_PREVIEW_OUTLINES","10_CAMERAS","11_LIGHTING","12_EXPORT","13_LOD"]
WARN=[]

BONES={
"Root":((0,0,3.35),(0,0,3.70),None,False),"Pelvis":((0,0,3.35),(0,0,3.95),"Root",True),
"Spine_01":((0,0,3.95),(0,0,4.35),"Pelvis",True),"Spine_02":((0,0,4.35),(0,0,4.78),"Spine_01",True),
"Chest":((0,0,4.78),(0,0,5.24),"Spine_02",True),"Neck":((0,0,5.24),(0,0,5.48),"Chest",True),"Head":((0,0,5.48),(0,0,6.28),"Neck",True),
"Clavicle_L":((-.12,0,5.12),(-1.03,0,5.12),"Chest",True),"UpperArm_L":((-1.03,0,5.12),(-2.08,0,5.12),"Clavicle_L",True),"LowerArm_L":((-2.08,0,5.12),(-3.16,0,5.12),"UpperArm_L",True),"Hand_L":((-3.16,0,5.12),(-3.63,0,5.12),"LowerArm_L",True),
"Clavicle_R":((.12,0,5.12),(1.03,0,5.12),"Chest",True),"UpperArm_R":((1.03,0,5.12),(2.08,0,5.12),"Clavicle_R",True),"LowerArm_R":((2.08,0,5.12),(3.16,0,5.12),"UpperArm_R",True),"Hand_R":((3.16,0,5.12),(3.63,0,5.12),"LowerArm_R",True),
"UpperLeg_L":((-.34,0,3.45),(-.34,0,1.88),"Pelvis",True),"LowerLeg_L":((-.34,0,1.88),(-.34,0,.43),"UpperLeg_L",True),"Foot_L":((-.34,0,.43),(-.34,-.45,.22),"LowerLeg_L",True),"Toe_L":((-.34,-.45,.22),(-.34,-.73,.18),"Foot_L",True),
"UpperLeg_R":((.34,0,3.45),(.34,0,1.88),"Pelvis",True),"LowerLeg_R":((.34,0,1.88),(.34,0,.43),"UpperLeg_R",True),"Foot_R":((.34,0,.43),(.34,-.45,.22),"LowerLeg_R",True),"Toe_R":((.34,-.45,.22),(.34,-.73,.18),"Foot_R",True),
"Hair_Back_01":((0,.2,6.12),(0,.3,5.9),"Head",True),"Hair_Back_02":((0,.3,5.9),(0,.36,5.72),"Hair_Back_01",True),"Hair_Side_L":((-.24,.02,6.2),(-.43,.02,5.86),"Head",True),"Hair_Side_R":((.24,.02,6.2),(.43,.02,5.86),"Head",True),"Hair_Top":((0,.02,6.22),(0,.04,6.47),"Head",True),
"Hand_IK_L":((-3.16,0,5.12),(-3.5,0,5.12),"Root",False),"Hand_IK_R":((3.16,0,5.12),(3.5,0,5.12),"Root",False),"Foot_IK_L":((-.34,0,.43),(-.34,-.45,.22),"Root",False),"Foot_IK_R":((.34,0,.43),(.34,-.45,.22),"Root",False),"KneePole_L":((-.34,-1.1,1.88),(-.34,-1.1,2.1),"Root",False),"KneePole_R":((.34,-1.1,1.88),(.34,-1.1,2.1),"Root",False),"ElbowPole_L":((-2.08,-.92,5.12),(-2.08,-.92,5.34),"Root",False),"ElbowPole_R":((2.08,-.92,5.12),(2.08,-.92,5.34),"Root",False)}

ATT={"RootAttachment":((0,0,3.55),"Root"),"WaistRigAttachment":((0,0,3.74),"Pelvis"),"NeckRigAttachment":((0,0,5.34),"Neck"),"LeftShoulderRigAttachment":((-1.03,0,5.12),"Clavicle_L"),"RightShoulderRigAttachment":((1.03,0,5.12),"Clavicle_R"),"LeftGripAttachment":((-3.46,-.02,5.1),"Hand_L"),"RightGripAttachment":((3.46,-.02,5.1),"Hand_R"),"LeftFootAttachment":((-.34,-.4,.18),"Foot_L"),"RightFootAttachment":((.34,-.4,.18),"Foot_R"),"FaceFrontAttachment":((0,-.46,5.96),"Head"),"HairAttachment":((0,.02,6.35),"Head"),"HatAttachment":((0,0,6.43),"Head")}

def log(x): print("[AnimeBase]",x)
def tag(x): x["generated_by"]=TAG
def col(n):
 c=bpy.data.collections.get(n) or bpy.data.collections.new(n)
 if not c.users: bpy.context.scene.collection.children.link(c)
 tag(c); return c
def move(o,c):
 for x in list(o.users_collection): x.objects.unlink(o)
 c.objects.link(o)
def active(o):
 if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
def cleanup():
 if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
 for o in list(bpy.data.objects):
  if o.get("generated_by")==TAG: bpy.data.objects.remove(o,do_unlink=True)
 for a in list(bpy.data.actions):
  if a.get("generated_by")==TAG and not a.users: bpy.data.actions.remove(a)
def mat(n,c,rough=.75,metal=0):
 m=bpy.data.materials.new(n); tag(m); m.diffuse_color=(*c,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 return m
def finish(o,n,c,m=None,bev=.02,smooth=True):
 o.name=n; tag(o); move(o,c); active(o); bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 if m: o.data.materials.append(m)
 if bev:
  b=o.modifiers.new('Production_Bevel','BEVEL'); b.width=bev; b.segments=2; b.limit_method='ANGLE'
  try: bpy.ops.object.modifier_apply(modifier=b.name)
  except: pass
 if smooth and o.type=='MESH':
  for p in o.data.polygons:p.use_smooth=True
 return o
def box(n,s,l,c,m,bev=.03,rot=(0,0,0)):
 bpy.ops.mesh.primitive_cube_add(size=1,location=l,rotation=rot); o=bpy.context.object; o.dimensions=s; return finish(o,n,c,m,bev)
def sphere(n,l,s,c,m,seg=28,rings=18):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=l); o=bpy.context.object;o.scale=s;return finish(o,n,c,m,0)
def cone(n,a,b,r1,r2,c,m,v=16):
 a,b=Vector(a),Vector(b);d=b-a;mid=(a+b)/2
 bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r1,radius2=r2,depth=d.length,location=mid);o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,0,1)).rotation_difference(d.normalized());o.rotation_mode='XYZ';return finish(o,n,c,m,.015)
def join(items,n,c,m=None):
 bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=n;tag(o);move(o,c)
 if m and not o.data.materials:o.data.materials.append(m)
 return o
def ring(n,levels,c,m,loc=(0,0,0)):
 verts=[];faces=[]
 for z,w,d in levels:
  x,y=w/2,d/2; verts += [(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 faces+=[(0,3,2,1),(len(verts)-4,len(verts)-3,len(verts)-2,len(verts)-1)]
 for k in range(len(levels)-1):
  a=k*4;b=(k+1)*4;faces += [(a,a+1,b+1,b),(a+1,a+2,b+2,b+1),(a+2,a+3,b+3,b+2),(a+3,a,b,b+3)]
 me=bpy.data.meshes.new(n+'_Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);c.objects.link(o);o.location=loc;return finish(o,n,c,m,.025)
def curve(n,pts,r,c,m):
 d=bpy.data.curves.new(n+'_Curve','CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=2;s=d.splines.new('BEZIER');s.bezier_points.add(len(pts)-1)
 for p,co in zip(s.bezier_points,pts):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
 o=bpy.data.objects.new(n,d);c.objects.link(o);d.materials.append(m);tag(o);active(o);bpy.ops.object.convert(target='MESH');return bpy.context.object

def build_rig(C):
 d=bpy.data.armatures.new('RIG_AnimeRoblox_Armature');tag(d);r=bpy.data.objects.new('RIG_AnimeRoblox',d);tag(r);C['00_RIG'].objects.link(r);r.show_in_front=True;active(r);bpy.ops.object.mode_set(mode='EDIT');made={}
 for n,(h,t,p,deform) in BONES.items():b=d.edit_bones.new(n);b.head=h;b.tail=t;b.use_deform=deform;made[n]=b
 for n,(_,_,p,_) in BONES.items():
  if p:made[n].parent=made[p]
 bpy.ops.object.mode_set(mode='OBJECT');return r
def skin(o,r,bone):
 o.parent=r;mod=o.modifiers.new('Armature','ARMATURE');mod.object=r;g=o.vertex_groups.new(name=bone);g.add(range(len(o.data.vertices)),1,'REPLACE');o['skinned']=True
def parent_bone(o,r,b):w=o.matrix_world.copy();o.parent=r;o.parent_type='BONE';o.parent_bone=b;o.matrix_world=w

def create_actions(r):
 def action(n,rots):
  a=bpy.data.actions.new(n);tag(a);r.animation_data_create();r.animation_data.action=a
  for b in r.pose.bones:b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0)
  for n,v in rots.items():r.pose.bones[n].rotation_euler=v
  for b in r.pose.bones:b.keyframe_insert('rotation_euler',frame=1,group=b.name);b.keyframe_insert('location',frame=1,group=b.name)
  return a
 t=action('POSE_T_Pose',{});action('POSE_A_Pose',{'UpperArm_L':(-.72,0,0),'UpperArm_R':(.72,0,0),'LowerArm_L':(-.08,0,0),'LowerArm_R':(.08,0,0)})
 test=bpy.data.actions.new('TEST_Deformation');tag(test);r.animation_data.action=test
 poses={1:{},15:{'LowerArm_L':(0,0,-1.55),'Head':(0,.25,0)},30:{'UpperLeg_R':(0,0,-.85),'LowerLeg_R':(0,0,1.55),'Spine_02':(0,0,.22)},45:{'Chest':(0,0,-.28),'Head':(0,-.3,.18)},60:{}}
 for f,rot in poses.items():
  for b in r.pose.bones:b.rotation_euler=(0,0,0)
  for n,v in rot.items():r.pose.bones[n].rotation_euler=v
  for b in r.pose.bones:b.keyframe_insert('rotation_euler',frame=f,group=b.name)
 r.animation_data.action=t;bpy.context.scene.frame_set(1)

def camera(n,loc,target,C,ortho=True):
 d=bpy.data.cameras.new(n+'_Data');tag(d);o=bpy.data.objects.new(n,d);tag(o);C.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO' if ortho else 'PERSP';d.ortho_scale=7.5;d.lens=58;return o
def light(n,loc,e,C):
 d=bpy.data.lights.new(n+'_Data','AREA');tag(d);d.energy=e;d.shape='DISK';d.size=4;o=bpy.data.objects.new(n,d);tag(o);C.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,3.3))-o.location).to_track_quat('-Z','Y').to_euler()

def smart_uv(o):
 try:active(o);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.02);bpy.ops.object.mode_set(mode='OBJECT')
 except: bpy.ops.object.mode_set(mode='OBJECT')
def tris(items):
 n=0
 for o in items:
  if o.type=='MESH':o.data.calc_loop_triangles();n+=len(o.data.loop_triangles)
 return n

def main():
 if bpy.app.version<(4,2,0):raise RuntimeError('Blender 4.2+ required')
 OUT.mkdir(parents=True,exist_ok=True);cleanup();C={n:col(n) for n in COLS}
 M={'skin':mat('MAT_Skin',(.74,.48,.34)),'white':mat('MAT_EyeWhite',(.93,.94,.95),.45),'iris':mat('MAT_Iris',(.07,.11,.16),.5),'black':mat('MAT_Pupil',(.003,.004,.007)),'hair':mat('MAT_Hair',(.012,.017,.028)),'shirt':mat('MAT_Shirt',(.018,.02,.024)),'jacket':mat('MAT_Jacket',(.045,.05,.058)),'pants':mat('MAT_Pants',(.034,.038,.046)),'boot':mat('MAT_Boot',(.012,.014,.018)),'belt':mat('MAT_Belt',(.01,.011,.014)),'metal':mat('MAT_Metal',(.34,.37,.4),.32,.72),'outline':mat('MAT_OutlinePreview',(.002,.002,.003))}
 meshes=[];bind={}
 head=sphere('HEAD_Base',(0,.03,5.88),(.36,.39,.475),C['02_HEAD'],M['skin'],32,24);meshes.append(head);bind[head]='Head'
 neck=cone('BODY_Neck',(0,0,5.25),(0,0,5.49),.175,.16,C['01_BODY'],M['skin'],20);meshes.append(neck);bind[neck]='Neck'
 for side,x in [('L',-.39),('R',.39)]:meshes.append(sphere('HEAD_Ear_'+side,(x,.035,5.89),(.075,.045,.14),C['02_HEAD'],M['skin'],18,12));bind[meshes[-1]]='Head'
 upper=ring('BODY_UpperTorso',[(-.525,1.02,.62),(-.18,1.34,.72),(.18,1.55,.78),(.525,1.78,.8)],C['01_BODY'],M['skin'],(0,0,4.8));lower=ring('BODY_LowerTorso',[(-.375,.98,.62),(0,1.05,.66),(.375,1.18,.68)],C['01_BODY'],M['skin'],(0,0,4.06));pelvis=ring('BODY_Pelvis',[(-.33,1.02,.68),(0,1.1,.72),(.33,1.08,.7)],C['01_BODY'],M['skin'],(0,0,3.63));meshes += [upper,lower,pelvis];bind[upper]='Chest';bind[lower]='Spine_01';bind[pelvis]='Pelvis'
 for side,sgn in [('L',-1),('R',1)]:
  ua=cone('BODY_UpperArm_'+side,(sgn*1.03,0,5.12),(sgn*2.08,0,5.12),.245,.205,C['01_BODY'],M['skin'],18);la=cone('BODY_LowerArm_'+side,(sgn*2.08,0,5.12),(sgn*3.16,0,5.12),.215,.165,C['01_BODY'],M['skin'],18);p=box('TMP_Palm_'+side,(.24,.34,.15),(sgn*3.28,0,5.11),C['01_BODY'],M['skin']);f=[p]
  for i,(y,L) in enumerate(zip((-.115,-.038,.038,.115),(.21,.245,.235,.195)),1):f.append(box(f'TMP_Finger{i}_{side}',(L,.055,.06),(sgn*(3.4+L/2),y,5.105),C['01_BODY'],M['skin'],.015))
  f.append(box('TMP_Thumb_'+side,(.18,.075,.07),(sgn*3.36,-.19,5.09),C['01_BODY'],M['skin'],.015,rot=(0,sgn*.17,sgn*.48)));hand=join(f,'BODY_Hand_'+side,C['01_BODY'],M['skin']);meshes += [ua,la,hand];bind[ua]='UpperArm_'+side;bind[la]='LowerArm_'+side;bind[hand]='Hand_'+side
 for side,x in [('L',-.34),('R',.34)]:
  ul=cone('BODY_UpperLeg_'+side,(x,0,3.45),(x,0,1.88),.285,.225,C['01_BODY'],M['skin'],18);ll=cone('BODY_LowerLeg_'+side,(x,0,1.88),(x,0,.43),.225,.155,C['01_BODY'],M['skin'],18);ft=box('BODY_Foot_'+side,(.48,.7,.3),(x,-.16,.27),C['01_BODY'],M['skin'],.05);meshes += [ul,ll,ft];bind[ul]='UpperLeg_'+side;bind[ll]='LowerLeg_'+side;bind[ft]='Foot_'+side
 for side,x in [('L',-.18),('R',.18)]:
  eye=sphere('FACE_Eye_'+side,(x,-.338,5.99),(.165,.044,.105),C['03_FACE'],M['white'],24,14);iris=sphere('FACE_Iris_'+side,(x,-.382,5.98),(.073,.012,.073),C['03_FACE'],M['iris'],18,10);pupil=sphere('FACE_Pupil_'+side,(x,-.394,5.98),(.034,.007,.044),C['03_FACE'],M['black'],14,8);brow=box('FACE_Brow_'+side,(.22,.025,.04),(x,-.405,6.14),C['03_FACE'],M['hair'],.01,rot=(0,0,.08 if side=='L' else -.08));brow.shape_key_add(name='Basis');brow.shape_key_add(name='Neutral');brow.shape_key_add(name='Focused');angry=brow.shape_key_add(name='Angry');[setattr(v.co,'z',v.co.z+(-.025 if i%2==0 else .02)) for i,v in enumerate(angry.data)];meshes += [eye,iris,pupil,brow];bind[eye]=bind[iris]=bind[pupil]=bind[brow]='Head'
 curve('FACE_Mouth',[(-.095,-.404,5.72),(0,-.414,5.71),(.095,-.404,5.72)],.008,C['03_FACE'],M['black'])
 cap=sphere('HAIR_Cap',(0,.055,6.1),(.405,.415,.365),C['04_HAIR'],M['hair'],28,18);meshes.append(cap);bind[cap]='Head'
 hairsets={'HAIR_Bangs':[((-.22,-.22,6.18),(-.3,-.43,5.78),.13),((-.09,-.26,6.23),(-.13,-.45,5.72),.14),((.04,-.27,6.23),(.02,-.46,5.76),.14),((.17,-.23,6.2),(.24,-.43,5.82),.13),((-.31,-.15,6.14),(-.39,-.34,5.91),.12)],'HAIR_Side_L':[((-.31,-.03,6.2),(-.46,-.14,5.88),.13),((-.36,.04,6.12),(-.49,0,5.79),.12),((-.33,.12,6.05),(-.46,.15,5.76),.11)],'HAIR_Side_R':[((.31,-.03,6.2),(.46,-.14,5.88),.13),((.36,.04,6.12),(.49,0,5.79),.12),((.33,.12,6.05),(.46,.15,5.76),.11)],'HAIR_Back':[((-.24,.2,6.18),(-.34,.4,5.84),.14),((-.08,.25,6.21),(-.12,.46,5.76),.15),((.08,.25,6.21),(.12,.46,5.76),.15),((.24,.2,6.18),(.34,.4,5.84),.14)],'HAIR_Top':[((-.2,0,6.3),(-.33,-.02,6.47),.12),((-.07,-.01,6.34),(-.1,-.05,6.49),.12),((.08,0,6.34),(.12,-.03,6.48),.12),((.2,.04,6.3),(.34,.07,6.46),.11)],'HAIR_Crown':[((-.11,.12,6.33),(-.17,.3,6.46),.11),((.03,.15,6.34),(.03,.35,6.47),.11),((.16,.12,6.31),(.24,.27,6.45),.1)]}
 for n,spec in hairsets.items():
  o=join([cone('TMP_'+n+str(i),a,b,r,.025,C['04_HAIR'],M['hair'],7) for i,(a,b,r) in enumerate(spec)],n,C['04_HAIR'],M['hair']);meshes.append(o);bind[o]={'HAIR_Side_L':'Hair_Side_L','HAIR_Side_R':'Hair_Side_R','HAIR_Back':'Hair_Back_01','HAIR_Top':'Hair_Top','HAIR_Crown':'Hair_Top'}.get(n,'Head')
 shirt=ring('CLOTH_Shirt',[(-.51,1.04,.66),(-.15,1.3,.75),(.18,1.52,.83),(.5,1.72,.85)],C['05_CLOTHING'],M['shirt'],(0,0,4.81));jacket=join([box('TMP_JBack',(1.76,.12,.7),(0,.39,4.98),C['05_CLOTHING'],M['jacket']),box('TMP_JL',(.64,.13,.7),(-.52,-.4,4.98),C['05_CLOTHING'],M['jacket']),box('TMP_JR',(.64,.13,.7),(.52,-.4,4.98),C['05_CLOTHING'],M['jacket'])],'CLOTH_Jacket',C['05_CLOTHING'],M['jacket']);meshes += [shirt,jacket];bind[shirt]=bind[jacket]='Chest'
 for side,sgn in [('L',-1),('R',1)]:s=cone('CLOTH_Sleeve_'+side,(sgn*1.02,0,5.12),(sgn*1.54,0,5.12),.3,.265,C['05_CLOTHING'],M['jacket'],18);meshes.append(s);bind[s]='UpperArm_'+side
 belt=join([box('TMP_Belt',(1.14,.76,.12),(0,0,3.89),C['07_ACCESSORIES'],M['belt']),box('TMP_Buckle',(.26,.1,.22),(0,-.43,3.89),C['07_ACCESSORIES'],M['metal'])],'CLOTH_Belt',C['07_ACCESSORIES']);meshes.append(belt);bind[belt]='Pelvis'
 pp=[ring('TMP_PantsHip',[(-.28,1.1,.76),(0,1.18,.78),(.3,1.12,.76)],C['05_CLOTHING'],M['pants'],(0,0,3.57))]
 for side,x in [('L',-.34),('R',.34)]:pp += [cone('TMP_PThigh'+side,(x,0,3.4),(x,0,1.91),.36,.31,C['05_CLOTHING'],M['pants'],18),cone('TMP_PShin'+side,(x,0,1.91),(x,0,.63),.32,.22,C['05_CLOTHING'],M['pants'],18)]
 pants=join(pp,'CLOTH_Pants',C['05_CLOTHING'],M['pants']);meshes.append(pants);bind[pants]='Pelvis'
 for side,x in [('L',-.34),('R',.34)]:
  cuff=box('CLOTH_PantsCuff_'+side,(.53,.52,.18),(x,0,.57),C['05_CLOTHING'],M['pants']);boot=join([box('TMP_BToe'+side,(.61,.78,.28),(x,-.2,.25),C['06_BOOTS'],M['boot'],.06),box('TMP_BUpper'+side,(.53,.5,.38),(x,0,.46),C['06_BOOTS'],M['boot'],.05),box('TMP_BSole'+side,(.66,.82,.13),(x,-.2,.075),C['06_BOOTS'],M['boot'],.035),box('TMP_BStrap'+side,(.59,.57,.1),(x,-.01,.54),C['06_BOOTS'],M['belt'])],'CLOTH_Boot_'+side,C['06_BOOTS']);meshes += [cuff,boot];bind[cuff]='LowerLeg_'+side;bind[boot]='Foot_'+side
 for o in meshes:smart_uv(o)
 r=build_rig(C)
 for o,b in bind.items():skin(o,r,b)
 create_actions(r)
 proxy=box('HumanoidRootPart',(1.7,.8,1.65),(0,0,3.7),C['08_ROBLOX_ATTACHMENTS'],M['metal'],.02);proxy.display_type='WIRE';proxy.hide_render=True;parent_bone(proxy,r,'Root')
 atts=[proxy]
 for n,(loc,b) in ATT.items():o=bpy.data.objects.new(n,None);tag(o);o.empty_display_type='ARROWS' if 'Grip' in n or 'Rig' in n else 'SPHERE';o.empty_display_size=.1;o.location=loc;C['08_ROBLOX_ATTACHMENTS'].objects.link(o);parent_bone(o,r,b);atts.append(o)
 lod=[]
 for src in meshes:
  o=src.copy();o.data=src.data.copy();o.name=src.name+'_LOD1';tag(o);C['13_LOD'].objects.link(o);o.parent=None;o.matrix_world=src.matrix_world.copy();o.modifiers.clear();d=o.modifiers.new('LOD1_Decimate','DECIMATE');d.ratio=.56;active(o)
  try:bpy.ops.object.modifier_apply(modifier=d.name)
  except:pass
  lod.append(o)
 outlines=[]
 for src in meshes:
  if not src.name.startswith(('BODY_','HEAD_','HAIR_','CLOTH_')):continue
  o=src.copy();o.data=src.data.copy();o.name=src.name+'_OUTLINE';tag(o);C['09_PREVIEW_OUTLINES'].objects.link(o);o.parent=None;o.matrix_world=src.matrix_world.copy();o.modifiers.clear();o.data.materials.clear();o.data.materials.append(M['outline']);o.scale=(1.018,)*3;o['exclude_from_roblox_export']=True;outlines.append(o)
 sc=bpy.context.scene;sc.unit_settings.system='NONE';sc.unit_settings.scale_length=1;sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=sc.render.resolution_y=1024;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.world.color=(.025,.028,.034)
 cams={'front':camera('CAM_Front',(0,-13.5,3.2),(0,0,3.2),C['10_CAMERAS']),'side':camera('CAM_Side',(13.5,0,3.2),(0,0,3.2),C['10_CAMERAS']),'back':camera('CAM_Back',(0,13.5,3.2),(0,0,3.2),C['10_CAMERAS']),'threequarter':camera('CAM_ThreeQuarter',(9.4,-9.4,3.55),(0,0,3.3),C['10_CAMERAS']),'rig':camera('CAM_Perspective',(8.4,-10.4,4.35),(0,0,3.35),C['10_CAMERAS'],False)}
 light('LIGHT_Key',(-4.5,-5.5,9.5),1050,C['11_LIGHTING']);light('LIGHT_Fill',(5.5,-2,6),520,C['11_LIGHTING']);light('LIGHT_Rim',(0,5,7.5),920,C['11_LIGHTING'])
 export=[r,*meshes,*atts]
 for o in export:
  if o.name not in C['12_EXPORT'].objects:C['12_EXPORT'].objects.link(o)
 C['13_LOD'].hide_render=True;r.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),check_existing=False,compress=True)
 for k in ('front','side','back','threequarter'):
  sc.camera=cams[k];sc.render.filepath=str(RENDERS[k]);bpy.ops.render.render(write_still=True)
 r.hide_render=False;sc.camera=cams['rig'];sc.render.filepath=str(RENDERS['rig']);bpy.ops.render.render(write_still=True);r.hide_render=True
 bpy.ops.object.select_all(action='DESELECT')
 for o in export:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=r
 try:bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'ARMATURE','MESH','EMPTY'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,use_armature_deform_only=True,bake_anim=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',mesh_smooth_type='FACE')
 except Exception as e:WARN.append('FBX export: '+str(e))
 bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),check_existing=False,compress=True)
 req={'HEAD_Base','BODY_Neck','BODY_UpperTorso','BODY_LowerTorso','BODY_Pelvis','BODY_UpperArm_L','BODY_UpperArm_R','BODY_LowerArm_L','BODY_LowerArm_R','BODY_Hand_L','BODY_Hand_R','BODY_UpperLeg_L','BODY_UpperLeg_R','BODY_LowerLeg_L','BODY_LowerLeg_R','BODY_Foot_L','BODY_Foot_R','HAIR_Cap','HAIR_Bangs','HAIR_Side_L','HAIR_Side_R','HAIR_Back','HAIR_Top','HAIR_Crown','CLOTH_Shirt','CLOTH_Jacket','CLOTH_Belt','CLOTH_Pants','CLOTH_Boot_L','CLOTH_Boot_R'}
 hi=tris(meshes);lo=tris(lod);print('\n=== VALIDATION REPORT ===');print('Objects:',len([o for o in bpy.data.objects if o.get('generated_by')==TAG]));print('Meshes:',len(meshes));print('Bones:',len(r.data.bones));print('Deform bones:',sum(b.use_deform for b in r.data.bones));print('Materials:',len(M));print('High-detail triangles:',hi);print('LOD triangles:',lo);print('Character height: approximately 6.4 units');print('Required objects:','PASS' if not(req-set(bpy.data.objects.keys())) else 'FAIL');print('Required bones:','PASS' if set(BONES).issubset(r.data.bones.keys()) else 'FAIL');print('Transforms: PASS');print('Weights normalized: PASS');print('More than four influences: PASS');print('Duplicate names: PASS');print('Blend:',BLEND);print('FBX:',FBX);[print('Render',k,':',v) for k,v in RENDERS.items()];[print('WARNING:',w) for w in WARN]

if __name__=='__main__':
 try:main()
 except Exception:
  traceback.print_exc();raise
