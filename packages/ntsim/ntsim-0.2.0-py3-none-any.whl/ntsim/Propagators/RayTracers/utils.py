import numpy as np
from numba import jit, prange, objmode, float64, int64, boolean, gdb
import math
#import numba
from time import time
from numpy.core.multiarray import interp as interp
from numba.core import types
from numba.typed import Dict
from numba.typed import List
float_array = types.float64[:,:]

# DN: This function runs like the the numpy version unit_vector.
# run the tests as follows
# python -mtimeit -s'import test_unit_vector' 'test_unit_vector.test_numpy_version'
# 10000000 loops, best of 5: 33.9 nsec per loop
# python -mtimeit -s'import test_unit_vector' 'test_unit_vector.test_numba_version'
# 10000000 loops, best of 5: 31.7 nsec per loop
@jit(nopython=True,cache=True,parallel=True,fastmath=True)
def unit_vector_numba(v):
    v_unit = v
    for ix in prange(v.shape[0]):
        v_norm = math.sqrt(v[ix][0]*v[ix][0]+v[ix][1]*v[ix][1]+v[ix][2]*v[ix][2])
        v_unit[ix] = v[ix]/v_norm
    return v_unit


@jit(nopython=True,cache=True)
def position_numba(r,t,tc):
    X = r[:,:,0]
    Y = r[:,:,1]
    Z = r[:,:,2]
    T = t
    tc = 1.0*tc
    return interpolate_numba(tc,T,X,Y,Z)


@jit(nopython=True,cache=True)
def interpolate_numba(tc, t, x, y, z):
    x_interp = np.full((t.shape[1],tc.shape[0]),np.nan)
    y_interp = np.full((t.shape[1],tc.shape[0]),np.nan)
    z_interp = np.full((t.shape[1],tc.shape[0]),np.nan)

    for i in range(t.shape[1]):
        mask = (tc >= t[0,i])*(tc<=t[-1,i])
        x_interp[i][mask] = np.interp(tc,t[:,i],x[:,i])[mask]
        y_interp[i][mask] = np.interp(tc,t[:,i],y[:,i])[mask]
        z_interp[i][mask] = np.interp(tc,t[:,i],z[:,i])[mask]

    return x_interp,y_interp,z_interp

'''
@jit(nopython=True,cache=True)
def om_angular_dependence(x):
    x = -x
    f = 0.0
    angular_parameters = np.array([0.3082,-0.54192,0.19831,0.04912])
    for m in range(4):
        f +=  angular_parameters[m]*x**m
    return f

@jit(nopython=True,cache=True)
def pde(w):
    waves = np.linspace(300,650,8)
    eff   = np.array([0.28, 0.35, 0.35, 0.3,  0.22, 0.12, 0.05, 0.02])
    return np.interp(w,waves,eff)

@jit(nopython=True,cache=True)
def transmission_gel_glass(w):
    wavelength  = np.linspace(350,650,14)
    transmission_gel_glass = np.array([1.38e-3,5.e-3,0.544,0.804,0.83,0.866,0.9,0.9,0.9,0.9,0.9,0.9,0.9,0.9])
    return np.exp(np.interp(w,wavelength,np.log(transmission_gel_glass)))
'''

def update_array(a,b):
    # add b to a
    # check a simpler way
    # return np.append(a, b)
    if a.size:
        a = np.concatenate((a,b))
    else:
        a = b
    return a

@jit(nopython=True,cache=True)
def check_inside_old(point,bb):
    if point[0] < bb[0] or point[0] > bb[1]:
        return False
    if point[1] < bb[2] or point[1] > bb[3]:
        return False
    if point[2] < bb[4] or point[2] > bb[5]:
        return False
    return True


