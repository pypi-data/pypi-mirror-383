import numpy as np
from numba import njit, types

@njit(types.containers.Tuple([types.float64[:],types.float64])(types.float64[:],types.float64[:]),cache=True)
def rotation_vector(primary_vector, direction_vector):
    rot_vec = np.empty(shape=(3))
    cos_phi_rot = primary_vector[0]*direction_vector[0]+\
                  primary_vector[1]*direction_vector[1]+\
                  primary_vector[2]*direction_vector[2]
    rot_vec[0] = primary_vector[1]*direction_vector[2]-primary_vector[2]*direction_vector[1]
    rot_vec[1] = primary_vector[2]*direction_vector[0]-primary_vector[0]*direction_vector[2]
    rot_vec[2] = primary_vector[0]*direction_vector[1]-primary_vector[1]*direction_vector[0]
    return rot_vec, cos_phi_rot

@njit(types.float64[:,:](types.float64[:],types.float64[:],types.float64[:,:]),cache=True)
def rotate_vectors(primary_vector, direction_vector, rotating_vectors):
    
    rot_vec, cos_phi_rot = rotation_vector(primary_vector, direction_vector)
    
    if cos_phi_rot == 1.:
        return rotating_vectors
    
    elif cos_phi_rot == -1.:
        for l in range(rotating_vectors.shape[0]):
            rotating_vectors[l][0] = -rotating_vectors[l][0]
            rotating_vectors[l][1] = -rotating_vectors[l][1]
            rotating_vectors[l][2] = -rotating_vectors[l][2]
        return rotating_vectors
    
    else:
        rot_vec = rot_vec/np.linalg.norm(rot_vec)
        
        sin_phi_rot = (1.-cos_phi_rot**2)**0.5
        
        for l in range(rotating_vectors.shape[0]):
            cos_alpha = rot_vec[0]*rotating_vectors[l][0]+\
                        rot_vec[1]*rotating_vectors[l][1]+\
                        rot_vec[2]*rotating_vectors[l][2]
            
            v_par_0 = rot_vec[0]*cos_alpha
            v_par_1 = rot_vec[1]*cos_alpha
            v_par_2 = rot_vec[2]*cos_alpha
            
            v_perp_0 = rotating_vectors[l][0]-v_par_0
            v_perp_1 = rotating_vectors[l][1]-v_par_1
            v_perp_2 = rotating_vectors[l][2]-v_par_2
            
            cross_0 = rot_vec[1]*v_perp_2-rot_vec[2]*v_perp_1
            cross_1 = rot_vec[2]*v_perp_0-rot_vec[0]*v_perp_2
            cross_2 = rot_vec[0]*v_perp_1-rot_vec[1]*v_perp_0
            
            rotating_vectors[l][0] = v_perp_0*cos_phi_rot+cross_0*sin_phi_rot+v_par_0
            rotating_vectors[l][1] = v_perp_1*cos_phi_rot+cross_1*sin_phi_rot+v_par_1
            rotating_vectors[l][2] = v_perp_2*cos_phi_rot+cross_2*sin_phi_rot+v_par_2
            
        return rotating_vectors