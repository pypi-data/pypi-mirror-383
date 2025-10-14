import numpy as np

from particle.pdgid import charge
from particle import Particle

from numba import njit, types, prange

import ntsim.utils.systemofunits as units

from ntsim.utils.pdg_constants import *

from scipy.special import gamma as fgamma
from scipy.integrate import quad

def count_bunches(amount_phts: int, phts_bunch: int) -> np.array:
    n_bunches = int(amount_phts/phts_bunch)+1
    if amount_phts > phts_bunch:
        bunch_bounds = np.linspace(0,phts_bunch*(n_bunches-1),num=n_bunches,dtype=int)
        bunch_bounds = np.concatenate((bunch_bounds,[amount_phts]),dtype=int)
    else:
        bunch_bounds = np.array([0,amount_phts])
    return n_bunches, bunch_bounds

def data_from_pdg(pdgid):
    is_charged = np.array([np.fabs(charge(x)) == 1.0 for x in pdgid])
    is_nuclei  = np.array([not len(str(x)) == 12 for x in pdgid])
    tot_mask   = is_charged & is_nuclei
    
    masses = np.array([Particle.from_pdgid(x).mass for x in pdgid[tot_mask]])
    
    return tot_mask, masses

@njit(types.float64[:,:](types.float64[:,:]),cache=True)
def unit_vector(v):
    n_v = v.shape[0]
    res = np.empty(shape=(n_v,3))
    for i in range(n_v):
        norm = (v[i][0]**2+v[i][1]**2+v[i][2]**2)**0.5
        if norm == 0: norm = 1
        for j in range(3):
            res[i][j] = v[i][j]/norm
    return res

@njit(types.float64[:,:](types.float64[:,:],types.float64[:,:]),cache=True)
def delta_pos(segments1,segments2):
    n_seg = segments1.shape[0]
    res = np.empty(shape=(n_seg,3))
    for seg in range(n_seg):
        res[seg][0] = segments2[seg][0]-segments1[seg][0]
        res[seg][1] = segments2[seg][1]-segments1[seg][1]
        res[seg][2] = segments2[seg][2]-segments1[seg][2]
    return res

@njit(types.float64[:](types.float64[:,:],types.float64[:,:]),cache=True)
def distance_pos(segments1,segments2):
    n_seg = segments1.shape[0]
    res = np.empty(shape=n_seg)
    for seg in range(n_seg):
        res[seg] = ((segments1[seg][0]-segments2[seg][0])**2+(segments1[seg][1]-segments2[seg][1])**2+(segments1[seg][2]-segments2[seg][2])**2)**0.5
    return res

@njit(types.float64[:](types.float64[:],types.float64[:]),cache=True)
def distance_time(segments1,segments2):
    n_seg = segments1.shape[0]
    res = np.empty(shape=n_seg)
    for seg in range(n_seg):
        res[seg] = np.abs(segments2[seg]-segments1[seg])
    return res

@njit(types.float64[:](types.float64[:]),cache=True)
def mean_energy_per_segment(segments):
    n_seg = segments.shape[0]
    res = np.empty(shape=n_seg)
    for seg in range(n_seg-1):
        res[seg] = (segments[seg]+segments[seg+1])*0.5
    return res

@njit(types.containers.Tuple([types.float64[:],types.float64[:]])(types.float64),fastmath=True,cache=True)
def gen_costh_prob(refr_index):
    costh_a = 2.87
    costh_b = -5.71
    costh_c = 0.341
    costh_d = -0.00131
    
    costh_values = np.random.uniform(-1., 1., 10000)
    costh_prob = costh_a * np.exp( costh_b * np.abs(costh_values - 1./refr_index)**costh_c ) + costh_d
    costh_prob = costh_prob/costh_prob.sum()
    return costh_values, costh_prob

@njit(types.float64[:](types.float64[:],types.int64[:],types.float64[:,:]),cache=True)
def random_choice(x_data, amounts, p_data):
    data = []
    for i in range(np.shape(p_data)[0]):
        cumsum = np.cumsum(p_data[i])
        #cumsum = list(accumu(p_data[i]))
        gamma = np.random.uniform(0., 1., size=amounts[i])
        idx = np.searchsorted(cumsum,gamma)
        data.append(x_data[idx])
    output_data = np.empty(shape=0)
    for dat in data:
        output_data = np.concatenate((output_data,dat))
    return output_data