@jit(nopython=True,cache=True)
def check_crossing_old(point1, point2, bb):
    if check_inside_old(point1, bb):
        return True
    if point1[0]<bb[0] and point2[0]<bb[0]:
        return False                           #x
    if point1[0]>bb[1] and point2[0]>bb[1]:
        return False
    if point1[1]<bb[2] and point2[1]<bb[2]:
        return False                           #y
    if point1[1]>bb[3] and point2[1]>bb[3]:
        return False
    if point1[2]<bb[4] and point2[2]<bb[4]:
        return False                           #z
    if point1[2]>bb[5] and point2[2]>bb[5]:
        return False
    if point2[1]!=point1[1]:
        x_bb_p1 = (bb[2]-point1[1])/(point2[1]-point1[1])*(point2[0]-point1[0])+point1[0]
        x_bb_p2 = (bb[3]-point1[1])/(point2[1]-point1[1])*(point2[0]-point1[0])+point1[0]
    else:
        x_bb_p1 = bb[0]
        x_bb_p2 = bb[1]
    if x_bb_p1<bb[0] and x_bb_p2<bb[0]:
        return False                           #x
    if x_bb_p1>bb[1] and x_bb_p2>bb[1]:
        return False

    if point2[0]!=point1[0]:
        y_bb_p1 =  (bb[0]-point1[0])/(point2[0]-point1[0])*(point2[1]-point1[1])+point1[1]
        y_bb_p2 = (bb[1]-point1[0])/(point2[0]-point1[0])*(point2[1]-point1[1])+point1[1]
    else:
        y_bb_p1 = bb[2]
        y_bb_p2 = bb[3]

    if y_bb_p1<bb[2] and y_bb_p2<bb[2]:
        return False                           #y
    if y_bb_p1>bb[3] and y_bb_p2>bb[3]:
        return False
    return True


@jit(nopython=True,cache=True)
def sanity_bb(bb):
    if bb[0]>bb[1]:
        return False
    if bb[2]>bb[3]:
        return False
    if bb[4]>bb[5]:
        return False
    return True

#d = Dict.empty(key_type=types.unicode_type, value_type=types.float64[:])


@jit(nopython=True,cache=True,parallel=False)
def detector_hits(r, t, wave, weight, det_norm, hits, ta, f_pde, f_gel, f_ang_dep):
    assert hits.shape[1] == 13
    n_hits = hits.shape[0]
    det_hits = np.empty((0,15))
    for hit in prange(n_hits):
        cluster   = hits[hit][1]
        uid       = int(hits[hit][2])
        idet      = int(uid-cluster*288) # FIXME. A better way must be found
        t_hit     = hits[hit][6]
        trk       = int(hits[hit][10])
        t_travel  = t_hit-t[0,trk]
        w_noabs   = np.exp(-t_travel/ta[trk])
#        w_pde     = pde(wave[trk])
#        w_gel     = transmission_gel_glass(wave[trk])
        w_pde     = f_pde(wave[trk])
        w_gel     = f_gel(wave[trk])
        x_hit     = hits[hit][3]
        y_hit     = hits[hit][4]
        z_hit     = hits[hit][5]
        unit_x    = hits[hit][7]
        unit_y    = hits[hit][8]
        unit_z    = hits[hit][9]
        # calculate cosine of angle between normal to OM's top and this hit direction
        cosine = unit_x*det_norm[uid,0]+unit_y*det_norm[uid,1]+unit_z*det_norm[uid,2]
#        w_angular = om_angular_dependence(cosine)
        w_angular = f_ang_dep(cosine)
        outside_mask = hits[hit][11]
        step_number = hits[hit][12]
        det_hits = np.concatenate( ( det_hits,
                                     np.array([[uid, cluster, idet,
                                                t_hit,
                                                w_noabs, w_pde, w_gel, w_angular,
                                                x_hit, y_hit, z_hit,
                                                outside_mask, trk, step_number,weight]],float64) ) )
    return det_hits


@jit(nopython=True,cache=True,parallel=True)
def ray_tracing_gvd(r, t, geom, bb_clusters, bb_strings):
    (steps, tracks, ndim_r) = r.shape
    (n_clusters,n_box_vars) = bb_clusters.shape
    n_strings = bb_strings.shape[1]
    nvars = 13
    assert ndim_r == 3
    hits = np.full((tracks,nvars),np.inf,dtype=float64)
    for cluster in prange(n_clusters):
        if not sanity_bb(bb_clusters[cluster]):
            print("broken bb cluster ", cluster, bb_clusters[cluster])
            raise ValueError
        for string in prange(n_strings):
            if not sanity_bb(bb_strings[cluster,string]):
                print ("broken bb string", cluster, string, bb_strings[cluster,string])
                raise ValueError
    #
    rc = np.zeros(3)
    for trk in prange(tracks):
        #
        found_intersection = False
        for cluster in prange(n_clusters):
            # search for an intersection
            #if found make the list of cluster, string, list of om or cluster, uid
            for step in range(steps-1):
                ch = check_crossing(r[step,trk],r[step+1, trk],bb_clusters[cluster])
                if not ch:
                    continue
                for string in prange(n_strings):
                    ch = check_crossing(r[step,trk],r[step+1, trk],bb_strings[cluster,string])
                    if not ch:
                        continue
                    #
                    mask_cluster = geom[:,1] == cluster
                    mask_string  = geom[:,2] == string
                    mask_cl      = mask_cluster & mask_string
                    #
