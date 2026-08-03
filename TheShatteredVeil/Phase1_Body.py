from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Vector


OUTPUT_DIR = Path(os.environ.get("SHATTERED_VEIL_OUTPUT", Path.cwd() / "TheShatteredVeil"))
PROGRESS_DIR = OUTPUT_DIR / "Progress"

BODY_MATERIAL_NAME = "MAT_Body_Neutral"
FLOOR_MATERIAL_NAME = "MAT_Floor_Neutral"


def clean_scene() -> None:
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.armatures,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

    for collection in list(bpy.data.collections):
        if collection.name != "Collection" and collection.users == 0:
            bpy.data.collections.remove(collection)


def ensure_collection(name: str) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection


def link_only(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    collection.objects.link(obj)


def create_material(name: str, color: tuple[float, float, float, float], roughness: float = 0.7) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = 0.0
    return material


def add_modifier_stack(obj: bpy.types.Object, subdivision: int = 1, bevel: float = 0.0) -> None:
    if bevel > 0.0:
        modifier = obj.modifiers.new("Bevel", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        modifier.limit_method = "ANGLE"
    if subdivision > 0:
        modifier = obj.modifiers.new("Subdivision", "SUBSURF")
        modifier.levels = subdivision
        modifier.render_levels = subdivision
        modifier.subdivision_type = "CATMULL_CLARK"


def finish_mesh(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    subdivision: int = 1,
    bevel: float = 0.0,
) -> bpy.types.Object:
    link_only(obj, collection)
    obj.data.materials.append(material)
    add_modifier_stack(obj, subdivision=subdivision, bevel=bevel)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def create_ring_body(
    name: str,
    rings: Sequence[tuple[float, float, float, float]],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    segments: int = 24,
    subdivision: int = 2,
) -> bpy.types.Object:
    """Create a smooth closed anatomical mass from elliptical horizontal rings.

    Each ring is (z, half_width_x, half_depth_y, center_y_offset).
    """
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    for z, radius_x, radius_y, center_y in rings:
        for index in range(segments):
            angle = (index / segments) * math.tau
            x = math.cos(angle) * radius_x
            y = center_y + math.sin(angle) * radius_y
            vertices.append((x, y, z))

    for ring_index in range(len(rings) - 1):
        start = ring_index * segments
        next_start = (ring_index + 1) * segments
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append((
                start + index,
                start + next_index,
                next_start + next_index,
                next_start + index,
            ))

    bottom_center = len(vertices)
    bottom_z, _, _, bottom_y = rings[0]
    vertices.append((0.0, bottom_y, bottom_z))
    top_center = len(vertices)
    top_z, _, _, top_y = rings[-1]
    vertices.append((0.0, top_y, top_z))

    for index in range(segments):
        next_index = (index + 1) % segments
        faces.append((bottom_center, next_index, index))
        top_start = (len(rings) - 1) * segments
        faces.append((top_center, top_start + index, top_start + next_index))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, collection, material, subdivision=subdivision)


def create_tube(
    name: str,
    centers: Sequence[Vector],
    radii: Sequence[tuple[float, float]],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    segments: int = 18,
    subdivision: int = 1,
) -> bpy.types.Object:
    if len(centers) != len(radii):
        raise ValueError("centers and radii must have the same length")

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []

    for index, center in enumerate(centers):
        if index == 0:
            tangent = (centers[1] - center).normalized()
        elif index == len(centers) - 1:
            tangent = (center - centers[index - 1]).normalized()
        else:
            tangent = (centers[index + 1] - centers[index - 1]).normalized()

        front = Vector((0.0, 1.0, 0.0))
        front = front - tangent * front.dot(tangent)
        if front.length < 1e-5:
            front = Vector((1.0, 0.0, 0.0))
            front = front - tangent * front.dot(tangent)
        front.normalize()
        side = tangent.cross(front).normalized()

        side_radius, front_radius = radii[index]
        for segment_index in range(segments):
            angle = (segment_index / segments) * math.tau
            point = (
                center
                + side * (math.cos(angle) * side_radius)
                + front * (math.sin(angle) * front_radius)
            )
            vertices.append(tuple(point))

    for ring_index in range(len(centers) - 1):
        start = ring_index * segments
        next_start = (ring_index + 1) * segments
        for segment_index in range(segments):
            next_index = (segment_index + 1) % segments
            faces.append((
                start + segment_index,
                start + next_index,
                next_start + next_index,
                next_start + segment_index,
            ))

    bottom_center = len(vertices)
    vertices.append(tuple(centers[0]))
    top_center = len(vertices)
    vertices.append(tuple(centers[-1]))
    for segment_index in range(segments):
        next_index = (segment_index + 1) % segments
        faces.append((bottom_center, next_index, segment_index))
        top_start = (len(centers) - 1) * segments
        faces.append((top_center, top_start + segment_index, top_start + next_index))

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, collection, material, subdivision=subdivision)


