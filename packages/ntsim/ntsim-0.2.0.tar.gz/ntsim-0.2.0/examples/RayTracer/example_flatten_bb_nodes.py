from ntsim.Detector.base.BoundingBoxNode import BoundingBoxNode
from ntsim.Propagators.RayTracers.rt_utils import flatten_bb_nodes

def create_bb_nodes():
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

    # Print the original tree
    print("Original Tree:")
    root.print()
    return root



def print_tree(bbs, uids, parents, children, detectors, index=0, indent=0):
    bounding_box = bbs[index]
    uid = uids[index]
    center = [(bounding_box[i] + bounding_box[i + 3]) / 2 for i in range(3)]
    dimensions = [bounding_box[i + 3] - bounding_box[i] for i in range(3)]
    print('  ' * indent + f'UID: {uid}, Center: {center}, Dimensions: {dimensions}, Bounding Box: {bounding_box}')

    # Find the children of the current node
    child_indices = [child for parent, child in zip(parents, children) if parent == index]
    print('  ' * indent + f'Children indices: {child_indices}')  # Debugging information

    # Print the UIDs of the detectors associated with this bounding box
    detector_uids = detectors[index] if index < len(detectors) else []
    print('  ' * indent + f'Detector UIDs: {detector_uids}')

    for child_index in child_indices:
        print_tree(bbs, uids, parents, children, detectors, child_index, indent + 1)

# Example usage:
root = create_bb_nodes()
bbs, uids, (parents, children), detectors = flatten_bb_nodes(root,2)
print("Reconstructed Tree:")
print('bbs: ',bbs)
print('uids: ',uids)
print('parents: ',parents)
print('children: ',children)
print('detectors: ',detectors)
print_tree(bbs, uids, parents, children, detectors)
