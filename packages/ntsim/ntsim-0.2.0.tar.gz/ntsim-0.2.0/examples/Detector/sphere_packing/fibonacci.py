from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

N = 1000  # Number of points
indexes = np.arange(0, N, dtype=float) + 0.5

phi = np.arccos(1 - 2 * (indexes / N))
theta = np.pi * (1 + 5**0.5) * indexes

x, y, z = np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z)
plt.show()
