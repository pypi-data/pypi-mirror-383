from gen_utils import unit_vector, uniform_random_vector_in_cone
import numpy as np

def test1(axis,angle):
    sample = 20
    axis = unit_vector(axis)
    axis = np.tile(axis,(sample,1))
    v = uniform_random_vector_in_cone(axis,angle)
    cosines = np.sum(v*axis,axis=1)
    angles  = np.arccos(cosines)

def test2(axis,angle):
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    pos = [221, 222, 223, 224]
    sample = 10000
    fig = plt.figure(figsize=plt.figaspect(0.5))

    plt.subplots_adjust(hspace=0.4)
    fig.suptitle('Validate rotations', fontsize=14)
    ax = Axes3D(fig)
    x = y = z = np.zeros(sample,dtype=float)
    v = np.tile(axis,(sample,1))
    v1 = uniform_random_vector_in_cone(v,angle)
    ax.scatter(v1[:,0],v1[:,1],v1[:,2], s=0.05,marker='.')
    plt.savefig('plots/test2_uniform_random_vector_in_cone.pdf')

#axis=np.array([[1,0,0], [0,1,0], [0,0,1], [1.,1.,2.]], dtype=np.float64)
#test1(axis,np.arccos(0.5))
axis=np.array([[0,1,2]])
test2(axis,np.pi/2)
