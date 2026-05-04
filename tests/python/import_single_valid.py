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

class TestOBJImportValidSingleObjectWithValidMtl(unittest.TestCase):

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

    # Test1: valid single object + valid MTL
    def test_valid_single_object_with_valid_mtl(self):
        self.import_obj(r"C:\Windows\System32\blender\tests\data\bl_single_valid.obj")

        objs = mesh_objects()
        self.assertEqual(1, len(objs), "Expected exactly one mesh object")

        obj = objs[0]
        self.assertEqual(3, len(obj.data.vertices), "Expected 3 vertices")
        self.assertEqual(1, len(obj.data.polygons), "Expected 1 face")

        self.assertGreaterEqual(len(obj.data.materials), 1, "Expected a material slot")
        self.assertIsNotNone(obj.data.materials[0], "Expected material to be assigned")
        self.assertEqual("RedMat", obj.data.materials[0].name)

if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)