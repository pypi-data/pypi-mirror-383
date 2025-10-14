import numpy as np
from ntsim.random import rng

def unit_vector(v):
    v_norm = np.ones(v.shape[0])
    np.sqrt(np.sum(np.power(v,2), axis=1), out=v_norm)
    zero_cond = v_norm==0. #булевая переменная, которая проверяет наличие нулей в v_norm
    v_norm[zero_cond] = np.ones(v_norm[zero_cond].shape) #замена нулей на единицы в v_norm
    v = (v.T/v_norm.T).T
    return v

def uniform_random_vector_in_cone(axis,costheta,eps=1e-10):
    # generate orthogonal random vector
    axis = unit_vector(axis)
    u = rng.uniform(size=(axis.shape[0],axis.shape[1]))
    ul = np.sum(u*axis,axis=1)
    ul = axis*ul.reshape(axis.shape[0],1)
    u = u - ul
    u = unit_vector(u)
    v = np.cross(u,axis)
    v = unit_vector(v)
    print(costheta,costheta.shape,axis.shape)
    z = rng.uniform(costheta,1,(axis.shape[0],))
    phi = 2*np.pi*rng.uniform(0,1,(axis.shape[0],))

    sintheta = np.sqrt(1-z**2)
    cosphi = np.cos(phi)
    sinphi = np.sin(phi)
    v_new = sintheta[:,None]*(cosphi[:,None]*u+sinphi[:,None]*v)+costheta[:,None]*axis

    c = np.sum(v_new*axis,axis=1)
    print(c)
    mask = c < costheta-eps
    if mask.any():
        print('uniform_random_vector_in_cone ',len(c[mask]))
        check1 = np.sum(u*axis,axis=1)
        check2 = np.sum(v*axis,axis=1)
        check3 = np.sum(u*v,axis=1)
        print('axis.shape',axis.shape)
        print('u.shape',u.shape)
        print('v.shape',v.shape)
        print('v_new.shape',v_new.shape)
        print(check1,check2,check3)
        print('costheta',costheta/c-1)

    return v_new


def rotate_vectors(r,dir,dir0):
    from scipy.spatial.transform import Rotation as R
    dir0 = np.array(dir0)
    phi = np.arctan2(dir0[1],dir0[0])
    theta = np.arccos(dir0[2]/np.sqrt(np.sum(dir0*dir0)))
    phi_d = np.tile([0,0,phi],(len(dir[:,0]),1))
    theta_d = np.tile([0,theta,0],(len(dir[:,0]),1))
    print(phi_d[:, None])
    t = R.from_rotvec(phi_d)
    t1 = R.from_rotvec(theta_d)
    r = t.apply(t1.apply(r))
    dir = t.apply(t1.apply(dir))
    return r, dir

def rotate_photons(ph_dir, seg_dir): # photon directions, segment directions
    from scipy.spatial.transform import Rotation
    phi = np.arctan2(seg_dir[:,1], seg_dir[:,0])
    theta = np.arccos(seg_dir[:,2]/np.sqrt(np.sum(seg_dir*seg_dir, axis=1)))
    phi   = np.array([np.zeros_like(phi), np.zeros_like(phi), phi]).T
    theta = np.array([np.zeros_like(theta), theta, np.zeros_like(theta)]).T
    rot1 = Rotation.from_rotvec(phi)
    rot2 = Rotation.from_rotvec(theta)
    return rot1.apply(rot2.apply(ph_dir))

def sample_cherenkov_photon_directions(n_photons, n):
    phi = rng.uniform(-np.pi, np.pi, n_photons)
    costh = 1./n
    sinth = (1.-costh**2)**0.5
    dirx = sinth*np.cos(phi)
    diry = sinth*np.sin(phi)
    dirz = np.full(n_photons, costh)
    directions = np.stack((dirx, diry, dirz), axis=-1)
    return directions


def translate_vectors(r, r0):
#    a = np.tile(r0, (r.shape[0],r.shape[1],1))
    r = r + r0
    return r, dir