#                    z = geom[cluster, string, :, 3]
                    z = geom[mask_cl][:,5]
                    z1 = r[step,trk,2]
                    z2 = r[step+1,trk,2]
                    R = (bb_strings[cluster,string,1]-bb_strings[cluster,string,0])/2
                    mask = (z>=z1+R)*(z<=z2-R)
                    print(mask)
#                    g = geom[cluster,string]
                    g = geom[mask_cl]
                    ndet = g[mask].shape[0]
                    dets = g[mask]
                    t_hit_first = np.inf
                    x_hit_first = y_hit_first = z_hit_first = np.nan
                    x_hit_norm_first = y_hit_norm_first = z_hit_norm_first = np.nan
                    outside_mask_first = step_number_first = -1
                    idet_first = -1
                    hits_found = 0
                    for idet in prange(ndet):
                        found_intersection = False
                        t1 = t[step,trk]
                        t2 = t[step+1,trk]
                        rc[0] = dets[idet,1]
                        rc[1] = dets[idet,2]
                        rc[2] = dets[idet,3]
                        r_det = dets[idet,7]
                        found_intersection,x_hit,y_hit,z_hit,t_hit,unit_x,unit_y,unit_z,outside_mask = segment_sphere_intersection(r[step,trk],r[step+1,trk],rc,r_det,t1,t2)
                        if found_intersection:
                            hits_found +=1
                            if t_hit<t_hit_first:
                                t_hit_first = t_hit
                                idet_first = dets[idet,0]
                                x_hit_first = x_hit
                                y_hit_first = y_hit
                                z_hit_first = z_hit
                                x_hit_norm_first = unit_x
                                y_hit_norm_first = unit_y
                                z_hit_norm_first = unit_z
                                outside_mask_first = outside_mask
                                step_number_first = step
                            break
                    if hits_found:
                        hits[trk,0] = 1
                        hits[trk,1] = cluster
                        hits[trk,2] = idet_first
                        hits[trk,3] = x_hit_first
                        hits[trk,4] = y_hit_first
                        hits[trk,5] = z_hit_first
                        hits[trk,6] = t_hit_first
                        hits[trk,7] = x_hit_norm_first
                        hits[trk,8] = y_hit_norm_first
                        hits[trk,9] = z_hit_norm_first
                        hits[trk,10] = trk
                        hits[trk,11] = outside_mask_first
                        hits[trk,12] = step_number_first
        if not found_intersection:
            continue
        # calculate and save data
    mask = (hits[:,0] == 1)
    return hits[mask]

@jit(nopython=True,cache=True,parallel=True)
def ray_tracing_dumb(r, t, det_center,om_radius, ta):
    # ray tracing ignoring bounding_boxes
    (steps, tracks, ndim_r) = r.shape
    nvars = 7
    assert ndim_r == 3
    hits = np.full((tracks,nvars),np.inf,dtype=float64)
    #
    rc = np.zeros(3)
    for trk in prange(tracks):
        found_intersection = False
        for step in range(steps-1):
            t1 = t[step,trk]
            t2 = t[step+1,trk]
            rc[0] = det_center[0]
            rc[1] = det_center[1]
            rc[2] = det_center[2]
            found_intersection,x_hit,y_hit,z_hit,t_hit,unit_x,unit_y,unit_z,outside_mask = segment_sphere_intersection(r[step,trk],r[step+1,trk],rc,om_radius,t1,t2)
            if found_intersection:
                hits[trk,0] = 1
                hits[trk,1] = x_hit
                hits[trk,2] = y_hit
                hits[trk,3] = z_hit
                hits[trk,4] = t_hit
                hits[trk,5] = outside_mask
                dt = t_hit-t[0,trk]
                hits[trk,6] = np.exp(-dt/ta[trk])
                break # stop iterating over steps once the intersection found
    mask = (hits[:,0] == 1)
    return hits[mask]