@njit(types.float64[:](types.float64[:],types.int64,types.float64[:]),cache=True)
def random_choice_single(x_data, amounts, p_data):
    cumsum = np.cumsum(p_data)
    gamma = np.random.uniform(0., 1., size=amounts)
    idx = np.searchsorted(cumsum,gamma)
    output_data = x_data[idx]
    return output_data

@njit(types.float64[:](types.float64[:],types.float64[:],types.float64),cache=True)
def get_sin2th(E,masses,n):
    sin2th = np.empty(shape=E.shape)
    for i, m in enumerate(masses):
        tmp = m/E[i]
        if tmp > 1 : a = 0.
        else : a = tmp
        beta = np.sqrt(1.-a**2)
        sin2th[i] = (1.-1./(n*beta)**2)
    return sin2th

@njit(types.float64[:](types.float64[:],types.float64,types.float64),cache=True)
def Frank_Tamm_formula(seg_sin2th,l_min,l_max):
    n_cher_phts_per_cm = np.empty_like(seg_sin2th)
    for i, sin2th in enumerate(seg_sin2th):
        if sin2th < 0. : n_cher_phts_per_cm[i] = 0.
        else : n_cher_phts_per_cm[i] = 2*np.pi*units.alpha_em*(1./l_min-1./l_max)*sin2th*(units.cm/units.nm)
    return n_cher_phts_per_cm

@njit(types.containers.Tuple([types.float64[:,:],types.float64[:],types.float64[:],types.float64[:,:]])(types.float64[:,:],types.float64[:,:],types.float64[:],types.float64[:],types.int64[:],types.int64[:],types.int64),cache=True)
def photon_quantities(pos_i, delta_pos, t_i, delta_t, progenitor_ids, seg_cher_phts, n_phts):
    ph_pos     = np.empty(shape=(n_phts,3))
    seg_dir    = np.empty(shape=(n_phts,3))
    ph_t       = np.empty(shape=(n_phts))
    progenitor = np.empty(shape=(n_phts))
    ph_rnd = np.random.uniform(0, .1, size=n_phts)
    k = 0
    for i in range(pos_i.shape[0]):
        for _ in range(seg_cher_phts[i]):
            for j in range(3):
                ph_pos[k][j]  = pos_i[i][j]+ph_rnd[k]*delta_pos[i][j]
                seg_dir[k][j] = delta_pos[i][j]
            ph_t[k]       = t_i[i]+ph_rnd[k]*delta_t[i] #FIXME
            progenitor[k] = progenitor_ids[i]
            k += 1
    return ph_pos, ph_t, progenitor, seg_dir

@njit(types.containers.Tuple([types.float64[:,:],types.float64[:]])(types.float64[:,:]),cache=True)
def rotation_vector(rot_vec):
    n_seg = rot_vec.shape[0]
    th = np.empty(shape=(n_seg))
    rot_vec = unit_vector(rot_vec)
    for i in range(n_seg):
        th[i] = np.arccos(rot_vec[i][2])
        tmp           = rot_vec[i][0]
        rot_vec[i][0] = -rot_vec[i][1]
        rot_vec[i][1] = tmp
        rot_vec[i][2] = 0.
    return rot_vec, th

@njit(types.float64[:,:](types.float64[:],types.int64[:],types.int64),cache=True)
def sample_cherenkov_photon_directions_n(sin2_th,seg_cher_phts,n_phts):
    dir = np.empty(shape=(n_phts,3))
    phi = np.random.uniform(-np.pi, np.pi, n_phts)
    k = 0
    for i in range(sin2_th.shape[0]):
        sin_th = sin2_th[i]**0.5
        cos_th = (1.-sin2_th[i])**0.5
        for _ in range(seg_cher_phts[i]):
            dir[k] = sin_th*np.cos(phi[k])
            dir[k][1] = sin_th*np.sin(phi[k])
            dir[k][2] = cos_th
            k += 1
    return dir