def create_rounded_mass(
    name: str,
    location: Vector,
    scale: tuple[float, float, float],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    subdivision: int = 2,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish_mesh(obj, collection, material, subdivision=subdivision)


def create_foot(
    name: str,
    x_center: float,
    y_center: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> bpy.types.Object:
    slices = [
        (y_center + 0.10, 0.065, 0.035, 0.145),
        (y_center - 0.02, 0.090, 0.030, 0.135),
        (y_center - 0.20, 0.075, 0.025, 0.095),
    ]
    vertices: list[tuple[float, float, float]] = []
    for y, half_width, bottom_z, top_z in slices:
        vertices.extend([
            (x_center - half_width, y, bottom_z),
            (x_center + half_width, y, bottom_z),
            (x_center + half_width, y, top_z),
            (x_center - half_width, y, top_z),
        ])

    faces = [
        (0, 1, 2, 3),
        (8, 11, 10, 9),
    ]
    for slice_index in range(len(slices) - 1):
        a = slice_index * 4
        b = (slice_index + 1) * 4
        faces.extend([
            (a + 0, b + 0, b + 1, a + 1),
            (a + 1, b + 1, b + 2, a + 2),
            (a + 2, b + 2, b + 3, a + 3),
            (a + 3, b + 3, b + 0, a + 0),
        ])

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return finish_mesh(obj, collection, material, subdivision=2, bevel=0.012)


def make_hand(
    side_name: str,
    wrist: Vector,
    hand_end: Vector,
    outward_sign: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
) -> list[bpy.types.Object]:
    direction = (hand_end - wrist).normalized()
    front = Vector((0.0, 1.0, 0.0))
    front = front - direction * front.dot(direction)
    if front.length < 1e-5:
        front = Vector((0.0, 0.0, 1.0))
    front.normalize()
    side = direction.cross(front).normalized()

    palm_center = wrist.lerp(hand_end, 0.55)
    palm = create_tube(
        f"{side_name}_Hand_Palm",
        [wrist, palm_center, hand_end],
        [(0.055, 0.032), (0.072, 0.038), (0.062, 0.030)],
        collection,
        material,
        segments=16,
        subdivision=1,
    )
    objects = [palm]

    finger_lengths = [0.075, 0.085, 0.080, 0.067]
    offsets = [-0.030, -0.010, 0.011, 0.031]
    for finger_index, (offset, length) in enumerate(zip(offsets, finger_lengths), start=1):
        base = hand_end + side * offset
        mid = base + direction * (length * 0.55) - front * 0.006
        tip = base + direction * length - front * 0.014
        finger = create_tube(
            f"{side_name}_Hand_Finger_{finger_index:02d}",
            [base, mid, tip],
            [(0.012, 0.011), (0.011, 0.010), (0.007, 0.007)],
            collection,
            material,
            segments=12,
            subdivision=1,
        )
        objects.append(finger)

    thumb_base = palm_center + side * (0.060 * outward_sign) - front * 0.008
    thumb_mid = thumb_base + side * (0.035 * outward_sign) + direction * 0.025
    thumb_tip = thumb_mid + direction * 0.035 - front * 0.005
    thumb = create_tube(
        f"{side_name}_Hand_Thumb",
        [thumb_base, thumb_mid, thumb_tip],
        [(0.015, 0.014), (0.013, 0.012), (0.008, 0.008)],
        collection,
        material,
        segments=12,
        subdivision=1,
    )
    objects.append(thumb)
    return objects


def create_body(collection: bpy.types.Collection, material: bpy.types.Material) -> list[bpy.types.Object]:
    objects: list[bpy.types.Object] = []

    torso = create_ring_body(
        "Body_Torso",
        [
            (1.10, 0.195, 0.145, 0.000),
            (1.20, 0.180, 0.140, -0.004),
            (1.32, 0.205, 0.160, -0.008),
            (1.46, 0.255, 0.185, -0.012),
            (1.59, 0.305, 0.190, -0.010),
            (1.69, 0.275, 0.165, -0.004),
        ],
        collection,
        material,
        subdivision=2,
    )
    objects.append(torso)

    pelvis = create_ring_body(
        "Body_Pelvis",
        [
            (0.91, 0.175, 0.145, 0.005),
            (0.98, 0.215, 0.170, 0.000),
            (1.07, 0.225, 0.175, 0.000),
            (1.14, 0.200, 0.155, 0.000),
        ],
        collection,
        material,
        subdivision=2,
    )
    objects.append(pelvis)

    neck = create_tube(
        "Body_Neck",
        [Vector((0.0, 0.0, 1.66)), Vector((0.0, -0.004, 1.74)), Vector((0.0, -0.008, 1.81))],
        [(0.100, 0.090), (0.088, 0.082), (0.095, 0.090)],
        collection,
        material,
        segments=20,
        subdivision=1,
    )
    objects.append(neck)

    head = create_ring_body(
        "Body_Head_ProportionReference",
        [
            (1.78, 0.085, 0.090, -0.008),
            (1.83, 0.110, 0.105, -0.012),
            (1.90, 0.135, 0.128, -0.010),
            (2.00, 0.145, 0.138, -0.004),
            (2.09, 0.125, 0.122, 0.000),
            (2.14, 0.075, 0.072, 0.000),
        ],
        collection,
        material,
        subdivision=2,
    )
    objects.append(head)

    for side_name, sign in (("Left", -1.0), ("Right", 1.0)):
        shoulder_center = Vector((0.315 * sign, 0.0, 1.625))
        deltoid = create_rounded_mass(
            f"Body_{side_name}_Shoulder",
            shoulder_center,
            (0.125, 0.145, 0.145),
            collection,
            material,
            subdivision=1,
        )
        objects.append(deltoid)

        elbow = Vector((0.515 * sign, -0.005, 1.405))
        wrist = Vector((0.675 * sign, -0.010, 1.205))
        hand_end = Vector((0.755 * sign, -0.015, 1.095))

        upper_arm = create_tube(
            f"Body_{side_name}_UpperArm",
            [
                Vector((0.300 * sign, 0.0, 1.615)),
                Vector((0.390 * sign, -0.004, 1.535)),
                elbow,
            ],
            [(0.105, 0.110), (0.115, 0.105), (0.082, 0.078)],
            collection,
            material,
            segments=18,
            subdivision=1,
        )
        objects.append(upper_arm)

        elbow_mass = create_rounded_mass(
            f"Body_{side_name}_Elbow",
            elbow,
            (0.082, 0.077, 0.078),
            collection,
            material,
            subdivision=1,
        )
        objects.append(elbow_mass)

        forearm = create_tube(
            f"Body_{side_name}_Forearm",
            [
                elbow,
                Vector((0.595 * sign, -0.008, 1.315)),
                wrist,
            ],
            [(0.080, 0.075), (0.090, 0.075), (0.052, 0.048)],
            collection,
            material,
            segments=18,
            subdivision=1,
        )
        objects.append(forearm)

        objects.extend(make_hand(side_name, wrist, hand_end, sign, collection, material))

        hip = Vector((0.145 * sign, 0.0, 0.995))
        knee = Vector((0.160 * sign, -0.010, 0.585))
        ankle = Vector((0.170 * sign, 0.005, 0.170))

        thigh = create_tube(
            f"Body_{side_name}_Thigh",
            [
                hip,
                Vector((0.155 * sign, 0.000, 0.835)),
                knee,
            ],
            [(0.130, 0.135), (0.145, 0.145), (0.092, 0.090)],
            collection,
            material,
            segments=20,
            subdivision=1,
        )
        objects.append(thigh)

        knee_mass = create_rounded_mass(
            f"Body_{side_name}_Knee",
            knee,
            (0.090, 0.085, 0.085),
            collection,
            material,
            subdivision=1,
        )
        objects.append(knee_mass)

        calf = create_tube(
            f"Body_{side_name}_LowerLeg",
            [
                knee,
                Vector((0.165 * sign, 0.020, 0.405)),
                ankle,
            ],
            [(0.088, 0.082), (0.108, 0.095), (0.060, 0.057)],
            collection,
            material,
            segments=20,
            subdivision=1,
        )
        objects.append(calf)

        ankle_mass = create_rounded_mass(
            f"Body_{side_name}_Ankle",
            ankle,
            (0.060, 0.060, 0.070),
            collection,
            material,
            subdivision=1,
        )
        objects.append(ankle_mass)

        foot = create_foot(
            f"Body_{side_name}_Foot",
            x_center=0.170 * sign,
            y_center=-0.005 if side_name == "Left" else 0.015,
            collection=collection,
            material=material,
        )
        objects.append(foot)

    return objects


def create_ground(collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0.0, 0.0, 0.0))
    floor = bpy.context.object
    floor.name = "Neutral_Ground_Plane"
    link_only(floor, collection)
    floor.data.materials.append(material)
    return floor


def look_at(obj: bpy.types.Object, target: Vector) -> None:
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def create_camera(
    name: str,
    location: tuple[float, float, float],
    target: Vector,
    collection: bpy.types.Collection,
    ortho_scale: float,
) -> bpy.types.Object:
    camera_data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, camera_data)
    collection.objects.link(camera)
    camera.location = location
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = ortho_scale
    camera_data.lens = 55
    look_at(camera, target)
    return camera


