import configargparse
import numpy as np
import unittest
import tempfile
import h5py

from ntsim.IO.gParticles import gParticles
from ntsim.IO.H5Writer import H5Writer
        
file_path = 'h5_output/events.h5'

class TestH5Writer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        parser = configargparse.ArgParser()
        H5Writer.add_args(parser)
        gParticles.add_args(parser)
        opts = parser.parse_known_args()
        gParticles.configure(gParticles, opts[0])
        self.writer = H5Writer('test_writer')
        self.writer.configure(opts[0])
        self.writer.open_file()
        self.writer.new_event('event_42')
    
    def tearDown(self):
        self.writer.close_file()
        self.temp_dir.cleanup()
    
    def test_file_creation(self):
        """Test basic file structure creation"""
        with h5py.File(self.writer.file.filename, "r") as f:
            # Verify header groups
            self.assertIn("geometry", f)
            self.assertIn("metadata", f)
            
            # Verify event groups
            self.assertIn("event_42", f)
            self.assertIn("tracks", f["event_42"])
            self.assertIn("particles", f["event_42"])
    
    def test_primitive_types(self):
        """Test writing primitive data types"""
        test_data = {
            "int_val": 42,
            "float_val": 3.14,
            "bool_val": True,
            "str_val": "test_string",
            "bytes_val": b"test_bytes"
        }
        
        self.writer.write_data(test_data, "metadata")
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            # Verify numeric types
            self.assertEqual(f["metadata/int_val"][()], 42)
            self.assertAlmostEqual(f["metadata/float_val"][()], 3.14)
            self.assertEqual(f["metadata/bool_val"][()], 1)
            
            # Verify string types
            self.assertEqual(f["metadata/str_val"][()].decode(), "test_string")
            self.assertEqual(f["metadata/bytes_val"][()], b"test_bytes")
    
    def test_str_sequence_types(self):
        """Test writing string sequence data types"""
        # Test homogeneous string list
        self.writer.write_data(["apple", "banana", "cherry"], "metadata")
        
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            # Verify string array
            str_arr = f["metadata/metadata"]
            self.assertEqual(str_arr.dtype, np.dtype("S6"))
            np.testing.assert_array_equal(
                str_arr[:],
                np.array([b"apple", b"banana", b"cherry"])
            )
    
    def test_mix_sequence_types(self):
        """Test writing mixed sequence data types"""
        # Test mixed-type sequence
        self.writer.write_data([42, 3.14, "test"], "metadata")
        
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:            
            # Verify mixed sequence group
            mixed_group = f["metadata/metadata"]
            self.assertEqual(mixed_group["0"][()], 42)
            self.assertAlmostEqual(mixed_group["1"][()], 3.14)
            self.assertEqual(mixed_group["2"][()].decode(), "test")
    
    def test_numpy_arrays(self):
        """Test writing numpy arrays of different dimensions"""
        test_arrays = {
            "1d": np.arange(10),
            "2d": np.random.rand(5, 3),
            "structured": np.array([(1, 2.0), (3, 4.0)], dtype=[("a", "i4"), ("b", "f8")])
        }
        
        self.writer.write_data(test_arrays, "tracks")
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            tracks = f["event_42/tracks"]
            np.testing.assert_array_equal(tracks["1d"][:], test_arrays["1d"])
            np.testing.assert_array_almost_equal(tracks["2d"][:], test_arrays["2d"])
            self.assertEqual(tracks["structured"].dtype, test_arrays["structured"].dtype)
    
    def test_database_objects(self):
        """Test writing DataBase-derived objects"""
        test_obj_1 = gParticles('test_particles_1',
                              uid = 42,
                              pdgid = 13,
                              pos_m=np.array([1., 2., 3.]),
                              t_ns = 1.,
                              direction = np.array([1., 0., 0.]),
                              Etot_GeV=5.,
                              metadata={"detector": "TPC", "event_id": 42}
                             )
        
        self.writer.write_data(test_obj_1, "particles")
        
        data = np.array([(42, 13, [1., 2., 3.], 1., [1., 0., 0.], 5.)], dtype=gParticles.data_type)
        
        test_obj_2 = gParticles('test_particles_2',
                              data=data,
                              metadata={"detector": "TPC", "event_id": 42}
                             )
        
        self.writer.write_data(test_obj_2, "particles")
        
        data = np.array([(42, 13, 1., 2., 3., 1., 1., 0., 0., 5.)], dtype=[('uid', 'i8'), ('pdgid', 'i4'), ('x_m', 'f8'), ('y_m', 'f8'), ('z_m', 'f8'), ('t_ns', 'f8'), ('dir_x', 'f8'), ('dir_y', 'f8'), ('dir_z', 'f8'), ('Etot_GeV', 'f8')])
        
        test_obj_3 = gParticles('test_particles_3')
        
        test_obj_3.from_custom_structured_array(data, {'pos_m':['x_m','y_m','z_m'],
                                                       'direction':['dir_x','dir_y','dir_z']})
        
        self.writer.write_data(test_obj_3, "particles")
        
        data = [np.array([42]), np.array([13]), np.array([[1., 2., 3.]]), np.array([1.]), np.array([[1., 0., 0.]]), np.array([5.])]
        names = ['uid', 'pdgid', 'pos_m', 't_ns', 'direction', 'Etot_GeV']
        
        test_obj_4 = gParticles('test_particles_4')
        
        test_obj_4.from_custom_array(data, names)
        
        self.writer.write_data(test_obj_4, "particles")
        
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            obj_group_1 = f["event_42/particles/test_particles_1"]
            np.testing.assert_array_equal(
                obj_group_1["data"]["pos_m"][:],
                np.array([[1., 2., 3.]])
            )
            self.assertEqual(obj_group_1["metadata/detector"][()].decode(), "TPC")
            self.assertEqual(obj_group_1["metadata/event_id"][()], 42)
            
            obj_group_2 = f["event_42/particles/test_particles_2"]
            np.testing.assert_array_equal(
                obj_group_2["data"]["t_ns"][:],
                1.
            )
            
            obj_group_3 = f["event_42/particles/test_particles_3"]
            np.testing.assert_array_equal(
                obj_group_3["data"]["direction"][:],
                np.array([[1., 0., 0.]])
            )
            
            obj_group_4 = f["event_42/particles/test_particles_4"]
            np.testing.assert_array_equal(
                obj_group_4["data"]["Etot_GeV"][:],
                5.
            )
    
    def test_accumulation_mode(self):
        """Test dictionary accumulation functionality"""
        data_to_accumulate = {
            "track1": np.array([1.0, 2.0, 3.0]),
            "track2": np.array([4.0, 5.0, 6.0])
        }
        
        self.writer.write_data(data_to_accumulate, "tracks", accumulate=True)
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            combined = f["event_42/tracks/combined"][:]
            expected = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
            np.testing.assert_array_equal(combined, expected)
    
    def test_special_methods(self):
        """Test geometry and clone shift writing"""
        # Test geometry writing
        bounds = np.array([(0, 0, 0, 10, 10, 10)], 
                        dtype=[("x1", "f4"), ("y1", "f4"), ("z1", "f4"),
                               ("x2", "f4"), ("y2", "f4"), ("z2", "f4")])
        detectors = np.array([(5, 5, 5)], dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")])
        
        self.writer.write_geometry(bounds, detectors)
        
        self.writer.close_file()
        
        with h5py.File(file_path, "r") as f:
            # Verify geometry
            self.assertIn("Bounding_Surfaces", f["geometry"])
            self.assertIn("Sensitive_Detectors", f["geometry"])
    
    def test_context_manager(self):
        """Test context manager functionality"""
        
        self.writer.close_file()
        
        with self.writer as writer:
            writer.write_data({"test": 42}, "metadata")
            
        # Verify file is closed
        self.assertIsNone(writer.file)
        
        # Verify data persisted
        with h5py.File(file_path, "r") as f:
            self.assertEqual(f["metadata/test"][()], 42)

if __name__ == "__main__":
    unittest.main()