@njit(types.float64[:,:](types.float64[:,:],types.float64[:,:]),parallel=False,cache=True)
def rotate_photons(u, v):
    
    p, theta = rotation_vector(u)
    p        = unit_vector(p)
    
    for l in prange(v.shape[0]):
        sin_theta = np.sin(theta[l])
        cos_theta = np.cos(theta[l])
        
        cos_alpha = p[l][0]*v[l][0]+p[l][1]*v[l][1]+p[l][2]*v[l][2]
        
        v_par_0 = p[l][0]*cos_alpha
        v_par_1 = p[l][1]*cos_alpha
        
        v_perp_0 = v[l][0]-v_par_0
        v_perp_1 = v[l][1]-v_par_1
        v_perp_2 = v[l][2]
        
        cross_0 = p[l][1]*v_perp_2
        cross_1 = -p[l][0]*v_perp_2
        cross_2 = p[l][0]*v_perp_1-p[l][1]*v_perp_0
        
        v[l][0] = v_perp_0*cos_theta+cross_0*sin_theta+v_par_0
        v[l][1] = v_perp_1*cos_theta+cross_1*sin_theta+v_par_1
        v[l][2] = v_perp_2*cos_theta+cross_2*sin_theta
    return v

@njit(types.float64[:](types.float64,types.float64,types.int64),cache=True)
def generate_cherenkov_spectrum_n(l_min,l_max,n_phts):
    # generate wavelength spectrum 1/lambda^2 in (lambda_min,lambda_max) according to
    # 1/lambda = 1/lambda_min - u*(1/lambda_min-1/lambda_max), where u = uniform in (0,1)
    res = np.empty(shape=n_phts)
    u = np.random.uniform(0., 1., size=n_phts)
    for i in range(n_phts):
        res[i] = (1./l_min - u[i]*(1./l_min-1./l_max))**(-1)
    return res

@njit(types.int32[:](types.float64[:],types.float64[:],types.float64[:,:]),cache=True)
def pdf_interpolate(energy_interp, energy_GeV, data_pdf):
    
    n_cascades = len(energy_GeV)
    values     = np.random.uniform(0., 1., size=n_cascades)
    value_bins = np.empty(shape=(n_cascades),dtype=np.int32)
    
    for n, ene in enumerate(energy_GeV):
        
        a = ene/100-ene//100
        idx = np.searchsorted(energy_interp, ene)
        inter_pde = (1-a)*data_pdf[idx-1]+a*data_pdf[idx]
        
        cdf = np.cumsum(inter_pde)
        cdf = cdf/cdf[-1]
        
        value_bins[n] = np.searchsorted(cdf, values[n])
        
    return value_bins

def shower_age(t, y, b):
        t1 = t+b
        shower_age = 3.*t1/(t1+2.*y)
        return shower_age
    
def NKG_distr(ene, t, NKG_a, NKG_b):
    t1 = t+NKG_b
    y = np.log(ene/Ec_ele_GeV)
    y = np.transpose([y])
    NKG = 0.31*NKG_a/np.sqrt(y)*shower_age(t, y, NKG_b)**(-1.5*t1)*np.exp(t1)
    return NKG

def gamma_distr_t_norm(t, gamma_a, gamma_b):
    gamma_distr = gamma_b**gamma_a/fgamma(gamma_a)*t**(gamma_a-1)*np.exp(-gamma_b*t)
    return gamma_distr

def read_datasets(dataset: str, energy_bounds: list):
    
