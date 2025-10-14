import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def test1():
    import numpy as np
    from scipy.spatial.transform import Rotation
    r = np.zeros((5,3))
    for i in range(len(r)):
        r[i][2] = 0.5
    d2 = np.array([0,1,0])
    d = np.array([1,1,1])
    d1 = np.array([0,0,1])
    dir = np.random.random((5,3))
    from gen_utils import rotate_vectors
    r1,dir1 = rotate_vectors(r,dir,d)
    #r2,dir2 = rotate_vectors(r,dir,d1)
    #dir3 = rotate_vectors(r,dir,d2)
    a = np.arccos(np.sum(r*r1,axis =1)/(np.sqrt(np.sum(r*r,axis = 1 ))*np.sqrt(np.sum(r1*r1,axis =1 ))))*180/np.pi
    print('angle between initial and final track (min and max)',a.min(),a.max())
    t = np.linspace(0,1,num=100)
    fig = plt.figure(figsize = (18,12))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(0*t, 0*t, 1*t, color = 'black',label='track before rotating')
    ax.plot(r[0][0]+dir[0][0]*t, r[0][1]+dir[0][1]*t, r[0][2]+dir[0][2]*t,color = 'black')
    ax.plot(r1[0][0]+dir1[0][0]*t, r1[0][1]+dir1[0][1]*t, r1[0][2]+dir1[0][2]*t,'green', label='rotating to (1,1,1)')
    ax.plot(d[0]*t, d[1]*t, d[2]*t, color = 'green')
    #ax.plot(r2[0][0]+dir2[0][0]*t, r2[0][1]+dir2[0][1]*t, r2[0][2]+dir2[0][2]*t,color = 'b', label='rotating to (0,1,0)')
    #ax.plot(d1[0]*t, d1[1]*t, d1[2]*t, color = 'b')
    ax.legend()
    plt.grid()
    plt.show()


test1()
