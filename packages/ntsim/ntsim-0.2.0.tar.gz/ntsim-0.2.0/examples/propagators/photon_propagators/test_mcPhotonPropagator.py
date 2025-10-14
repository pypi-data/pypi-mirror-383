import configargparse
from argparse import Namespace, BooleanOptionalAction
from ntsim.utils.arguments_handling import NestedNamespace

import numpy as np

from ntsim.Medium.base.BaseMediumProperties import BaseMediumProperties
from ntsim.Medium.Medium import Medium
import ntsim.utils.systemofunits as units
from ntsim.utils.gen_utils import unit_vector

from ntsim.IO.gPhotons import gPhotons
from ntsim.Propagators.Factories.PhotonPropagatorFactory import PhotonPropagatorFactory
from ntsim.Propagators.PhotonPropagators.MCPhotonPropagator import mcPhotonPropagatorConfig

import logging.config
from ntsim.utils.logger_config import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')

for key in logging.Logger.manager.loggerDict:
    print(key)
    
logging.getLogger('Medium').setLevel('CRITICAL')

def mcPhotonPropagator_options(opts: NestedNamespace) -> mcPhotonPropagatorConfig:
    return mcPhotonPropagatorConfig(
        n_scatterings = opts.photons.n_scatterings
    )

class MediumProperties(BaseMediumProperties):

    def __init__(self, name: str):
        super().__init__(name)

    def configure(self, opts: Namespace) -> bool:
        """ Configure medium properties based on the provided options. """
        try:
            self.scattering_model        = opts.scat_model
            self.wavelength_nm           = np.linspace(opts.wavelength_range_nm[0],opts.wavelength_range_nm[1],num=100)
            self.scattering_inv_length_m = np.linspace(opts.scattering_inv_length_m[0], opts.scattering_inv_length_m[1], num=100)
            self.absorption_inv_length_m = np.linspace(opts.absorption_inv_length_m[0], opts.absorption_inv_length_m[1], num=100)
            self.group_refraction_index  = np.linspace(opts.group_refraction_index[0], opts.group_refraction_index[1], num=100)
            self.anisotropy              = opts.anisotropy
            return True
        except Exception as e:
            logger.error(f"Failed to configure MediumProperties: {e}")
            return False
        
def generate_photons(opts: Namespace) -> gPhotons:
    photons = gPhotons('mcPhotonPropagator')
    
    n_photons  = int(opts.n_photons)
    n_steps    = int(opts.n_scatterings)
    
    rng        = np.random.default_rng(seed=opts.random_seed)
    
    if opts.set_normal_distr:
        mu_r       = opts.position_m
        sigma_r    = 1.
        cov_matrix = np.eye(N=3)*sigma_r
        r          = rng.multivariate_normal(mu_r,cov_matrix,size=n_photons)
    else:
        r          = np.array([opts.position_m])
        r          = np.repeat(r,repeats=n_photons,axis=0)
    
    t          = np.zeros(shape=n_photons)
    dir        = np.repeat([opts.direction],repeats=n_photons,axis=0)
    dir        = unit_vector(dir)
    wavelength = rng.uniform(low=opts.wavelength_range_nm[0],high=opts.wavelength_range_nm[1],size=n_photons)
    progenitor = np.zeros(shape=n_photons)
    
    photons.add_photons(n_photons,n_steps,r,t,dir,wavelength,progenitor)

    logger.info('photons generated')
    return photons

if __name__ == '__main__':
    # Parse command line arguments
    parser = configargparse.get_argument_parser()
    parser.add('--photons.propagator_name',dest='photon_propagator_name',type=str,default='mcPhotonPropagator',help='')
    parser.add('--photons.random_seed',type=int,default=42,help='random seed for the NumPy random generator')
    parser.add('--photons.n_photons',type=int,default=1000,help='number of optical photons')
    parser.add('--photons.set_normal_distr',action=BooleanOptionalAction,default=False)
    parser.add('--photons.position_m',type=float,nargs=3,default=[0,0,0],help='initial position of optical photons')
    parser.add('--photons.direction',type=float,nargs=3,default=[0,0,1],help='direction of optical photons')
    parser.add('--photons.scat_model',type=str,choices=('HenyeyGreenstein','Rayleigh','HG+Rayleigh','FlatScatteringModel'),default='HenyeyGreenstein', help='scattering model')
    parser.add('--photons.n_scatterings',type=int,default=5,help='number of scattering steps')
    parser.add('--photons.wavelength_range_nm',type=float,nargs=2,default=[350,600],help='wavelength range of optical photons in nm')
    parser.add('--photons.scattering_inv_length_m',type=float,nargs=2,default=[1./(60*units.m),1./(60*units.m)],help='scattering inverse length in m^-1')
    parser.add('--photons.absorption_inv_length_m',type=float,nargs=2,default=[1./(20*units.m),1./(20*units.m)],help='absorption inverse length in m^-1')
    parser.add('--photons.group_refraction_index',type=float,nargs=2,default=[1.34,1.36],help='group refraction index')
    parser.add('--photons.anisotropy',type=float,default=0.88, help='scattering anisotropy')
    
    opts = parser.parse_args(namespace=NestedNamespace())
    
    medium_properties = MediumProperties(name=opts.photons.scat_model)
    medium = Medium(medium_properties)
    medium.configure(opts.photons)
    model = medium.get_model()
    
    photons = generate_photons(opts.photons)

    factory = PhotonPropagatorFactory()
    factory.configure(opts)
    photon_propagator = factory.get_instance()[0]
    photon_propagator.configure(mcPhotonPropagator_options(opts))
    photon_propagator.propagate(photons,medium)