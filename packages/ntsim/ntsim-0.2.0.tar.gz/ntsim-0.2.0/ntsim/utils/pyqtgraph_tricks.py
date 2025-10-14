import numpy as np
import pyqtgraph.opengl as gl
from PyQt5 import QtCore, QtGui, QtWidgets

def draw_arrow(window, start, end, color, arrowhead_length_ratio=0.2, arrowhead_width_ratio=0.1):
    # Ensure start and end are float arrays
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    # Create the arrow shaft
    shaft = np.array([start, end])
    shaft_item = gl.GLLinePlotItem(pos=shaft, color=color, width=2, antialias=True)
    window.addItem(shaft_item)

    # Define the point where the arrowhead starts
    arrowhead_start = end - arrowhead_length_ratio * (end - start)

    # Define the base of the arrowhead
    direction = (end - start) / np.linalg.norm(end - start)
    orthogonal = np.cross(direction, np.array([direction[1], -direction[0], 0]))
    if np.linalg.norm(orthogonal) == 0:  # this happens only if direction was [0, 0, z]
        orthogonal = np.array([1., 0., 0.])
    orthogonal /= np.linalg.norm(orthogonal)
    Q = arrowhead_start + arrowhead_width_ratio * orthogonal
    R = arrowhead_start - arrowhead_width_ratio * orthogonal

    # Create the arrowhead
    arrowhead1 = np.array([Q, end])
    arrowhead2 = np.array([R, end])
    arrowhead1_item = gl.GLLinePlotItem(pos=arrowhead1, color=color, width=2, antialias=True)
    arrowhead2_item = gl.GLLinePlotItem(pos=arrowhead2, color=color, width=2, antialias=True)
    window.addItem(arrowhead1_item)
    window.addItem(arrowhead2_item)
