"""
Put all of the necessary post-processing functions here

	Written by A L Danhaive: ald66@cam.ac.uk
"""

__all__ = ['process_results']

# imports
from . import  preprocess as pre
from . import  fitting as fit

from . import  utils

from matplotlib import pyplot as plt

import jax.numpy as jnp
from jax import image
import numpyro

import arviz as az

import numpy as np

from jax.scipy.signal import convolve

import argparse

from astropy.cosmology import Planck18 as cosmo

import xarray as xr

from astropy.table import Table

import corner

# import smplotlib

def save_fit_results(output, inf_data, kin_model, z_spec, ID, v_re_med, v_re_16, v_re_84, save_runs_path):
	''' 
		Save all of the best-fit parameters in a table
	'''
	#compute v/sigma posterior and quantiles
	inf_data.posterior['v_sigma'] = inf_data.posterior['v_re'] / inf_data.posterior['sigma0']
	v_sigma_16 = jnp.array(inf_data.posterior['v_sigma'].quantile(0.16, dim=["chain", "draw"]))
	v_sigma_med = jnp.array(inf_data.posterior['v_sigma'].median(dim=["chain", "draw"]))
	v_sigma_84 = jnp.array(inf_data.posterior['v_sigma'].quantile(0.84, dim=["chain", "draw"]))

	#compute Mdyn posterior and quantiles
	pressure_cor = 3.35 #= 2*re/rd
	inf_data.posterior['v_circ2'] = inf_data.posterior['v_re']**2 + inf_data.posterior['sigma0']**2*pressure_cor
	inf_data.posterior['v_circ'] = np.sqrt(inf_data.posterior['v_circ2'])
	ktot = 1.8 #for q0 = 0.2
	G = 4.3009172706e-3 #gravitational constant in pc*M_sun^-1*(km/s)^2
	DA = cosmo.angular_diameter_distance(z_spec).to('m')
	meters_to_pc = 3.086e16
	# Convert arcseconds to radians and calculate the physical size
	inf_data.posterior['r_eff_pc'] = np.deg2rad(inf_data.posterior['r_eff']*0.06/3600)*DA.value/meters_to_pc
	inf_data.posterior['M_dyn'] = np.log10(ktot*inf_data.posterior['v_circ2']*inf_data.posterior['r_eff_pc']/G)

	M_dyn_16 = jnp.array(inf_data.posterior['M_dyn'].quantile(0.16, dim=["chain", "draw"]))
	M_dyn_med = jnp.array(inf_data.posterior['M_dyn'].median(dim=["chain", "draw"]))
	M_dyn_84 = jnp.array(inf_data.posterior['M_dyn'].quantile(0.84, dim=["chain", "draw"]))

	v_circ_16 = jnp.array(inf_data.posterior['v_circ'].quantile(0.16, dim=["chain", "draw"]))
	v_circ_med = jnp.array(inf_data.posterior['v_circ'].median(dim=["chain", "draw"]))
	v_circ_84 = jnp.array(inf_data.posterior['v_circ'].quantile(0.84, dim=["chain", "draw"]))

	#save results to a file
	params= ['ID', 'PA_50', 'i_50', 'Va_50', 'r_t_50', 'sigma0_50', 'v_re_50', 'amplitude_50', 'r_eff_50', 'n_50','PA_morph_50', 'PA_16', 'i_16', 'Va_16', 'r_t_16', 'sigma0_16', \
	  'v_re_16', 'PA_84', 'i_84', 'Va_84', 'r_t_84', 'sigma0_84', 'v_re_84', 'v_sigma_16', 'v_sigma_50', 'v_sigma_84', 'M_dyn_16', 'M_dyn_50', 'M_dyn_84', \
		'vcirc_16', 'vcirc_50', 'vcirc_84', 'r_eff_16', 'r_eff_84', 'ellip_50', 'ellip_16', 'ellip_84', 'x0_vel_16', 'x0_vel_50', 'x0_vel_84', 'y0_vel_16', 'y0_vel_50', 'y0_vel_84', \
			'xc_morph_16', 'xc_morph_50', 'xc_morph_84', 'yc_morph_16', 'yc_morph_50', 'yc_morph_84', 'amplitude_16', 'amplitude_84', 'n_16', 'n_84']
	t_empty = np.zeros((len(params), 1))
	res = Table(t_empty.T, names=params)
	res['ID'] = ID
	res['PA_50'] = kin_model.PA_mean
	res['i_50'] = kin_model.i_mean
	res['Va_50'] = kin_model.Va_mean
	res['r_t_50'] = kin_model.r_t_mean
	res['sigma0_50'] = kin_model.sigma0_mean_model
	res['v_re_50'] = v_re_med
	res['amplitude_50'] = kin_model.amplitude_mean
	res['r_eff_50'] = kin_model.r_eff_mean
	res['n_50'] = kin_model.n_mean
	res['PA_morph_50'] = kin_model.PA_morph_mean
	res['v_sigma_50'] = v_sigma_med

	res['PA_16'] = kin_model.PA_16
	res['i_16'] = kin_model.i_16
	res['Va_16'] = kin_model.Va_16
	res['r_t_16'] = kin_model.r_t_16
	res['sigma0_16'] = kin_model.sigma0_16
	res['v_re_16'] = v_re_16
	res['v_sigma_16'] = v_sigma_16

	res['PA_84'] = kin_model.PA_84
	res['i_84'] = kin_model.i_84
	res['Va_84'] = kin_model.Va_84
	res['r_t_84'] = kin_model.r_t_84
	res['sigma0_84'] = kin_model.sigma0_84
	res['v_re_84'] = v_re_84
	res['v_sigma_84'] = v_sigma_84

	res['M_dyn_16'] = M_dyn_16
	res['M_dyn_50'] = M_dyn_med
	res['M_dyn_84'] = M_dyn_84

	res['vcirc_16'] = v_circ_16
	res['vcirc_50'] = v_circ_med
	res['vcirc_84'] = v_circ_84

	res['r_eff_16'] = kin_model.r_eff_16
	res['r_eff_84'] = kin_model.r_eff_84

	res['ellip_50'] = kin_model.ellip_mean
	res['ellip_16'] = kin_model.ellip_16
	res['ellip_84'] = kin_model.ellip_84

	res['x0_vel_16'] = kin_model.x0_vel_16
	res['x0_vel_50'] = kin_model.x0_vel_mean
	res['x0_vel_84'] = kin_model.x0_vel_84

	res['y0_vel_16'] = kin_model.y0_vel_16
	res['y0_vel_50'] = kin_model.y0_vel_mean
	res['y0_vel_84'] = kin_model.y0_vel_84

	res['xc_morph_16'] = kin_model.xc_morph_16
	res['xc_morph_50'] = kin_model.xc_morph_mean
	res['xc_morph_84'] = kin_model.xc_morph_84

	res['yc_morph_16'] = kin_model.yc_morph_16
	res['yc_morph_50'] = kin_model.yc_morph_mean
	res['yc_morph_84'] = kin_model.yc_morph_84

	res['amplitude_16'] = kin_model.amplitude_16
	res['amplitude_84'] = kin_model.amplitude_84

	res['n_16'] = kin_model.n_16
	res['n_84'] = kin_model.n_84

	res.write(save_runs_path + output + '/' + str(ID) + '_results', format='ascii', overwrite=True)

	#save a cornerplot of the v_sigma and sigma posteriors
	fig = plt.figure(figsize=(10, 10))
	CORNER_KWARGS = dict(
		smooth=4,
		label_kwargs=dict(fontsize=20),
		title_kwargs=dict(fontsize=20),
		quantiles=[0.16, 0.5, 0.84],
		plot_density=False,
		plot_datapoints=False,
		fill_contours=True,
		plot_contours=True,
		show_titles=True,
		labels=[r'$v_{re}/\sigma$', r'$\sigma_0$ [km/s]',  r'$\log ( M_{dyn} [M_{\odot}])$', r'$v_{circ}$ [km/s]'],
		titles= [r'$v_{re}/\sigma$ ', r'$\sigma_0$', r'$\log M_{dyn}$',r'$v_{circ}$'],
		max_n_ticks=3,
		divergences=False)

	figure = corner.corner(inf_data, group='posterior', var_names=['v_sigma','sigma0', 'M_dyn', 'v_circ'],
						color='dodgerblue', **CORNER_KWARGS)
	plt.tight_layout()
	plt.savefig(save_runs_path + output + '/' + str(ID)+'_v_sigma_corner.png', dpi=300)
	plt.close()


