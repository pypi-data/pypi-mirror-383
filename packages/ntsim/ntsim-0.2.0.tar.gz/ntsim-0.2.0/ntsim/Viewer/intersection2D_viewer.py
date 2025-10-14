from ntsim.Viewer.viewer_base import viewerbase
import pyqtgraph.opengl as gl
import numpy as np
from pyqtgraph.Qt import QtGui
import pyqtgraph as pg

import matplotlib.pyplot as plt

from ntsim.Viewer.hits_viewer import hits_viewer
from ntsim.Viewer.tracks_viewer import tracks_viewer

from ntsim.utils.gen_utils import unit_vector, align_unit_vectors

import logging
log = logging.getLogger('histogram_viewer')

class intersection_viewer(viewerbase):
    def configure(self, opts):
        self.options = opts
#        print('opts: ', opts)
        self.ph_x = self.data['photons'].r[:, :, 0]
        self.ph_y = self.data['photons'].r[:, :, 1]
        self.ph_z = self.data['photons'].r[:, :, 2]
        self.ph_t = self.data['photons'].t
#        print('ph_t: ', self.ph_t)
        tracks = tracks_viewer.pos


#    def position(self,t):
#        return position_numba(self.r,self.t,t)

    def plane_of_cherenkov_ring(self):
#        print('geom: ', np.shape(self.data['geom']))
        (n_clusters,n_strings,n_om,n_vars) = np.shape(self.data['geom'])
        x = np.ndarray((n_clusters, n_strings, n_om), float)
        y = np.ndarray((n_clusters, n_strings, n_om), float)
        x_min = np.ndarray((n_clusters,), float)
        x_max = np.ndarray((n_clusters,), float)
        y_min = np.ndarray((n_clusters,), float)
        y_max = np.ndarray((n_clusters,), float)
        self.x_clusters = np.ndarray((n_clusters,), float)
        self.y_clusters = np.ndarray((n_clusters,), float)
        self.R_clusters = np.ndarray((n_clusters,), float)
        for i in range(n_clusters):
#            print(self.data['geom'][i][0][0][1])
            for j in range(n_strings):
                for k in range(n_om):
                    vars = self.data['geom'][i, j, k]
                    x[i, j, k]   = vars[1]
                    y[i, j, k]   = vars[2]
            x_min[i], x_max[i] = np.amin(x[i, :, :]), np.amax(x[i, :, :])
            y_min[i], y_max[i] = np.amin(y[i, :, :]), np.amax(y[i, :, :])
            self.x_clusters[i] = x[i][-1][0]
            self.y_clusters[i] = y[i][-1][0]
#            print('x_center: ', self.x_clusters)
        self.R_clusters = np.mean([x_max - x_min, y_max - y_min], axis = 0) / 2.
        self.R_clusters = self.R_clusters[0]
#        print(self.R_clusters)
#        print(x_max - x_min)
#        print(y_max - y_min)
#        print('r: ', self.data['photons'].r[0])
#       поворот цилиндров детектора относительно трека частицы

#        track_dir = unit_vector(np.diff(self.data['photons'].r, axis = 1)[0])
#        z_dir = np.tile(np.array([0. ,0., 1]), (np.shape(track_dir)[0], 1))
#        for n in range(np.shape(self.data['photons'].r)[0]):
#            rot = align_unit_vectors(z_dir, track_dir)
#        print(rot.as_euler('xyz', degrees=True))

        self.track_dir = unit_vector(np.diff(self.data['photons'].r, axis = 1)[0])
        self.track_dir = self.track_dir[~np.all(self.track_dir == 0, axis = 1)][0]
        self.track_dir = np.tile(self.track_dir, (np.shape(self.data['photons'].dir)[1], 1))
        mcos_theta = np.mean(np.sum(self.track_dir * (self.data['photons'].dir)[0], axis = 1))
        self.mcos_theta_s = mcos_theta**2
#        self.intersection3D()

    def intersection3D(self):
        self.t0 = 0.
        t = 2.*10**(-9)
        self.r = self.data['photons'].r[0][0]
#        print(self.r)
        self.v = 3*10**8
        self.n = self.track_dir[0]
        n = self.n
        alpha = self.n[2]**2-self.mcos_theta_s
        p = self.r + self.v*self.n*(t-self.t0)
        B = n*np.sum(self.n*p)-p*self.mcos_theta_s
        C = np.sum(self.n*p)**2-np.sum(p**2)*self.mcos_theta_s
        phi = np.linspace(0,2*np.pi,10**4)
        cos = np.cos(phi)
        sin = np.sin(phi)
        beta = B[2] + n[1]*n[2]*self.R_clusters*sin + n[0]*n[2]*self.R_clusters*cos
        gamma = (n[0]*n[0] - self.mcos_theta_s)*self.R_clusters**2*cos**2 + 2*n[0]*n[1]*self.R_clusters**2*sin*cos + (n[1]*n[1] - self.mcos_theta_s)*self.R_clusters**2*sin**2
        gamma = gamma + 2*B[0]*self.R_clusters*cos + 2*B[1]*self.R_clusters*sin + C
        x1 = self.R_clusters*cos
        y1 = self.R_clusters*sin
        D = beta**2-alpha*gamma

        z1 = (-beta + (D)**0.5)/alpha
        z2 = (-beta - (D)**0.5)/alpha
        x = np.hstack((x1,x1))
        y = np.hstack((y1,y1))
        z = np.hstack((z1,z2))
        return np.array([x,y,z])

    def intersection2D(self):
        r = self.intersection3D()
        n = self.n
        x_p= (1-n[0]*n[0])*r[0]-n[0]*n[1]*r[1] - n[0]*n[2]*r[2]
        y_p= (-n[0]*n[1])*r[0]+(1 - n[1]*n[1])*r[1] - n[1]*n[2]*r[2]
        z_p= (-n[0]*n[2])*r[0]-(n[1]*n[2])*r[1] + (1-n[2]*n[2])*r[2]
        return np.array([x_p, y_p, z_p]), np.array([r[0],r[1],r[2]])

    def plot_intersection(self):
        rp,rg = self.intersection2D()
        fig = plt.figure(figsize = (18,12))
        ax = fig.add_subplot(111, projection='3d')
#        print(rp[0], len(rp[0]), type(rp[0]))
        ax.scatter(rp[0],rp[1],rp[2],s = 0.5)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        plt.show()
        plt.close()

    def display_static(self, vis = True):
        pass

    def display_frame(self,frame):
        pass