def align_unit_vectors(a,b):
    # find rotation R: R*a = b
    from scipy.spatial.transform import Rotation
    a = unit_vector(a)
    b = unit_vector(b)
    c = np.cross(a,b)
    c = unit_vector(c)
    cosine = np.sum(a*b,axis=1)
    angle = np.arccos(cosine)
#    print(c.shape,angle.shape)
    rot = Rotation.from_rotvec(c*angle[:,None])
    return rot

def uniform_random_vector_in_cone_old(axis,angle):
    from scipy.spatial.transform import Rotation
    # axis = cone center
    # angle = cone angle (in radians)
    # algorithm from https://math.stackexchange.com/questions/56784/generate-a-random-direction-within-a-cone

    # generate random v1 around (0,0,1) on the sphere segment with theta  in (angle,1)
    z = rng.uniform(np.cos(angle), 1, axis.shape[0])
    phi = 2*np.pi*rng.uniform(size=axis.shape[0])
    v1 = np.array([np.sqrt(1-z**2)*np.cos(phi),np.sqrt(1-z**2)*np.sin(phi),z]).T

    axis = unit_vector(axis)
    # make the vector product of cone axis with unit_z = (0,0,1): orth = unit_z x axis
    unit_z = np.array([0.,0.,1.])
    orth = np.cross(unit_z,axis)
    # check
    mask = np.sum(orth*orth,axis=1) != 0.0
    orth = unit_vector(orth)
#    print(orth)
    # rotate generated random vector v1 around orth by angle between unit_z and axis.
    # This way cone axis will be centered on axis instead of (0,0,1)
    cosines = np.sum(axis*unit_z,axis=1)
    axis_angle = np.arccos(cosines).reshape(cosines.shape[0],1)
    rot = Rotation.from_rotvec(axis_angle * orth)
#    print(rot.as_dcm())

    new_v = rot.apply(v1)
#    a = rot.apply(unit_z)
    c = np.sum(new_v*axis,axis=1)
    mask = np.arccos(c)>angle
    if mask.any():
        print('uniform_random_vector_in_cone ',orth)
    return new_v

from numba import jit
import numpy as np

@jit(nopython=True,cache=True,error_model="numpy")
def segment_generator(center, radius, num_segments, intersect=True):
    segments = np.empty((num_segments, 2, 3))  # Preallocate array for segments
    for i in range(num_segments):
        theta = rng.uniform(0, 2*np.pi)
        phi = rng.uniform(0, np.pi)
        r = rng.uniform(0, radius)
        x = r * np.sin(phi) * np.cos(theta) + center[0]
        y = r * np.sin(phi) * np.sin(theta) + center[1]
        z = r * np.cos(phi) + center[2]

        # Generate a random direction
        phi = rng.uniform(0, np.pi)
        theta = rng.uniform(0, 2*np.pi)
        x_dir = np.sin(phi) * np.cos(theta)
        y_dir = np.sin(phi) * np.sin(theta)
        z_dir = np.cos(phi)

        # Ensure point_outside_sphere is outside the sphere
        point_outside_sphere_x = x + x_dir * 2*radius
        point_outside_sphere_y = y + y_dir * 2*radius
        point_outside_sphere_z = z + z_dir * 2*radius

        if not intersect:
            # Generate points outside the sphere
            x = x + 2 * radius
            y = y + 2 * radius
            z = z + 2 * radius
            point_outside_sphere_x = point_outside_sphere_x + 2 * radius
            point_outside_sphere_y = point_outside_sphere_y + 2 * radius
            point_outside_sphere_z = point_outside_sphere_z + 2 * radius

        segments[i, 0, :] = [point_outside_sphere_x, point_outside_sphere_y, point_outside_sphere_z]
        segments[i, 1, :] = [x, y, z]
    return segments


