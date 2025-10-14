import configargparse
from argparse import Namespace

import matplotlib.pyplot as plt

import numpy as np
import scipy.integrate as integrate

from ntsim.Medium.scattering_models import HenyeyGreenstein, Rayleigh, HGplusRayleigh, FlatScatteringModel
from ntsim.Medium.Medium import Medium
from ntsim.Detector.base.BaseMediumProperties import BaseMediumProperties
import ntsim.utils.systemofunits as units

import logging
logger = logging.getLogger('Medium.Examples')
logformat='[%(name)20s ] %(levelname)8s: %(message)s'
logging.basicConfig(format=logformat)

def plot_pdf(model, filename, g_values=None):
    if g_values is None:
        g_values = [0.99, 0.9, 0.5, 0.0]

    pos = [221, 222, 223, 224]
    for ig in g_values:
        model.g = ig
        result = integrate.quad(lambda x: model.pdf(x), -1, 1)
        print(f"g={ig:>5}, integral: {result}")

    mu = np.linspace(-1, 1, 10000)
    fig = plt.figure(figsize=(12, 8))
    plt.subplots_adjust(hspace=0.4)
    fig.suptitle(f'{model.name} angular distribution', fontsize=14)
    for i in range(4):
        ax = plt.subplot(pos[i])
        model.g = g_values[i]
        plt.plot(mu, model.pdf(mu), label='pdf')
        plt.plot(mu, model.cdf(mu), label=f'cdf')
        mu_random = model.random_mu(sample=100000)
        plt.hist(mu_random, bins=2000, density=True)
        plt.legend(loc='best')
        plt.grid(True)
        plt.gca().set_xlabel(r'$\cos\;\theta$')
        plt.yscale('log')
        ax.title.set_text(f'g={g_values[i]:>5}')
    plt.savefig(filename)

class MediumProperties(BaseMediumProperties):

    def __init__(self, name: str):
        super().__init__(name)

    def configure(self, opts: Namespace) -> bool:
        """Configure medium properties based on the provided options. """
        try:
            # Set wavelength range
            self.wavelength_nm = np.linspace(opts.waves[0], opts.waves[1], num=100)

            # Set scattering_inv_length_m
            self.scattering_inv_length_m = np.linspace(opts.scattering_inv_length_m[0], opts.scattering_inv_length_m[1], num=100)

            # Set absorption_inv_length_m
            self.absorption_inv_length_m = np.linspace(opts.absorption_inv_length_m[0], opts.absorption_inv_length_m[1], num=100)

            # Set group_refraction_index
            self.group_refraction_index = np.linspace(opts.group_refraction_index[0], opts.group_refraction_index[1], num=100)

            # Set anisotropy
            self.anisotropy = opts.anisotropy

            return True
        except Exception as e:
            self.log.error(f"Failed to configure MediumProperties: {e}")
            return False

def pdf_filename(name):
    names = {'HenyeyGreenstein':'angular_HenyeyGreenstein.pdf','Rayleigh':'angular_Rayleigh.pdf',
             'HG+Rayleigh':'angular_HGRayleigh.pdf','FlatScatteringModel':'angular_FlatScatteringModel.pdf'}
    if name in names:
        return names[name]
    else:
        logger.info(f'known models: {names.keys()}')
        logger.error(f'unknown model name: {name}')

if __name__ == "__main__":
    # Parse command line arguments
    from ntsim.utils.arguments_handling import NestedNamespace
    parser = configargparse.get_argument_parser()
    parser.add('--model', type=str, choices=('HenyeyGreenstein','Rayleigh','HG+Rayleigh','FlatScatteringModel'),default='HenyeyGreenstein', help='scattering model')
    parser.add('--scattering_inv_length_m', type=float, nargs=2, default=[1./(10*units.m),1./(40*units.m)], help='scattering inverse length in m^-1')
    parser.add('--absorption_inv_length_m', type=float, nargs=2, default=[1./(20*units.m),1./(100*units.m)], help='absorption inverse length in m^-1')
    parser.add('--group_refraction_index', type=float, nargs=2, default=[1.34,1.36], help='group refraction index')
    parser.add('--anisotropy', type=float, default=0.88, help='scattering anisotropy')
    parser.add('--waves', type=float, default=[350,600], help='wavelengths in nm')

    parser.add('--show-pdf', action='store_true', help='Show probability density function.')
    parser.add('--output-dir', type=str, default='plots/', help='Output directory for plots')


    opts = parser.parse_args(namespace=NestedNamespace())
    medium_properties = MediumProperties(name=opts.model)
    medium = Medium(medium_properties)
    medium.configure(opts)
    model = medium.get_model()
    import os
    if not os.path.exists(opts.output_dir):
        os.makedirs(opts.output_dir)

    if opts.show_pdf:
        filename = opts.output_dir + pdf_filename(model.name)
        plot_pdf(model,filename)
