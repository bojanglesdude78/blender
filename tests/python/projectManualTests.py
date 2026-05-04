import bpy
import os
import unittest
import tempfile

PARTIALLY_VALID_MULTI_OBJ = """\
# One valid object and one broken object
o ValidTriangle
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 1.0 0.0
f 1 2 3
 
o BrokenObject
v 2.0 0.0 0.0
f 999 1000 1001
f not_a_face garbage @@@@
"""
 
SINGLE_MISSING_MTL_OBJ = """\
mtllib this_file_does_not_exist.mtl
o SimplePlane
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.5 1.0 0.0
usemtl MissingMaterial
f 1 2 3
"""
 
VALID_WITH_MTL_OBJ = """\
mtllib valid_with_mtl.mtl
o Cube
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 1.0 1.0 0.0
v 0.0 1.0 0.0
v 0.0 0.0 1.0
v 1.0 0.0 1.0
v 1.0 1.0 1.0
v 0.0 1.0 1.0
usemtl TestMaterial
f 1 2 3 4
f 5 6 7 8
f 1 2 6 5
f 2 3 7 6
f 3 4 8 7
f 4 1 5 8
"""
 
EMPTY_OBJ = ""

VALID_WITH_MTL_MTL = """\
newmtl TestMaterial
Kd 0.64 0.64 0.64
"""

INVALID_OBJ = """\
THIS IS NOT A VALID OBJ FILE
@@@@ garbage content ####
"""
 

def reset_blender():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mesh_objects():
    return [obj for obj in bpy.data.objects if obj.type == 'MESH']\

class TestOBJImportManualSuite(unittest.TestCase):

    def setUp(self):
        reset_blender()
        self.test_dir = tempfile.mkdtemp()
        self._write_fixtures()

    def tearDown(self):
        for filename in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, filename))
        os.rmdir(self.test_dir)  

    def _write_fixtures(self):
        self._write("partially_valid_multi.obj", PARTIALLY_VALID_MULTI_OBJ)
        self._write("single_missing_mtl.obj", SINGLE_MISSING_MTL_OBJ)
        self._write("valid_with_mtl.obj", VALID_WITH_MTL_OBJ)
        self._write("empty.obj", EMPTY_OBJ)
        self._write("valid_with_mtl.mtl", VALID_WITH_MTL_MTL)
        #self._write("invalid.obj", INVALID_OBJ)

    def _write(self, filename, content):
        with open(os.path.join(self.test_dir, filename), 'w') as f:
            f.write(content)
        
    def import_obj(self, filename, **kwargs):
        path= os.path.join(self.test_dir, filename)
        result = bpy.ops.wm.obj_import(filepath=path, **kwargs)
        self.assertEqual({'FINISHED'}, result)
        return path

    #Test1: partially valid multiple objects
    def test_partially_valid_multi_object(self):
        self.import_obj("partially_valid_multi.obj")
        objs= mesh_objects()
        self.assertGreater(len(objs), 0, "Expected at least one mesh object from the valid portion")


    #Test2: valid object and missing MTL
    def test_valid_object_missing_mtl(self):
        self.import_obj("single_missing_mtl.obj")
        objs= mesh_objects()
        self.assertEqual(1, len(objs), "Expected exactly one mesh object")
        obj= objs[0]
        self.assertEqual(3, len(obj.data.vertices), "Expected 3 vertices")
        self.assertEqual(1, len(obj.data.polygons), "Expected 1 face")
        
    #Test3: large scales (x1000)
    def test_extrem_scale(self):
        self.import_obj("valid_with_mtl.obj", global_scale=1000.0)
 
        objs= mesh_objects()
        self.assertEqual(1, len(objs), "Expected exactly one mesh object")
        self.assertGreater(max(objs[0].dimensions), 10.0, "Expected object to be scaled up significantly")

    #Test4: empty OBJ handled safely
    def test_empty_obj_safe_handling(self):
       self.import_obj("empty.obj")
       objs = mesh_objects()
       self.assertEqual(0, len(objs), "Expected no mesh objects for empty OBJ")

if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
