import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QMainWindow, QApplication
import numpy as np

def sierpinski(x, y, z, size, depth):
    if depth == 0:
        return [(x, y, z)]

    points = []
    new_size = size / 2.0

    for dx in [0, 1]:
        for dy in [0, 1]:
            for dz in [0, 1]:
                if dx + dy + dz != 1:
                    new_x = x + dx * new_size
                    new_y = y + dy * new_size
                    new_z = z + dz * new_size
                    points += sierpinski(new_x, new_y, new_z, new_size, depth-1)

    return points

class Visualizer(QMainWindow):

    def __init__(self, points):
        super(Visualizer, self).__init__()
        self.initUI(points)

    def initUI(self, points):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('3D Fractal Placement of Optical Modules')

        self.w = gl.GLViewWidget(self)
        self.w.opts['distance'] = 50
        self.w.setGeometry(0, 0, 800, 600)
        self.w.show()

        g = gl.GLGridItem()
        g.scale(2, 2, 1)
        self.w.addItem(g)

        pos = np.array(points)
        color = np.ones((len(points), 4), dtype=float)
        color[:, 3] = 0.5  # alpha channel

        sp2 = gl.GLScatterPlotItem(pos=pos, size=4, color=color)
        sp2.translate(5, 5, 0)
        self.w.addItem(sp2)

if __name__ == '__main__':
    import sys

    points = sierpinski(0, 0, 0, 20, 3)  # x, y, z, size, depth

    app = QApplication(sys.argv)
    ex = Visualizer(points)
    ex.show()
    sys.exit(app.exec_())
