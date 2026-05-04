#hi

import bpy
import os
import unittest

def reset_blender():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mesh_objects():
    return [obj for obj in bpy.data.objects if obj.type == 'MESH']

def scene_dump():
    objs = mesh_objects()
    lines = [f"mesh_object_count={len(objs)}"]

    for obj in sorted(objs, key=lambda o: o.name):
        lines.append(f"object={obj.name}")
        lines.append(f"vertices={len(obj.data.vertices)}")
        lines.append(f"faces={len(obj.data.polygons)}")

        mats = []
        for mat in obj.data.materials:
            mats.append(mat.name if mat else "None")
        lines.append(f"materials={','.join(mats)}")

    return "\\n".join(lines)

class TestOBJImportEmpty(unittest.TestCase):

    def setUp(self):
        reset_blender()
        self.test_dir = os.path.dirname(__file__)

    def tearDown(self):
        for filename in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, filename))
        os.rmdir(self.test_dir)

    def import_obj(self, filename):
        path = os.path.join(self.test_dir, filename)
        result = bpy.ops.wm.obj_import(filepath=path)
        self.assertEqual({'FINISHED'}, result)
        return path

    def test_empty_obj_safe_handling(self):
        self.import_obj(r"C:\Windows\System32\blender\tests\data\empty.obj")

        objs = mesh_objects()
        self.assertEqual(0, len(objs), "Expected no mesh objects for empty OBJ")

if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