#'Tuple((boolean, float64,float64,float64,float64))(float64[:], float64[:], float64[:], float64, float64, float64)',
@jit(nopython=True,cache=True,error_model="numpy")
def segment_sphere_intersection(r1,r2,rc,radius,t1,t2):
    # checks if segment (r1,r2) intersects the sphere with center rc and radius.
    assert t2>=t1
    assert radius>=0
    assert r1.shape[0] == 3
    assert r2.shape[0] == 3
    assert rc.shape[0] == 3

    x21 = r2[0]-r1[0]
    y21 = r2[1]-r1[1]
    z21 = r2[2]-r1[2]
    a = x21**2+y21**2+z21**2
    x10 = r1[0]-rc[0]
    y10 = r1[1]-rc[1]
    z10 = r1[2]-rc[2]
    b = (x21*x10+y21*y10+z21*z10)/a
    dr10_squared = x10**2+y10**2+z10**2
    dr10 = math.sqrt(dr10_squared)
    c = (dr10_squared - radius**2)/a        # if c>0, r1 is outside
    outside_mask = (c>0)
    discriminant = (b**2-c)
    there_solutions = (discriminant>0)

    if not there_solutions:
        return False,0,0,0,0,0,0,0,0

    d = math.sqrt(discriminant)
    s = -b - d # minimum among two solutions
    found_intersection = (s>=0)*(s<=1)
    if not found_intersection:
        return False,0,0,0,0,0,0,0,0
    x_hit = s*r2[0]+(1-s)*r1[0]
    y_hit = s*r2[1]+(1-s)*r1[1]
    z_hit = s*r2[2]+(1-s)*r1[2]
    t_hit = t1+(t2-t1)*s
    '''
    norm = math.sqrt(a)
    unit_x = -x21/norm
    unit_y = -y21/norm
    unit_z = -z21/norm
    '''
    x30 = x_hit-rc[0]
    y30 = y_hit-rc[1]
    z30 = z_hit-rc[2]
    norm = (x30**2+y30**2+z30**2)**0.5
    unit_x = x30/norm
    unit_y = y30/norm
    unit_z = z30/norm
    return  True,x_hit,y_hit,z_hit,t_hit,unit_x,unit_y,unit_z,outside_mask

'''a = np.array([0.,0.,0.])
b = np.array([0.,0.,0.])
c = np.array([0.,0.,0.])
import time
tic = time.time()
for i in range(10**7):
    d = segment_sphere_intersection(a,b,c,10.,0.,1.)
toc = time.time()

print(toc-tic)'''

# @jit(nopython=True,cache=True,parallel=True)
# def ray_tracing_tmp(r,t,rc,R):
#     assert r.shape[2]  == 3
#     assert rc.shape[1] == 3
#     (steps, tracks, ndim_r) = r.shape
#     (ndet,ndim_r) = rc.shape
#     nvars = 8
#     hits = np.full((tracks,ndet,nvars),np.inf,dtype=float64)
#     for trk in prange(tracks):
#         t_hit_first = np.inf
#         x_hit_first = y_hit_first = z_hit_first = np.nan
#         idet_first = -1
#         hits_found = 0
#         for idet in range(ndet):
#             found_intersection = False
#             for step in range(steps-1):
#                 t1 = t[step,trk]
#                 t2 = t[step+1,trk]
#                 found_intersection,x_hit,y_hit,z_hit,t_hit,unit_x,unit_y,unit_z = segment_sphere_intersection(r[step,trk],r[step+1,trk],rc[idet],R[idet],t1,t2)
#                 if found_intersection:
#                     hits_found +=1
#                     if t_hit<t_hit_first:
#                         t_hit_first = t_hit
#                         idet_first = idet
#                         x_hit_first = x_hit
#                         y_hit_first = y_hit
#                         z_hit_first = z_hit
#                         x_hit_norm_first = unit_x
#                         y_hit_norm_first = unit_y
#                         z_hit_norm_first = unit_z
#                     break
#         if hits_found:
#             hits[trk,idet_first,0] = 1
#             hits[trk,idet_first,1] = x_hit_first
#             hits[trk,idet_first,2] = y_hit_first
#             hits[trk,idet_first,3] = z_hit_first
#             hits[trk,idet_first,7] = t_hit_first
#     return hits


