# Scattering Models Example

This example demonstrates the usage of different scattering models available in the `ntsim` package. The models include `HenyeyGreenstein`, `Rayleigh`, `HG+Rayleigh`, and `FlatScatteringModel`.

## Overview

The script allows users to:

- Configure medium properties such as wavelength range, scattering inverse length, absorption inverse length, group refraction index, and anisotropy.
- Plot the probability density function (PDF) of the selected scattering model.

## Prerequisites

Ensure you have the following libraries installed:

- `configargparse`
- `numpy`
- `matplotlib`
- `scipy`

## Usage

To run the example:

```bash
python3 exampleScatteringModels.py [OPTIONS]
```

### Options:

- `--model`: Choose the scattering model. Options: `HenyeyGreenstein`, `Rayleigh`, `HG+Rayleigh`, `FlatScatteringModel`. Default is `HenyeyGreenstein`.
- `--scattering_inv_length_m`: Define the scattering inverse length in m^-1. Default is `[1./(10*units.m),1./(40*units.m)]`.
- `--absorption_inv_length_m`: Define the absorption inverse length in m^-1. Default is `[1./(20*units.m),1./(100*units.m)]`.
- `--group_refraction_index`: Set the group refraction index. Default is `[1.34,1.36]`.
- `--anisotropy`: Define the scattering anisotropy. Default is `0.88`.
- `--waves`: Set the wavelengths in nm. Default is `[350,600]`.
- `--show-pdf`: If set, the probability density function will be displayed.
- `--output-dir`: Define the output directory for plots. Default is `plots/`.

### Example:

To run the script with the `HG+Rayleigh` model and display the PDF:

```bash
python3 exampleScatteringModels.py --model HG+Rayleigh --show-pdf
```

## Output

The script will generate a plot of the probability density function for the selected scattering model and save it in the specified output directory.
