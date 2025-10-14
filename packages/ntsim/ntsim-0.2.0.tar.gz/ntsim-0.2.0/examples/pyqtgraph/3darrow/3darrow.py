from ntsim.utils.pyqtgraph_tricks import draw_arrow
import numpy as np
import pyqtgraph.opengl as gl
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = gl.GLViewWidget()
    window.show()
    window.setCameraPosition(distance=20)

    start = np.array([0, 0, 0])
    end = np.array([1, 0, 1])
    color = np.array([1, 0, 0, 1])  # RGBA
    draw_arrow(window, start, end, color)

    QtWidgets.QApplication.instance().exec_()
