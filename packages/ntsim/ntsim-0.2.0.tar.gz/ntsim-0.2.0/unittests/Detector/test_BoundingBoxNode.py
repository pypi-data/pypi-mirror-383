import numpy as np
import unittest
from ntsim.Detector.BoundingBoxNode import BoundingBoxNode

def arrays_equal(a, b):
    return np.allclose(a,b)

def boxes_equal(box1, box2):
    return arrays_equal(box1.bounding_box, box2.bounding_box) and box1.uid == box2.uid

class TestBoundingBoxNode(unittest.TestCase):
    def setUp(self):
        BoundingBoxNode.instances.clear()

    def test_init(self):
        box = BoundingBoxNode(uid=0, center=[5, 5, 5], dimensions=[10, 10, 10])
        self.assertEqual(box.uid, 0)
        self.assertTrue(arrays_equal(box.center, [5, 5, 5]))
        self.assertTrue(arrays_equal(box.dimensions, [10, 10, 10]))
        self.assertTrue(arrays_equal(box.bounding_box, [0, 0, 0, 10, 10, 10]))
        self.assertEqual(box.children, [])

    def test_add_child(self):
        parent = BoundingBoxNode(uid=0, center=[5, 5, 5], dimensions=[10, 10, 10])
        child = BoundingBoxNode(uid=1, center=[5, 5, 5], dimensions=[5, 5, 5])
        parent.add_child(child)
        self.assertEqual(len(parent.children), 1)
        self.assertTrue(boxes_equal(parent.children[0], child))

    def test_find_node(self):
        parent = BoundingBoxNode(uid=0, center=[5, 5, 5], dimensions=[10, 10, 10])
        child = BoundingBoxNode(uid=1, center=[5, 5, 5], dimensions=[5, 5, 5])
        parent.add_child(child)
        self.assertTrue(boxes_equal(parent.find_node(0), parent))
        self.assertTrue(boxes_equal(parent.find_node(1), child))
        self.assertIsNone(parent.find_node(2))

    def test_unique_uid(self):
        box1 = BoundingBoxNode(uid=0, center=[5, 5, 5], dimensions=[10, 10, 10])
        with self.assertRaises(ValueError):
            box2 = BoundingBoxNode(uid=0, center=[5, 5, 5], dimensions=[10, 10, 10])

if __name__ == '__main__':
    unittest.main()