#    data_photons = np.genfromtxt('Datasets/DataPhotons.dat', delimiter=',')
    n_steps       = int((energy_bounds[1]-energy_bounds[0])//100+1)
    energy_interp = np.linspace(*energy_bounds, n_steps, dtype=float)
    
    data_grid = np.empty(shape=(n_steps, 2, 10000))
    data_pdf  = np.empty(shape=(n_steps, 10000))
    
    for n, ene in enumerate(energy_interp):
        data_grid[n] = np.load(f'Datasets/{dataset}/grid_e_{int(ene)}_GeV.npy')
        data_pdf[n]  = np.load(f'Datasets/{dataset}/pdf_e_{int(ene)}_GeV.npy')
    
    return energy_interp, data_grid, data_pdf

@njit(types.float64[:,:](types.int64,types.float64[:],types.float64[:]),cache=True)
def sample_photon_directions(n_photons, costh_values, costh_prob):
        cos_theta = random_choice_single(costh_values,n_photons,costh_prob)
        res = np.empty(shape=(n_photons,3))
        phi = np.random.uniform(-np.pi, np.pi, n_photons)
        sinth = np.sqrt(1.-cos_theta**2)
        res[:,0] = sinth * np.sin(phi)
        res[:,1] = sinth * np.cos(phi)
        res[:,2] = cos_theta
        return res

@njit(types.float64[:,:](types.float64[:],types.float64[:],types.float64[:]),cache=True)
def parameter_a_max_interpolate(ene, ene_bounds, param):
    
    ene_per_bounds = np.empty(shape=(len(ene_bounds)))
    shifts_interp  = np.empty(shape=(len(ene),3))
    
    shift = 0
    for n in range(len(ene_bounds)-1):

        ene_per_bounds = ene[(ene>ene_bounds[n])&(ene<ene_bounds[n+1])]
        param_a_max_interp = np.interp(ene_per_bounds, ene_bounds[n:n+2], param[n:n+2])
        
        shift_left  = param_a_max_interp-param[n]
        shift_right = param_a_max_interp-param[n+1]
        
        shifts_interp[shift:shift+len(ene_per_bounds),0] = n
        shifts_interp[shift:shift+len(ene_per_bounds),1] = shift_left
        shifts_interp[shift:shift+len(ene_per_bounds),2] = shift_right
        
        shift += len(ene_per_bounds)
    
    return shifts_interp

@njit(types.float64[:,:](types.float64[:],types.float64[:,::1],types.float64[::1],types.float64[:,:]),cache=True)
def params_interpolate(energy_GeV, data_grid_a, data_grid_b, data_pdf):
    
    n_cascades = len(energy_GeV)
    values     = np.random.uniform(0., 1., size=n_cascades)

    data_params = np.empty(shape=(len(energy_GeV),2))
    
    diff_a = np.diff(data_grid_a[0])
    diff_a = diff_a[diff_a!=0.][-1]
    diff_b = np.diff(data_grid_b)
    diff_b = diff_b[diff_b!=0.][-1]
    
    pdf_left  = data_pdf[0]/np.sum(data_pdf[0])/diff_a/diff_b
    pdf_right = data_pdf[1]/np.sum(data_pdf[1])/diff_a/diff_b
    
    for n, ene in enumerate(energy_GeV):
        
        a = ene/100-ene//100
        pdf_interp = (1-a)*pdf_left+a*pdf_right
        
        cdf_interp = np.cumsum(pdf_interp)
        cdf_interp = cdf_interp/cdf_interp[-1]
        
        value_bins = np.searchsorted(cdf_interp, values[n])
        
        data_a = data_grid_a[n][value_bins]
        data_b = data_grid_b[value_bins]
        
        data_params[n,0] = data_a
        data_params[n,1] = data_b
        
    return data_params

@njit(types.float64[:](types.float64[:],types.float64,types.float64),fastmath=True,cache=True)
def line(ene, a, b):
    return a*np.log(ene)+b

@njit(types.float64[:](types.float64[:],types.float64,types.float64),fastmath=True,cache=True)
def ln_line(ene, a, b):
    return np.log(a*np.log(ene)+b)

def logn_line(ene, a, b, n):
    return np.emath.logn(n,a*np.log(ene)+b)

@njit(types.float64[:](types.float64[:],types.float64,types.float64,types.float64),fastmath=True,cache=True)
def inv_line(ene, a, b, c):
    return (a*np.log(ene)+b)**(-1)+c

#@njit(types.float64[:,:](types.float64[:],types.float64[:,:],types.float64[:,:]),cache=True)
def shower_age(t, NKG_b, y):
    t1 = t+NKG_b
    shower_age = 3.*t1/(t1+2.*y)*np.heaviside(t1,0.)
#    shower_age[shower_age<0.] = 0.01
    return shower_age

#@njit(types.float64[:,:](types.float64[:],types.float64[:,:],types.float64[:,:],types.float64[:,:]),cache=True)
def NKG_adv(t, NKG_a, NKG_b, NKG_max):
    t1 = t+NKG_b
    y = NKG_max+NKG_b
    NKG = 0.31*NKG_a/np.sqrt(y)*shower_age(t, NKG_b, y)**(-1.5*t1)*np.exp(t1)
    return NKG