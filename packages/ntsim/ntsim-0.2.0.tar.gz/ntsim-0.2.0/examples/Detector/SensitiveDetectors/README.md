# Sensitive Detectors Visualization

This directory contains scripts that provide visualizations and simulations for different types of sensitive detectors using `pyqtgraph` and `PyQt5`.

## Table of Contents

1. [exampleSphericalSensitiveDetector.py](#examplesphericalsensitivedetectorpy)
2. [exampleBGVDSensitiveDetector.py](#examplebgvdsensitivedetectorpy)
3. [Future Scripts](#future-scripts)

---

## exampleSphericalSensitiveDetector.py

### Overview

This script provides a visualization of line segments in relation to a sphere. It illustrates the functionality of `detector.line_segment_intersection` by visually indicating which segments intersect the sphere and which do not.

### Key Features

- **Sphere Visualization**: Displays a sphere in a 3D space.
- **Segment Intersection Check**: Uses different colors for line segments to indicate their expected and actual intersection behavior with the sphere.

### How to Run

```bash
python3 exampleSphericalSensitiveDetector.py \
 --center 1 2 3 --radius 4 --num_segments 3
```

---

## exampleBGVDSensitiveDetector.py

### Overview

This script simulates the response of a BGVD Sensitive Detector to line segments and provides a visualization of the detector, hits, and the photocathode unit vector.

### Key Features

- **BGVD Sensitive Detector Simulation**: Simulates the response of the detector to line segments.
- **Visualization**: Displays the detector, hits, and the photocathode unit vector.
- **Effects Application**: Applies all effects for each segment and visualizes the hits with colors based on the effects.

### How to Run

```bash
python3 exampleBGVDSensitiveDetector.py \
 --center 1 2 3 --radius 4 --num_segments 3 --detector_normal 0 0 -1 --waves 350 600 --display
```

---

## Future Scripts

This directory is expected to expand with more scripts related to sensitive detectors' visualizations and simulations. Ensure to check back for updates and new additions.

## Dependencies

- `numpy`
- `configargparse`
- `pyqtgraph`
- `PyQt5`
- `logging`
- `matplotlib`

## Notes

Ensure you have all the dependencies installed before running the scripts. The visualizations provide intuitive ways to understand the behavior of different types of sensitive detectors and their interactions with line segments. Adjust the command-line arguments as needed to visualize different configurations and scenarios.