def process_results(output, master_cat, line,  mock_params = None, test = None, j = None, parametric = False, ID = None, save_runs_path = None,
                     field=None, grism_filter='F444W', delta_wave_cutoff=0.02, factor=5, wave_factor=10, model_name='Disk',
                     manual_psf_name=None, manual_grism_file=None):
	"""
		Main function that automatically post-processes the inference data and saves all of the relevant plots
		Returns the main data products so that data can be analyzed separately

		Parameters
		----------
		manual_psf_name : str, optional
			PSF filename (required if field='manual')
		manual_grism_file : str, optional
			Grism spectrum filename (required if field='manual')
	"""

	#pre-process the galaxy data
	z_spec, wavelength, wave_space, obs_map, obs_error, kin_model, grism_object, delta_wave = pre.run_full_preprocessing(
		output, master_cat, line, mock_params=mock_params, save_runs_path=save_runs_path,
		source_id=ID, field=field, grism_filter=grism_filter, delta_wave_cutoff=delta_wave_cutoff,
		factor=factor, wave_factor=wave_factor, model_name=model_name,
		manual_psf_name=manual_psf_name, manual_grism_file=manual_grism_file)

	#load inference data
	if mock_params is None:
		# inf_data = az.InferenceData.from_netcdf('FrescoHa/Runs-Final/' + output + '/'+ 'output')
		inf_data = az.InferenceData.from_netcdf(save_runs_path + output + '/' + str(ID) + '_output')
		j=0
	else:
		inf_data = az.InferenceData.from_netcdf('testing/' + str(test) + '/' + str(test) + '_' + str(j) + '_'+ 'output')
		
	num_samples = inf_data.posterior['sigma0'].shape[1]
	data = fit.Fit_Numpyro(obs_map = obs_map, obs_error = obs_error, grism_object = grism_object, kin_model = kin_model, inference_data = inf_data , parametric = parametric)
	inf_data, model_map,  model_flux, fluxes_mean, model_velocities, model_dispersions = kin_model.compute_model(inf_data, grism_object,parametric)
	#define the wave_space
	index_min = grism_object.index_min
	index_max = grism_object.index_max
	len_wave = int((wave_space[len(wave_space)-1] - wave_space[0])/(delta_wave))
	wave_space = jnp.linspace(wave_space[0], wave_space[len(wave_space)-1], len_wave+1)
	wave_space = wave_space[index_min:index_max]

	#save the posterior of the velocity at the effective radius
	inf_data, v_re_16, v_re_med, v_re_84 = utils.add_v_re(inf_data, kin_model, grism_object, num_samples)



	# compute v/sigma posterior and quantiles

	# Get number of chains from the inference data
	num_chains = inf_data.posterior['sigma0'].shape[0]
	num_samples_prior = inf_data.prior['sigma0'].shape[1]

	inf_data.posterior['sigma0_trunc'] = xr.DataArray(np.zeros((num_chains, num_samples)), dims = ('chain', 'draw'))
	inf_data.prior['sigma0_trunc'] = xr.DataArray(np.zeros((1, num_samples_prior)), dims = ('chain', 'draw'))
	for i in range(num_chains):
		for sample in range(num_samples):
			if inf_data.posterior['sigma0'].quantile(0.16) <= 30:
				inf_data.posterior['sigma0_trunc'][i,sample] = np.random.uniform(inf_data.posterior['sigma0'].quantile(0.84), 0.5*inf_data.posterior['sigma0'].quantile(0.16))
			else:
				inf_data.posterior['sigma0_trunc'][i,sample] = inf_data.posterior['sigma0'][i,sample]

	# Process prior samples separately
	for sample in range(num_samples_prior):
		if inf_data.posterior['sigma0'].quantile(0.16) <= 30:
			inf_data.prior['sigma0_trunc'][0,sample] = np.random.uniform(inf_data.prior['sigma0'].quantile(0.84), 0.5*inf_data.prior['sigma0'].quantile(0.16))
		else:
			inf_data.prior['sigma0_trunc'][0,sample] = inf_data.prior['sigma0'][0,sample]
				
	inf_data.posterior['v_sigma'] = inf_data.posterior['v_re'] / inf_data.posterior['sigma0_trunc']
	inf_data['prior']['v_sigma'] = inf_data.prior['v_re'] / inf_data.prior['sigma0_trunc']
	v_sigma_16 = jnp.array(inf_data.posterior['v_sigma'].quantile(0.16, dim=["chain", "draw"]))
	v_sigma_med = jnp.array(inf_data.posterior['v_sigma'].median(dim=["chain", "draw"]))
	v_sigma_84 = jnp.array(inf_data.posterior['v_sigma'].quantile(0.84, dim=["chain", "draw"]))
	
	#save the best fit parameters in a table

	save_fit_results(output, inf_data, kin_model, z_spec, ID, v_re_med, v_re_16, v_re_84, save_runs_path = save_runs_path)
	
	kin_model.plot_summary(obs_map, obs_error, inf_data, wave_space, save_to_folder = output, name = 'summary', v_re = v_re_med, save_runs_path = save_runs_path, ID = ID)

	return  v_re_16, v_re_med, v_re_84, kin_model, inf_data


parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, default='',
					help='folder of the galaxy you want to postprocess')
parser.add_argument('--line', type=str, default='H_alpha',
					help='line to fit')        
parser.add_argument('--master_cat', type=str, default='CONGRESS_FRESCO/master_catalog.cat',
					help = 'master catalog file to use for the post-processing')                                                                                  	

if __name__ == "__main__":

	#run the post-processing hands-off 
	args = parser.parse_args()
	output = args.output
	line = args.line
	master_cat = args.master_cat

	inf_data = az.InferenceData.from_netcdf('fitting_results/' + output + '/'+ 'output')
	process_results(output,master_cat,line)
