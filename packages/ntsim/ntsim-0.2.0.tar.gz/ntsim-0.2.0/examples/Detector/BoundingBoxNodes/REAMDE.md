# BoundingBox Visualization for Detector Nodes

This script provides a way to visualize bounding boxes for detector nodes using `pyqtgraph` and `PyQt5`. The bounding boxes represent different components of a detector system, including the world, clusters, strings, and individual detectors.

## Overview

1. **createBoundingBoxNodes(opts)**: This function creates a hierarchical structure of bounding boxes. It starts with the world, then clusters, followed by strings, and finally individual detectors. The function takes in various parameters like the radius of an OM (Optical Module), the number of OMs along a string, cluster radius, etc., to create this structure.

2. **displayBoundingBoxNodes(world)**: This function visualizes the bounding boxes in a 3D space using `pyqtgraph`. The world is represented in blue, clusters in green, strings in red, and detectors in cyan.

## How to Run

To run the script, use the following command:

```bash
python3 your_script_name.py \
 --om_radius 0.03 --num_oms 4 --cluster_radius 1.5 \
 --num_strings 8 --world_radius 6 --z_margin 0.5 --num_clusters 6 --display
```

## Command Line Arguments

- `--om_radius`: Radius of an Optical Module (OM).
- `--num_oms`: Number of OMs along a string.
- `--om_z_spacing`: Z spacing between OMs.
- `--cluster_radius`: Radius of a cluster.
- `--num_strings`: Number of strings in a cluster.
- `--world_radius`: Radius of the world.
- `--z_margin`: Z margin for the world.
- `--num_clusters`: Number of clusters in the world.
- `--display`: Flag to trigger the visualization.

## Dependencies

- `numpy`
- `configargparse`
- `pyqtgraph`
- `PyQt5`

## Notes

Ensure you have all the dependencies installed before running the script. The visualization provides a hierarchical view of the detector system, making it easier to understand the spatial arrangement of different components. Adjust the command-line arguments as needed to visualize different configurations.
