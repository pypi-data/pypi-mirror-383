import matplotlib.pyplot as plt
  
def test1():
    import numpy as np
    from scipy.spatial.transform import Rotation
    r = np.random.random((1,1,2))
    t = np.linspace(0,1,num = 50)
    d = np.random.random(2)
    from gen_utils import translate_vectors
    r1,dir1 = translate_vectors(r,dir,d)
    fig = plt.figure()
    plt.plot(r[0][0][0]*t, r[0][0][1]*t, color = 'black', label='initial vector')
    plt.plot(r1[0][0][0]*t, r1[0][0][1]*t, label='final vector')
    plt.plot(r[0][0][0]+d[0]*t,r[0][0][1]+d[1]*t,label = 'translation vector')
    plt.legend()
    plt.grid()
    plt.show()
test1()
