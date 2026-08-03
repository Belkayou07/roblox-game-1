"""Clean Blender's startup scene, then run the generated character builder.

The first local build left Blender's default Cube in place. That cube buried the
lower half of the character and dominated every preview render. This wrapper is
run inside a dedicated background Blender process, so clearing the full startup
scene is safe and intentional.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import bpy


def clear_startup_scene() -> None:
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    # Remove orphan startup datablocks so they cannot be re-linked later.
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.armatures,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)


def load_generator(path: Path):
    spec = importlib.util.spec_from_file_location("shattered_veil_generator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load generator: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    generator = repo_root / "TheShatteredVeil" / "BlenderGenerateAsset.py"
    if not generator.exists():
        raise FileNotFoundError(f"Missing generator: {generator}")

    clear_startup_scene()
    module = load_generator(generator)
    module.main()


if __name__ == "__main__":
    main()
