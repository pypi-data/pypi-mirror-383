import numpy as np
import argparse
import abc

import ntsim.utils.systemofunits as units
from ntsim.random import rng
from ntsim.Base.BaseConfig import BaseConfig

def range_theta(arg):
    theta_min = 0.
    theta_max = 180.
    try:
        f = float(arg)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a floating point number")
    if f < theta_min or f > theta_max:
        raise argparse.ArgumentTypeError("Argument must be < " + str(theta_max) + "and > " + str(theta_min))
    return f

def range_phi(arg):
    phi_min = 0.
    phi_max = 360.
    try:
        f = float(arg)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a floating point number")
    if f < phi_min or f > phi_max:
        raise argparse.ArgumentTypeError("Argument must be < " + str(phi_max) + "and > " + str(phi_min))
    return f

class PrimaryGeneratorBase(BaseConfig):
    arg_dict_position = {
        'random_position': {'action': 'store_true', 'help': ''},
        'random_volume': {'type': str, 'choices': ['cylinder'], 'default': 'cylinder', 'help': ''},
        'volume_position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': ''},
        'cylinder_height': {'type': float, 'nargs': '+', 'default': [200.,1360.], 'help': ''},
        'cylinder_radius': {'type': float, 'nargs': '+', 'default': [1000.,1000.], 'help': ''},
        'cylinder_density': {'type': float, 'nargs': '+', 'default': [2.65,1.], 'help': ''},
        'ground_level': {'type': float, 'default': 200., 'help': ''},
        'layers_radius_m': {'type': float, 'nargs': '+', 'default': [1000.,1000.], 'help': ''},
        'layers_weight': {'type': float, 'nargs': '+', 'default': [1.,1.], 'help': ''},
        'set_angular_direction': {'action': 'store_true', 'help': ''},
        'direction_theta': {'type': range_theta, 'default': 0., 'help': ''},
        'direction_phi': {'type': range_phi, 'default': 0., 'help': ''},
    }
    
    def __init__(self, name: str):
        self._name = name
        self.logger.info(f'Initialized Generator')

    @abc.abstractmethod
    def make_event(self, event):
        pass
    
    def set_random_position(self, n_vertices, random_volume):
        
        self._available_random_volumes = {'cylinder': self.random_cylinder}
        self._available_random_options = {'cylinder': [np.array(self.cylinder_height), np.array(self.cylinder_radius),
                                                       np.array(self.cylinder_density), self.ground_level,
                                                       np.array(self.layers_radius_m), np.array(self.layers_weight)]}
        
        random_volumes = self._available_random_volumes[random_volume]
        random_options = self._available_random_options[random_volume]
        
        positions_m = random_volumes(n_vertices, *random_options)
        
        return positions_m
    
    def random_cylinder(self, n_vertices: int, height: np.array, radius: np.array,
                        density: np.array, ground_level: float,
                        layers_radius: np.array, layers_weight: np.array) -> np.array:
        
        gamma_1 = rng.uniform(size=n_vertices)
        
        norm_density         = np.sum(density)
        cylinder_weights     = density/norm_density
        cum_cylinder_weights = np.cumsum(cylinder_weights)
        
        sample_cylinders = np.searchsorted(cum_cylinder_weights, gamma_1)
        
        _, cylinder_counts = np.unique(np.append(sample_cylinders,np.arange(len(cum_cylinder_weights))), return_counts=True)
        cylinder_counts    -= 1
        
        heights = np.repeat(height, cylinder_counts)
        
        shifts = np.cumsum(height)
        shifts = np.repeat(shifts, cylinder_counts)
        shifts = shifts-heights
        
        positions_m  = np.empty(shape=(n_vertices,3))
        weights_func = np.empty(shape=(n_vertices))
        
        idx = 0
        cyl = 0
        
        for n_cylinder, n_sampels in enumerate(cylinder_counts):
            
            idx_layers  = int(np.argwhere(layers_radius[idx:]==radius[n_cylinder])[0])+1
            layer_radii = layers_radius[idx:idx+idx_layers]
            layer_radii = np.append([0.],layer_radii)
            
            layer_weights = layers_weight[idx:idx+idx_layers]
            layer_weights = layer_weights/np.sum(layer_weights)
            cum_layer_weights = np.cumsum(layer_weights)
            
            idx += idx_layers
            
            if not n_sampels: continue
            
            layer_w_uni = (layer_radii[1:]**2-layer_radii[:-1]**2)/layer_radii[-1]**2
            weight_func = 1./layer_weights*layer_w_uni
            
            gamma_2 = rng.uniform(size=n_sampels)
            gamma_3 = rng.uniform(size=n_sampels)
            gamma_4 = rng.uniform(size=n_sampels)
            gamma_5 = rng.uniform(size=n_sampels)
            
            sample_layers = np.searchsorted(cum_layer_weights, gamma_2)
            
            _, layer_counts = np.unique(np.append(sample_layers,np.arange(len(cum_layer_weights))), return_counts=True)
            layer_counts    -= 1
            
            weights_func[cyl:cyl+n_sampels] = np.repeat(weight_func, layer_counts)
            
            layer_split = np.cumsum(layer_counts)[:-1]
            
            gamma_3 = np.split(gamma_3, layer_split)
            gamma_4 = np.split(gamma_4, layer_split)
            
            cylinder_height = heights[cyl:cyl+n_sampels]
            cylinder_shift  = shifts[cyl:cyl+n_sampels]
            
            x = np.empty(shape=n_sampels)
            y = np.empty(shape=n_sampels)
            
            lay = 0
            for n_layer, counts in enumerate(layer_counts):
                phi = 2*np.pi*gamma_4[n_layer]
                rho = np.sqrt((layer_radii[1:][n_layer]**2-layer_radii[:-1][n_layer]**2)*gamma_3[n_layer]+layer_radii[:-1][n_layer]**2)
                x[lay:lay+counts] = rho*np.cos(phi)
                y[lay:lay+counts] = rho*np.sin(phi)
                
                lay += counts
                
            z = cylinder_height*gamma_5+cylinder_shift-ground_level
            
            positions_m[cyl:cyl+n_sampels] = np.array([x,y,z]).T + self.volume_position_m
            
            cyl += n_sampels
        
        return positions_m, weights_func
    
    def angular_direction(self, theta, phi):
        
        direction = np.empty(shape=3)
        
        direction[0] = np.sin(theta*units.deg2rad)*np.cos(phi*units.deg2rad)
        direction[1] = np.sin(theta*units.deg2rad)*np.sin(phi*units.deg2rad)
        direction[2] = np.cos(theta*units.deg2rad)
        
        return direction