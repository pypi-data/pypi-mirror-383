import unittest
from ntsim.Detector.base.BoundingBoxNode import BoundingBoxNode
from ntsim.Propagators.RayTracers.rt_utils import flatten_bb_nodes
import numpy as np
from numpy import array
class TestFlattenTree(unittest.TestCase):

    def create_bb_nodes(self):
        # Create a tree with arbitrary depth
        root = BoundingBoxNode(0, [0, 0, 0], [2, 2, 2])
        child1 = BoundingBoxNode(1, [1, 1, 1], [1, 1, 1])
        child2 = BoundingBoxNode(2, [-1, -1, -1], [1, 1, 1])
        grandchild1 = BoundingBoxNode(3, [1.25, 1.25, 1.25], [0.5, 0.5, 0.5])
        grandchild2 = BoundingBoxNode(4, [-1.75, -1.75, -1.75], [0.5, 0.5, 0.5])

        root.add_child(child1)
        root.add_child(child2)
        child1.add_child(grandchild1)
        child2.add_child(grandchild2)

        return root

    def test_flatten(self):
        root = self.create_bb_nodes()

        flattened_bbs, relations = flatten_bb_nodes(root)
        expected_bbs = [array([-1., -1., -1.,  1.,  1.,  1.]), array([0.5, 0.5, 0.5, 1.5, 1.5, 1.5]), array([1. , 1. , 1. , 1.5, 1.5, 1.5]), array([-1.5, -1.5, -1.5, -0.5, -0.5, -0.5]), array([-2. , -2. , -2. , -1.5, -1.5, -1.5])]
        expected_relations = [((0, 0), [(1, 1), (3, 2)]), ((3, 2), [(4, 4)]), ((1, 1), [(2, 3)])]

        for fb, eb in zip(flattened_bbs, expected_bbs): # Compare arrays individually
            self.assertTrue(np.array_equal(fb, eb), f"Expected {eb}, but got {fb}")

        self.assertEqual(relations, expected_relations, f"Expected {expected_relations}, but got {relations}")

if __name__ == "__main__":
    unittest.main()
