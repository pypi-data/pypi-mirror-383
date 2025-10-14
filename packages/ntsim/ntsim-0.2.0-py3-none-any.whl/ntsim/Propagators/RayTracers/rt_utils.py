import numpy as np
from numba import jit, njit, types, prange,float64, int64
from numba.typed import List
from numba.types import UniTuple, boolean
from ntsim.utils.report_timing import report_timing
import math
from ntsim.Propagators.RayTracers.utils import segment_sphere_intersection

'''
def check_crossing(label: str):
    for attr_name in dir(BoundingSurfaces):
        if label == attr_name:
            attr_value = getattr(BoundingSurfaces, attr_name)
            return attr_value.check_intersection
'''

#signature_check_crossing = boolean(float64[:], float64[:], float64[:])
@njit(types.boolean(types.float64[:],types.float64[:],types.float64[:]), cache=True)
def check_intersection_box(point1, point2, bounding_box):
    # Define the parametric line: P(t) = point1 + t * (point2 - point1)
    delta = point2 - point1
    
    x,y,z,wx,wy,h, = bounding_box
    bb = np.array([x-wx,y-wy,z-h,x+wx,y+wy,z+h])

    # Define the clipping parameters for t
    t_min = 0
    t_max = 1

    # Clip against each axis
    for i in range(3):
        if delta[i] == 0:
            # Line is parallel to this axis; check if it's outside the bounding box
            if point1[i] < bb[i] or point1[i] > bb[i + 3]:
                return False
        else:
            # Compute the intersection values for this axis
            t1 = (bb[i] - point1[i]) / delta[i]
            t2 = (bb[i + 3] - point1[i]) / delta[i]

            # Swap if necessary to ensure t1 < t2
            if t1 > t2:
                t1, t2 = t2, t1

            # Update the clipping parameters
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)

            # Check if the line is outside the bounding box
            if t_min > t_max:
                return False

    # If we reach here, the line segment intersects the bounding box
    return True