def generate_cherenkov_spectrum(lambda_min,lambda_max,sample):
    # generate wavelength spectrum 1/lambda^2 in (lambda_min,lambda_max) according to
    # 1/lambda = 1/lambda_min - u*(1/lambda_min-1/lambda_max), where u = uniform in (0,1)
    u = rng.uniform(size=sample)
    x = 1/lambda_min - u*(1/lambda_min-1/lambda_max)
    return 1/x

def searchsorted2d(a,b):
    m,n = a.shape
    max_num = np.maximum(a.max() - a.min(), b.max() - b.min()) + 1
    r = max_num*np.arange(a.shape[0])[:,None]
    p = np.searchsorted( (a+r).ravel(), (b+r).ravel(), side='left' ).reshape(m,-1)
    return p - n*(np.arange(m)[:,None])

def axes_bounds(x,y,z):
    return [axis_bounds(x), axis_bounds(y), axis_bounds(z)]

def axis_bounds(x):
    return [np.min(x),np.max(x)]

def get_particle_name_by_pdgid(pdgid):
    from particle import Particle
    return Particle.from_pdgid(pdgid).name

def get_pdgid_by_particle_name(name):
    from particle import Particle
    return int(Particle.from_evtgen_name(name).pdgid)

def resonance_decay(P: np.array, E: float, pdgid_1: int, pdgid_2: int):
#    print('P: ', P)
#    print('E: ', E)
    import ntsim.utils.systemofunits as units
    from particle import Particle
    from vector import obj
    m_pi     = Particle.from_pdgid(pdgid_1).mass*units.MeV/units.GeV
    m_p      = Particle.from_pdgid(pdgid_2).mass*units.MeV/units.GeV
    delta_m2 = m_p**2-m_pi**2
    M        = np.sqrt(E**2 - np.sum(P**2))
#    print('m_p: ', m_p)
#    print('m_pi: ', m_pi)
#    print('M: ', M)
    E_p  = 0.5*(M + delta_m2/M)
    E_pi = 0.5*(M - delta_m2/M)
#    print('E_p: ', E_p)
#    print('E_pi: ', E_pi)
    P_p  = np.sqrt(E_p**2 - m_p**2)
    P_pi = np.sqrt(E_pi**2 - m_pi**2)
#    print('P_p: ', np.sqrt(np.sum(P_p**2)))
#    print('P_pi: ', np.sqrt(np.sum(P_pi**2)))
    while True:
        cos_theta = rng.uniform(-1.0, 1.0)
        xi = rng.uniform(0, 5/8)
        pdf_Rein_Sehgal = (5 - 3*cos_theta**2)/8
        if pdf_Rein_Sehgal - xi >= 0: break
    sin_theta = np.sqrt(1 - cos_theta**2)
    phi = 2*np.pi*rng.uniform()
    nP_pi = P_pi*np.array((sin_theta*np.cos(phi), sin_theta*np.sin(phi), cos_theta))
    nP_p  = -nP_pi
#    print('nP_p: ', np.sqrt(np.sum(nP_p**2)))
#    print('nP_pi: ', np.sqrt(np.sum(nP_pi**2)))
    four_P_pi = obj(px=nP_pi[0], py=nP_pi[1], pz=nP_pi[2], E=E_pi)
    four_P_p  = obj(px=nP_p[0], py=nP_p[1], pz=nP_p[2], E=E_p)
    four_P_pi = four_P_pi.boost_p4(obj(px=P[0], py=P[1], pz=P[2], E=E))
    four_P_p = four_P_p.boost_p4(obj(px=P[0], py=P[1], pz=P[2], E=E))
    return (np.array((four_P_pi.px, four_P_pi.py, four_P_pi.pz)), four_P_pi.E,
            np.array((four_P_p.px, four_P_p.py, four_P_p.pz)), four_P_p.E)

def make_random_position_shifts(radius, height, amount):
    r = np.sqrt(rng.uniform(0 , radius**2 , amount))
    phi = rng.uniform(0 , 2*np.pi , amount)
    x = np.multiply(r, np.cos(phi))
    y = np.multiply(r, np.sin(phi))
    z = rng.uniform(0, height, amount)-0.5*height
    return np.array([x,y,z]).T