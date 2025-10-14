import configargparse
import numpy as np
import time
from ntsim.Propagators.RayTracers.rt_utils import flatten_bb_nodes, hierarchical_searches, check_crossing, check_crossing_vectorized
from ntsim.Detector.base.BoundingBoxNode import BoundingBoxNode
from ntsim.Detector.TelescopeFactory import TelescopeFactory
from examples.Telescopes.Example1.Example1Telescope import example1_telescope_options


def create_segments(bbs, parents, num_segments):
    # Identify leaf nodes (nodes without children)
    leaf_indices = [i for i in range(len(bbs)) if not any(parent == i for parent in parents)]

    segments = []
    expected_intersections = []

    world_bb = bbs[0]  # Assuming the world bounding box is the first one
    # Calculate the distance to place the start point outside the world bounding box
    dimensions = world_bb[3:]-world_bb[:3]
    world_radius = np.linalg.norm(dimensions)
    outside_distance = world_radius * 2.5  # 2.5 times the radius to ensure it's outside
    for _ in range(num_segments):
        # Randomly select a leaf node
        leaf_index = np.random.choice(leaf_indices)
        leaf_bb = bbs[leaf_index]

        # Create an endpoint within the leaf bounding box
        end_point = np.random.uniform(leaf_bb[:3], leaf_bb[3:])

        # Create a start point outside the world bounding box
        direction = np.random.uniform(-1, 1, 3)
        direction /= np.linalg.norm(direction)  # Normalize the direction
        start_point = world_bb[:3] + outside_distance * direction

        # Add the segment
        segments.append([start_point, end_point])

        # Add the leaf index to the expected intersections
        expected_intersections.append(leaf_index)
    return np.array(segments), np.array(expected_intersections)

def find_intersections_hierarchical(segments, bbs, parents, children):
    # Perform the hierarchical search
    start_time = time.time()
    intersections_hierarchical = hierarchical_searches(segments, bbs, parents, children)
    end_time = time.time()
    print(f"Hierarchical search time: {end_time - start_time} seconds")
    print(f"Intersections found (hierarchical): {intersections_hierarchical}")
    return intersections_hierarchical

def find_intersections_brute_force(segments, bbs, parents):
    # Perform the brute-force search
    start_time = time.time()
    intersections_brute_force = []
    # Check if the bounding box intersects with any segment
    for p1, p2 in segments:
        for i, bb in enumerate(bbs):
            # Check if the bounding box has children
            has_children = any(parent == i for parent in parents)
            if not has_children and check_crossing(p1, p2, bb):
                intersections_brute_force.append(i)
    end_time = time.time()
    print(f"Brute-force search time: {end_time - start_time} seconds")
    print(f"Intersections found (brute-force): {intersections_brute_force}")
    return intersections_brute_force

def find_intersections_vectorized(segments, bbs, parents):
    # Check vectorized function
    start_time = time.time()
    intersection_indices = check_crossing_vectorized(segments, bbs, parents)

    # Initialize an empty list for each segment
    intersections_vectorized = [[] for _ in range(segments.shape[0])]

    # Iterate through the intersection indices and append the bounding box index to the corresponding segment's list
    for bb_index, segment_index in intersection_indices:
        intersections_vectorized[segment_index].append(bb_index)

    # Convert the lists to a flat array, maintaining the order of segments
#    intersections_vectorized_flat = [item[0] for item in intersections_vectorized]


    end_time = time.time()
    print(f"intersections_vectorized search time: {end_time - start_time} seconds")
    print(f"intersections_vectorized:{intersections_vectorized}")
    return intersections_vectorized

def test_intersection_functions(opts):
    # Create a TelescopeFactory object
    factory = TelescopeFactory()

    # Configure the factory with the provided options
    factory.configure(opts)

    # Get telescope
    telescope = factory.get_telescope()

    # Configure the telescope
    telescope.configure(example1_telescope_options(opts))

    # Create a world
    world = BoundingBoxNode(uid=0, center=np.array([0,0,0]), dimensions=np.array([1, 1, 1]))  # dimensions will be updated in add_bounding_boxes method

    # Build the bounding boxes for the telescope
    telescope.add_bounding_boxes(world=world, build=True)

    # Flatten the bounding box tree
    bbs, uids, relationships = flatten_bb_nodes(world)
    parents, children = relationships  # Unpack the tuple into two separate arrays
    segments, expected_intersections = create_segments(bbs, parents, 10)  # Example with 100 segments

    print(f"Intersections expected : {expected_intersections}")
    # Start tests
    intersections_hierarchical = find_intersections_hierarchical(segments, bbs, parents, children)
    intersections_brute_force = find_intersections_brute_force(segments, bbs, parents)
    intersections_vectorized = find_intersections_vectorized(segments, bbs, parents)
    # Check that all methods found the same intersections
    #assert list(intersections_hierarchical) == intersections_brute_force == list(expected_intersections), "Different intersections found!"


if __name__ == '__main__':
    # Parse command line arguments
    from ntsim.utils.arguments_handling import NestedNamespace
    parser = configargparse.get_argument_parser()
    parser.add('--telescope.name', type=str, default='Example1Telescope', help='Telescope to use')
    parser.add('--telescope.Example1.radius', type=float, default=0.2, help='sensitive_detector radius')
    parser.add('--telescope.Example1.photocathode_unit_vector', type=float, nargs=3, default=[0, 0, -1], help='unit vector of the  sensitive detector photocathode ')
    parser.add('--telescope.Example1.n_clusters_x', type=int, default=1, help='Number of clusters in x direction')
    parser.add('--telescope.Example1.n_clusters_y', type=int, default=1, help='Number of clusters in y direction')
    parser.add('--telescope.Example1.n_strings_x', type=int, default=1, help='Number of strings in x direction within a cluster')
    parser.add('--telescope.Example1.n_strings_y', type=int, default=1, help='Number of strings in y direction within a cluster')
    parser.add('--telescope.Example1.z_spacing', type=float, default=1, help='Spacing in z direction')
    parser.add('--telescope.Example1.n_detectors_z', type=int, default=1, help='Number of detectors in z direction per string')
    parser.add('--telescope.Example1.x_string_spacing', type=float, default=2, help='Spacing between strings in x direction')
    parser.add('--telescope.Example1.y_string_spacing', type=float, default=2, help='Spacing between strings in y direction')
    parser.add('--telescope.Example1.x_cluster_spacing', type=float, default=10, help='Spacing between clusters in x direction')
    parser.add('--telescope.Example1.y_cluster_spacing', type=float, default=10, help='Spacing between clusters in y direction')
    parser.add('--telescope.Example1.world_center', type=float, nargs=3, default=[0, 0, 0], help='Center of the world')

    opts = parser.parse_args(namespace=NestedNamespace())
    test_intersection_functions(opts)
