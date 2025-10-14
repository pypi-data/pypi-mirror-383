import cProfile
import configargparse
from examples.RayTracer.example_rt_bb import test_intersection_functions

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
    profiler = cProfile.Profile()
    profiler.enable()
    test_intersection_functions(opts)
    profiler.disable()
    profiler.print_stats(sort='cumulative')
    profiler.dump_stats('profile_results.prof')