def create_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    collection: bpy.types.Collection,
    target: Vector,
) -> bpy.types.Object:
    light_data = bpy.data.lights.new(name, "AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size
    light = bpy.data.objects.new(name, light_data)
    collection.objects.link(light)
    light.location = location
    look_at(light, target)
    return light


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "EEVEE_NEXT") else "BLENDER_EEVEE"

    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"

    scene.world.color = (0.055, 0.055, 0.060)
    scene.view_settings.look = "AgX - Medium High Contrast"

    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0


def evaluated_triangle_count(objects: Iterable[bpy.types.Object]) -> int:
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        total += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    return total


def render_camera(camera: bpy.types.Object, filepath: Path) -> None:
    scene = bpy.context.scene
    scene.camera = camera
    scene.render.filepath = str(filepath)
    bpy.ops.render.render(write_still=True)


def export_progress_glb(body_objects: Sequence[bpy.types.Object], filepath: Path) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in body_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = body_objects[0]
    bpy.ops.export_scene.gltf(
        filepath=str(filepath),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
    )
    bpy.ops.object.select_all(action="DESELECT")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    clean_scene()
    configure_scene()

    body_collection = ensure_collection("BODY_PHASE_1")
    ground_collection = ensure_collection("GROUND_NEUTRAL")
    lighting_collection = ensure_collection("LIGHTING_NEUTRAL")
    camera_collection = ensure_collection("CAMERAS_PROGRESS")

    body_material = create_material(BODY_MATERIAL_NAME, (0.32, 0.30, 0.29, 1.0), roughness=0.78)
    floor_material = create_material(FLOOR_MATERIAL_NAME, (0.18, 0.19, 0.21, 1.0), roughness=0.92)

    root = bpy.data.objects.new("CursedNinja_Phase1_Root", None)
    body_collection.objects.link(root)

    body_objects = create_body(body_collection, body_material)
    for obj in body_objects:
        obj.parent = root

    create_ground(ground_collection, floor_material)

    target = Vector((0.0, 0.0, 1.08))
    create_area_light("Neutral_Key", (3.4, -4.2, 4.8), 1150.0, 4.0, lighting_collection, target)
    create_area_light("Neutral_Fill", (-3.0, -2.2, 3.2), 650.0, 3.5, lighting_collection, target)
    create_area_light("Neutral_Top", (0.0, 1.6, 5.0), 800.0, 3.0, lighting_collection, target)

    front_camera = create_camera(
        "Camera_Phase1_Front",
        (0.0, -6.0, 1.10),
        target,
        camera_collection,
        ortho_scale=2.38,
    )
    side_camera = create_camera(
        "Camera_Phase1_Side",
        (5.5, 0.0, 1.10),
        target,
        camera_collection,
        ortho_scale=2.38,
    )

    front_path = PROGRESS_DIR / "Phase1_Body_Front.png"
    side_path = PROGRESS_DIR / "Phase1_Body_Side.png"
    blend_path = PROGRESS_DIR / "Phase1_Body.blend"
    glb_path = PROGRESS_DIR / "Phase1_Body.glb"
    report_path = PROGRESS_DIR / "Phase1_Report.json"

    render_camera(front_camera, front_path)
    render_camera(side_camera, side_path)
    export_progress_glb(body_objects, glb_path)

    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    triangle_count = evaluated_triangle_count(body_objects)
    report = {
        "character": "The Shattered Veil",
        "phase": 1,
        "phase_name": "Body proportions and anatomy",
        "status": "awaiting visual approval",
        "height_meters": 2.14,
        "target_heads_tall": 7.6,
        "body_mesh_objects": len(body_objects),
        "evaluated_triangles": triangle_count,
        "outputs": [
            str(front_path.relative_to(OUTPUT_DIR)),
            str(side_path.relative_to(OUTPUT_DIR)),
            str(blend_path.relative_to(OUTPUT_DIR)),
            str(glb_path.relative_to(OUTPUT_DIR)),
        ],
        "not_included_yet": [
            "final head and face concealment",
            "hair",
            "clothing",
            "weapons",
            "materials beyond neutral body review",
            "rigging",
            "VFX",
        ],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("PHASE 1 COMPLETE")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