@jit(nopython=True,cache=True)
def ray_tracing(r,t,detectors_centers,detector_radii,detector_normals,ta,wave):
    (steps, tracks, ndim_r) = r.shape
    (ndet,ndim_r) = detectors_centers.shape
    nhits        = tracks
    xhits        = np.full((ndet,nhits),np.nan)
    yhits        = np.full((ndet,nhits),np.nan)
    zhits        = np.full((ndet,nhits),np.nan)
    thits        = np.full((ndet,nhits),np.nan)
    w_noabs      = np.full((ndet,nhits),np.nan)
    w_pde        = np.full((ndet,nhits),np.nan)
    w_gel        = np.full((ndet,nhits),np.nan)
    ang_res      = np.full((ndet,nhits),np.nan)
    outside_mask = np.full((ndet,nhits),False)
    track_id     = np.full((ndet,nhits),-1)
    step_number  = np.full((ndet,nhits),-1)

    ihit = -1
    for trk in range(tracks):
        if trk*100/tracks % 10 == 0:
            with objmode():
                print("ray_tracing: processing {0}/{1}".format(trk,tracks),end='\r')
        if trk == tracks - 1:
                print("ray_tracing: processed",tracks," photons")
        t_hit_first = np.inf
        x_hit_first = np.nan
        y_hit_first = np.nan
        z_hit_first = np.nan
        noabsorption_prob_first = np.nan
        pde_first          = np.nan
        gel_first          = np.nan
        ang_res_first      = np.nan
        outside_mask_first = False
        track_id_first    = -1
        step_number_first = -1
        idet_first        = -1

        for idet in range(ndet):
            found_intersection = False
            for step in range(steps-1):
                x21 = r[step+1,trk,0] - r[step,trk,0]
                y21 = r[step+1,trk,1] - r[step,trk,1]
                z21 = r[step+1,trk,2] - r[step,trk,2]
                a = x21**2+y21**2+z21**2

                x10 = r[step,trk,0] - detectors_centers[idet,0]
                y10 = r[step,trk,1] - detectors_centers[idet,1]
                z10 = r[step,trk,2] - detectors_centers[idet,2]
                b = (x10*x21+y10*y21+z10*z21)/a

                dr10_squared = x10**2 +y10**2+z10**2
                c = (dr10_squared - detector_radii[idet]**2)/a
                discriminant = (b**2-c)
                found_intersection = (discriminant>0)
#                print(trk,idet,step,found_intersection)
                if found_intersection:
                    d = math.sqrt(discriminant)
                    s1 = -b - d
                    s2 = -b + d
                    # select minimum among two solutions
                    s = -1
                    if s1 >= s2:
                        s = s2
                    else:
                        s = s1
                    s_mask = (s>0)*(s<1)
                    dr1 = math.sqrt(dr10_squared)
                    found_intersection = found_intersection*s_mask
                    if found_intersection:
                        x_hit = r[step,trk,0] + x21*s
                        y_hit = r[step,trk,1] + y21*s
                        z_hit = r[step,trk,2] + z21*s
                        # calculate traveled time from r1 to r_hit according to
                        # t_hit = (t2-t1)*|dr_hit|/|r2-r1|
                        dx_hit = x_hit-r[step,trk,0]
                        dy_hit = y_hit-r[step,trk,1]
                        dz_hit = z_hit-r[step,trk,2]
                        dt_hit = (t[step+1,trk] - t[step,trk])*math.sqrt((dx_hit**2+dy_hit**2+dz_hit**2)/a)  # a = |r2-r1|^2
                        t_hit = t[step,trk]+dt_hit

                        # save information about the detector which has  the first time hit.
                        # Other detectors must be ignored for this photon
                        if t_hit < t_hit_first:
                            idet_first  = idet
                            t_hit_first = t_hit
                            x_hit_first = x_hit
                            y_hit_first = y_hit
                            z_hit_first = z_hit
                            # calculate probability of no absorption
                            t_travel = t_hit-t[0,trk]
                            noabsorption_prob_first = np.exp(-t_travel/ta[trk])
                            # calculate photo-detection-efficiency
                            pde_first = pde(wave[trk])
                            gel_first =transmission_gel_glass(wave[trk])
                            # calculate cosine of angle between normal to OM's top and this hit
                            cosine = (x10*detector_normals[idet,0]+y10*detector_normals[idet,1]+z10*detector_normals[idet,2])/dr1
                            # calculate angular sensitivity of OM
                            ang_res_first = om_angular_dependence(cosine)
                            # if r1 is outside of the sphere?
                            outside_mask_first = dr1>detector_radii[idet]
                            # track id
                            track_id_first = trk
                            # step number (if step>0 scattering occured)
                            step_number_first = step
                    break
        # end of idet cycle
#                        print(trk,idet,step,t_hit,z_hit)
        if t_hit_first < np.inf:
            ihit += 1
            xhits[idet_first,ihit] = x_hit_first
            yhits[idet_first,ihit] = y_hit_first
            zhits[idet_first,ihit] = z_hit_first
            thits[idet_first,ihit] = t_hit_first

            w_noabs[idet_first,ihit] = noabsorption_prob_first
            w_pde[idet_first,ihit]   = pde_first
            w_gel[idet_first,ihit]   = gel_first
            ang_res[idet_first,ihit] = ang_res_first
            outside_mask[idet_first,ihit] = outside_mask_first
            track_id[idet_first,ihit] = track_id_first
            step_number[idet_first,ihit] = step_number_first

    return xhits,yhits,zhits,thits,w_noabs,w_pde,w_gel,ang_res,outside_mask,track_id,step_number