'''
Let's define
* A is the start point of straight line segment, A = {x1,y1,z1}
* B is the end point of straight line segment,   B = {x2,y2,z2}
* C is the center of the center of the intersected sphere, C = {x3,y3,z3}
* r is the radius of the center of the intersected sphere

Coordinate equations of the straight line
x = x1+u*(x2-x1)
y = y1+u*(y2-y1)
z = z1+u*(z2-z1)

Equation of the sphere
(x-x3)^2+(y-y3)^2+(z-z3)^2=r^2

Substituting the equation of the line into the sphere gives a quadratic equation of the form
a*u^2+b*u+c=0
where
a=(x2-x1)^2+(y2-y1)^2+(z2-z1)^2
b=2*[(x2-x1)*(x1-x3)+(y2-y1)*(y1-y3)+(z2-z1)*(z1-z3)]
c=x3^2+y3^2+z3^2+x1^2+y1^2+z1^2-2*[x3*x1+y3*y1+z3*z1]-r^2

The exact behaviour is determined by the determinant
b^2-4*a*c
* If this is less than 0 then the line does not intersect the sphere
* If it equals 0 then the line is a tangent to the sphere intersecting it at one point, namely at u = -b/2a
* If it is greater then 0 the line intersects the sphere at two points
'''
@njit(types.boolean(types.float64[:],types.float64[:],types.float64[:]), cache=True)
def check_intersection_sphere(point1, point2, bounding_sphere):
    # Define the parametric line: P(t) = point1 + t * (point2 - point1)
    x1,y1,z1   = point1
    x2,y2,z2   = point2
    x3,y3,z3,r,_,__ = bounding_sphere
    
    a = (x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2
    b = 2*((x2 - x1) * (x1 - x3) + (y2 - y1) * (y1 - y3) + (z2 - z1) * (z1 - z3))
    c = x3**2 + y3**2 + z3**2 + x1**2 + y1**2 + z1**2 - 2*(x3*x1 + y3*y1 + z3*z1) - r**2
    
    d = b**2 - 4*a*c
    
    if d < 0:
        return False
    
    u1 = -(b+d**0.5)/(2.*a)
    u2 = -(b-d**0.5)/(2.*a)
    
    if ((u1 < 0 and u2 < 0) or (u1 > 1 and u2 > 1)):
        return False
    
    return True
    '''
    a = (x3-x1)*(x2-x1)+(y3-y1)*(y2-y1)+(z3-z1)*(z2-z1)
    b = (x2-x1)**2+(y2-y1)**2+(z2-z1)**2
    
    u = a/b
    
    s1 = x1 + u*(x2-x1)
    s2 = y1 + u*(y2-y1)
    s3 = z1 + u*(z2-z1)
    
    distance = ((s1-x3)**2+(s2-y3)**2+(s3-z3)**2)**0.5
    
    distance1 = ((x1-x3)**2+(y1-y3)**2+(z1-z3)**2)**0.5
    distance2 = ((x2-x3)**2+(y2-y3)**2+(z2-z3)**2)**0.5
    
#    print('distance: ', distance)
    
#    print('u: ', u)
    
#    if d < 0:
    if ((u >= 0 and u <= 1) and distance <= r) or distance1 <= r or distance2 <= r:
        return True
    
    return False
    '''

@njit(types.boolean(types.float64[:],types.float64[:],types.float64[:]), cache=True)
def check_intersection_cylinder(point1, point2, bounding_cylinder):
    # Define the parametric line: P(t) = point1 + t * (point2 - point1)
    x1,y1,z1     = point1
    x2,y2,z2     = point2
    x3,y3,z3,r,h,_ = bounding_cylinder
    
    a = (x2 - x1)**2 + (y2 - y1)**2
    b = 2*((x2 - x1) * (x1 - x3) + (y2 - y1) * (y1 - y3))
    c = (x3 - x1)**2 + (y3 - y1)**2 - r**2
    
    d = b**2 - 4*a*c
    
    if d < 0:
        return False
    
    if (z2 < z3-h and z1 < z3-h) or (z2 > z3+h and z1 > z3+h):
        return False
    
    if (x1-x3)**2+(y1-y3)**2 <= r**2 or \
       (x2-x3)**2+(y2-y3)**2 <= r**2:
        return True
    else:
        if a == 0:
            return False
        u1 = (-b-np.sqrt(d))/(2*a)
        u2 = (-b+np.sqrt(d))/(2*a)
        if ((u1 < 0 and u2 < 0) or (u1 > 1 and u2 > 1)):
            return False
        z_inter_1 = z1+u1*(z2-z1)
        z_inter_2 = z1+u2*(z2-z1)
        if (z_inter_1 >= z3-h and z_inter_1 <= z3+h) or \
           (z_inter_2 >= z3-h and z_inter_2 <= z3+h):
            return True
        else:
            return False

#def flatten_bb_nodes(node):
#    bbs = []
#    uids = [] # Add this line to store the UIDs
#    parents = []
#    children = []
#    _flatten_bb_nodes_helper(node, bbs, uids, parents, children, 0)
#    return np.array(bbs, dtype=np.float64), np.array(uids, dtype=np.int64), (np.array(parents, dtype=np.int64), np.array(children, dtype=np.int64))

#def _flatten_bb_nodes_helper(node, bbs, uids, parents, children, index):
#    bbs.append(node.bounding_box)
#    uids.append(node.uid) # Add this line to store the UID of the node
#    for child in node.children:
#        child_index = len(bbs)
#        parents.append(index)
#        children.append(child_index)
#        _flatten_bb_nodes_helper(child, bbs, uids, parents, children, child_index)

def flatten_bb_nodes(node, target_depth=None):
    max_depth = _get_max_depth(node)
    if target_depth is None:
        target_depth = max_depth
    if target_depth < 0 or target_depth > max_depth:
        raise ValueError(f"Invalid target depth: {target_depth}. Must be between 0 and {max_depth}.")

    bbs = []
    uids = []
    parents = []
    children = []
    detectors = []
    _flatten_bb_nodes_helper(node, bbs, uids, parents, children, detectors,  0, target_depth, 0)
    return (np.array(bbs, dtype=np.float64), np.array(uids, dtype=np.int64),
            np.array(parents, dtype=np.int64), np.array(children, dtype=np.int64),
            np.array(detectors, dtype=np.int64))

def _flatten_bb_nodes_helper(node, bbs, uids, parents, children, detectors, index, target_depth, current_depth):
    bbs.append(node.bounding_box)
    uids.append(node.uid)
    start_index = len(detectors)
    if target_depth is not None and current_depth == target_depth:
        node_detectors = _get_all_detectors(node)
        detectors.append(node_detectors)
        return


    for child in node.children:
        child_index = len(bbs)
        parents.append(index)
        children.append(child_index)
        _flatten_bb_nodes_helper(child, bbs, uids, parents, children, detectors, child_index, target_depth, current_depth + 1)

def _get_all_detectors(node):
    detectors = []
    if len(node.children) == 0:  # If the node is a leaf
        detectors.append(node.uid)  # Assuming the UID of the leaf box is the same as the detector inside
    else:
        for child in node.children:
            detectors.extend(_get_all_detectors(child))
    return detectors

def _get_max_depth(node):
    if len(node.children) == 0:
        return 0
    return 1 + max(_get_max_depth(child) for child in node.children)

@njit(cache=True)
def hierarchical_search(segment, bbs):
    num_nodes = len(bbs)
    point1, point2 = segment
    stack = np.zeros(num_nodes, dtype=np.int64)  # Preallocated stack
    stack[0] = 0  # Start with the root node (world)
    stack_size = 1
    segment_intersections = List.empty_list(int64)  # Typed list for intersections
    while stack_size > 0:
        index = stack[stack_size - 1]  # Get the next node from the stack
        stack_size -= 1
#        print('before check:', index,bbs[index]['bbs'],bbs[index]['box_uid'])
######## FIXME: Perhaps this procedure can be made automatic for all bounding classes
        if bbs[index]['label'] == b'BoundingBox':
#            print('Box: ', point1, point2, bbs[index]['bbs'])
            flag = check_intersection_box(point1, point2, bbs[index]['bbs'])
#            print(flag)
        elif bbs[index]['label'] == b'BoundingCylinder':
#            print('Cylinder: ', point1, point2, bbs[index]['bbs'])
            flag = check_intersection_cylinder(point1, point2, bbs[index]['bbs'])
#            print(flag)
        elif bbs[index]['label'] == b'BoundingSphere':
#            print('Sphere: ', point1, point2, bbs[index]['bbs'])
            flag = check_intersection_sphere(point1, point2, bbs[index]['bbs'])
#            print(flag)
########
        if flag:
            parent_uid = bbs[index]['box_uid']
            child_indices = np.where(bbs['parent'] == parent_uid)[0]  # Find children of the current node
            if len(child_indices) > 0:
                for i, child_index in enumerate(child_indices):
                    stack[stack_size + i] = child_index  # Push child index onto the stack
                stack_size += len(child_indices)
            else:
                segment_intersections.append(index)
    
    return segment_intersections

@njit(parallel=True, cache=True)
def hierarchical_searches(segments, bbs, parents, children):
    num_segments = len(segments)
    intersections = List()  # Typed list for intersections

    for segment_index in prange(num_segments):  # Use prange for parallel execution
        segment = segments[segment_index]
        segment_intersections = hierarchical_search(segment, bbs, parents, children)
        intersections.append((segment_index, segment_intersections))  # Append as a typed list

    return intersections

def check_crossing_vectorized(segments, bbs, parents):
    # Extract points and bounding box coordinates
    point1s = segments[:, 0, :]
    point2s = segments[:, 1, :]
    bb_mins = bbs[:, None, :3]
    bb_maxs = bbs[:, None, 3:]

    # Check if point1 is outside the bounding box
    outside_point1 = np.logical_or.reduce((point1s < bb_mins) | (point1s > bb_maxs), axis=-1)

    # Check if point2 is inside the bounding box
    inside_point2 = np.logical_and.reduce((bb_mins <= point2s) & (point2s <= bb_maxs), axis=-1)

    # Combine the checks
    intersections = outside_point1 & inside_point2

    # Check if the bounding box has children
    has_children = np.isin(np.arange(len(bbs)), parents)

    # Filter the intersections to only include leaf nodes
    leaf_intersections = intersections & ~has_children[:, None]

    # Get the indices of the intersections
    intersection_indices = np.argwhere(leaf_intersections)

    return intersection_indices

@njit(cache=True, error_model="numpy")
def segment_sphere_intersection_new(r1, r2, rc, radius, t1, t2):
    assert t2 >= t1
    assert radius >= 0
    assert r1.shape[0] == 3
    assert r2.shape[0] == 3
    assert rc.shape[0] == 3

    r21 = r2 - r1
    a = np.dot(r21, r21)
    r10 = r1 - rc
    b = np.dot(r21, r10) / a
    dr10_squared = np.dot(r10, r10)
    c = (dr10_squared - radius**2) / a

    if c > 0 or b**2 - c < 0:
        return False, np.zeros(3), 0, np.zeros(3), 1


    d = math.sqrt(b**2 - c)
    s = -b - d
    if s < 0 or s > 1:
        return False, np.zeros(3), 0, np.zeros(3), 0


    hit_point = s * r2 + (1 - s) * r1
    t_hit = t1 + (t2 - t1) * s
    norm = math.sqrt(a)
    unit_direction = -r21 / norm

    return True, hit_point, t_hit, unit_direction, c > 0

@njit(cache=True)
def check_inside(point, bb):
    """
    Check if a point is inside a bounding box.

    Parameters:
    - point: A 3D point represented as a tuple or list of (x, y, z).
    - bb: Bounding box represented as a tuple or list of (x_min, y_min, z_min, x_max, y_max, z_max).

    Returns:
    - True if the point is inside the bounding box, False otherwise.
    """

    x, y, z = point
    x_min, y_min, z_min, x_max, y_max, z_max = bb

    return x_min <= x <= x_max and y_min <= y <= y_max and z_min <= z <= z_max

@njit(cache=True)
def detector_response(wavelength, intersection, effects, effects_options, output_array, uid, self_weight):
    vars = np.array([wavelength, intersection[0], intersection[1], intersection[2], intersection[3], intersection[4], intersection[5], intersection[6]], dtype=np.float64)
    total_effect = 1.0
    effects_options = effects_options[effects_options[:,:,0][:,0] == uid][0]
    for i, effect in enumerate(effects):
        opts = effects_options[i]
        i_effect = effect(vars, opts)
        total_effect *= i_effect
        output_array[i] = i_effect
    total_effect *= self_weight
    
    return total_effect

@report_timing
@njit(parallel=False, cache=True)
def ray_tracer(r, t, w, wt, ta, bboxes_depth, detectors_depth, effects, effects_options):
    # get number of nodes and photons
    (n_photons, steps, dim) = r.shape
    assert dim == 3

    # Create an output array for detector_response
    effects_array = np.empty(len(effects), dtype=np.float64)

    # Initialize a list to store the hits
    hits_list = []
    # loop over n_photons to find their intersections with bounding boxes and sensitive detectors
    for i_photon in prange(n_photons):
        segments = r[i_photon]
        times = t[i_photon]
        t_abs = ta[i_photon]
        wavelength = w[i_photon]
        self_weight = wt[i_photon]
        intersection = path_tracer(segments, times, bboxes_depth, detectors_depth)
        if intersection is not None:
            uid = int(intersection[7])  # detector uid
            travel_time = intersection[3] - times[intersection[3] >= times][0]
            w_noabs = np.exp(-travel_time/t_abs)
            total_effect = detector_response(wavelength, intersection, effects, effects_options, effects_array, uid, self_weight)
            # Flatten the effects_array
            # Append the hit to hits_list
            hit_data = [uid, intersection[3], intersection[0], intersection[1], intersection[2]]
            hit_data.append(i_photon)
            hit_data.append(w_noabs) # for w_noabs
            hit_data.append(self_weight) # for weight
            hits_list.append(hit_data)
            for e in effects_array:
                hit_data.append(e)
            hit_data.append(total_effect)
    return hits_list


@njit(cache=True)
def earliest_intersection(intersections):
    if len(intersections) == 0:
        return None  # Return None if there are no intersections

    earliest_time = np.inf  # Initialize with infinity
    earliest_intersection_data = None

    for intersection in intersections:
        time = intersection[3]  # Assuming the time is the fourth element
        if time < earliest_time:
            earliest_time = time
            earliest_intersection_data = intersection

    return earliest_intersection_data

@njit(cache=True)
def path_tracer(segments, t, bboxes_depth,  detectors_depth):
    (steps, dim) = segments.shape
    assert dim == 3
    found_sphere_intersection = False
    intersections = List()
    # Iterate over each segment to find intersections with bounding boxes and detectors
    for i_step in range(steps-1):
        r1 = segments[i_step]
        r2 = segments[i_step+1]
        if r2[2] < 0.: continue
        t1 = t[i_step]
        t2 = t[i_step+1]
        segment_pair = np.stack((r1, r2), axis=0)  # Create the segment
        # Call hierarchical_search for segment_pair
        box_intersections = hierarchical_search(segment_pair, bboxes_depth)
        intersections_tot = len(box_intersections)
        if intersections_tot == 0:
            continue

        for k in range(intersections_tot):
            box_index = box_intersections[k]
            box_uid = bboxes_depth[box_index]['box_uid']
            #
            # get list of detectors with parent equal to box_uid
            detectors = detectors_depth[detectors_depth['parent_box_uid'] == box_uid]
            for detector in detectors:
                position = detector['position']
                radius   = detector['radius']
                sphere_intersection = segment_sphere_intersection(r1, r2, position, radius, t1, t2)
                if sphere_intersection[0]:
                    found_sphere_intersection = True
                    data = List()
                    [data.append(x) for x in sphere_intersection[1:-1]]
                    data.append(detector['detector_uid'])
                    intersections.append(data)

        if found_sphere_intersection:
            return earliest_intersection(intersections)
    return None
