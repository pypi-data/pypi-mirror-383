def test1():
    import numpy as np
    from scipy.spatial.transform import Rotation
    a = np.array([0,0,1])
    b = np.array([0,1,0])
    a = np.tile(a,(10,1))
    b = np.tile(b,(10,1))
    from gen_utils import align_unit_vectors

    rot = align_unit_vectors(a,b)
    print(rot.apply(a),b)



test1()
