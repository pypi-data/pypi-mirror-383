"""

	Module holding all of the kinematic models used in the fitting process.

	Written by A L Danhaive: ald66@cam.ac.uk
"""
__all__ = ["KinModels"]

# imports
import numpy as np
# geko related imports
from . import  utils
from . import  plotting

# jax and its functions
import jax
import jax.numpy as jnp
from jax.scipy.stats import norm
from jax.scipy.signal import convolve
# from scipy.signal import convolve
from jax import image

# from skimage.morphology import dilation, disk

from astropy.modeling.models import GeneralSersic2D, Sersic2D

# scipy and its functions
from scipy.constants import pi
from scipy.ndimage import measurements

# numpyro and its functions
import numpyro
import numpyro.distributions as dist
from numpyro.distributions.transforms import AffineTransform
from numpyro.infer.reparam import TransformReparam, CircularReparam, LocScaleReparam

from matplotlib import pyplot as plt

from photutils import centroids

from astropy.cosmology import Planck18 as cosmo

import time

from scipy.constants import c

import math
import xarray as xr
jax.config.update('jax_enable_x64', True)
# numpyro.enable_validation()  # Disabled for performance - only enable for debugging

# ============================================================================
# STANDALONE JIT-COMPILED FUNCTIONS (extracted from class methods)
# ============================================================================

@jax.jit
def _v_rad_core(x, y, PA, i, Va, r_t, r):
	"""Core computation for radial velocity (extracted from KinModels.v_rad)"""
	return (2/pi)*Va*jnp.arctan(r/r_t)*jnp.sin(i)


@jax.jit  
def _vel1d_core(r, Va, r_t):
	"""Core computation for 1D velocity profile (extracted from KinModels.vel1d)"""
	r_t_safe = jnp.where(r_t != 0.0, r_t, 1.0)
	r_safe = jnp.where(r != 0.0, r, 1.0)
	v_out = jnp.where((r_t!=0.0) & (r!=0.0), (2.0/jnp.pi)*Va*jnp.arctan2(r_safe,r_t_safe), 0.0)
	return jnp.array(v_out)


@jax.jit
def _v_core(x, y, PA, i, Va, r_t):
	"""Core computation for velocity field (extracted from KinModels.v)"""
	i_rad = i / 180 * jnp.pi
	PA_rad = PA / 180 * jnp.pi
	
	# Precompute trigonometric values
	sini = jnp.sin(i_rad)
	cosi = jnp.cos(i_rad)
	
	# Rotate coordinates
	x_rot = x * jnp.cos(PA_rad) - y * jnp.sin(PA_rad)
	y_rot = x * jnp.sin(PA_rad) + y * jnp.cos(PA_rad)
	
	# Safeguard for cases where cosi is zero
	i_rad_safe = jnp.where(cosi != 0, i_rad, 0)
	cosi_safe = jnp.where(cosi != 0, cosi, 1e-6)  # Use a small epsilon to avoid division by zero
	
	# Calculate r, handling x_rot = 0 and y_rot = 0 cases separately
	r_squared = x_rot**2 / cosi_safe**2 + y_rot**2
	r_safe_squared = jnp.where(r_squared != 0.0, r_squared, 1e-12)  # Small epsilon to avoid sqrt(0)
	r = jnp.sqrt(r_safe_squared)
	
	# Handle the special case where r = 0 or where both x_rot and y_rot are 0 explicitly
	r_safe = jnp.where((x_rot != 0) | (y_rot != 0), r, 1e-6)  # Use a small epsilon for r when both x_rot and y_rot are zero
	
	# Calculate observed velocity using the standalone vel1d function
	vel_obs = jnp.where(cosi != 0, _vel1d_core(r_safe, Va, r_t) * sini, _vel1d_core(x_rot, Va, r_t))
	
	# Final velocity computation, handling r = 0 or x_rot = y_rot = 0 case
	vel_obs_final = jnp.where(r_safe != 0.0, vel_obs * (y_rot / r_safe), 0.0)
	
	return vel_obs_final


@jax.jit
def _v_int_core(x, y, PA, i, Va, r_t):
	"""Core computation for integrated velocity field (extracted from KinModels.v_int)"""
	i_rad = i / 180 * jnp.pi
	PA_rad = PA / 180 * jnp.pi
	
	# Precompute trigonometric values
	sini = jnp.sin(i_rad)
	cosi = jnp.cos(i_rad)
	
	# Rotate coordinates
	x_rot = x * jnp.cos(PA_rad) - y * jnp.sin(PA_rad)
	y_rot = x * jnp.sin(PA_rad) + y * jnp.cos(PA_rad)
	
	# Safeguard for cases where cosi is zero
	i_rad_safe = jnp.where(cosi != 0, i_rad, 0)
	cosi_safe = jnp.where(cosi != 0, cosi, 1e-6)  # Use a small epsilon to avoid division by zero
	
	# Calculate r, handling x_rot = 0 and y_rot = 0 cases separately
	r_squared = x_rot**2 / cosi_safe**2 + y_rot**2
	r_safe_squared = jnp.where(r_squared != 0.0, r_squared, 1e-12)  # Small epsilon to avoid sqrt(0)
	r = jnp.sqrt(r_safe_squared)
	
	# Handle the special case where r = 0 or where both x_rot and y_rot are 0 explicitly
	r_safe = jnp.where((x_rot != 0) | (y_rot != 0), r, 1e-6)  # Use a small epsilon for r when both x_rot and y_rot are zero
	
	# Calculate observed velocity using the standalone vel1d function
	vel_obs = jnp.where(cosi != 0, _vel1d_core(r_safe, Va, r_t) * sini, _vel1d_core(x_rot, Va, r_t))
	
	# Final velocity computation, handling r = 0 or x_rot = y_rot = 0 case
	vel_obs_final = jnp.where(r_safe != 0.0, vel_obs * (y_rot / r_safe), 0.0)
	
	return vel_obs_final

# ============================================================================

class KinModels:
	'''
		This top level class only contains the functions to make the velocity maps. The rest will be specific to each sub class.
	'''


	def __init__(self):
		"""
		Initialize a new kinematic model.

		Creates a base kinematic model object with velocity field calculations
		using arctangent rotation curve parameterization.
		"""
		print('New kinematic model created')
	
	def v_rad(self, x, y, PA, i, Va, r_t, r):
		"""Radial velocity component"""
		return _v_rad_core(x, y, PA, i, Va, r_t, r)


	def v(self, x, y, PA, i, Va, r_t):
		"""2D velocity field calculation"""
		return _v_core(x, y, PA, i, Va, r_t)
	
	def v_int(self, x, y, PA, i, Va, r_t):
		"""Integrated velocity field calculation"""
		return _v_int_core(x, y, PA, i, Va, r_t)
	


	def vel1d(self, r, Va, r_t):
		"""1D velocity profile"""
		return _vel1d_core(r, Va, r_t)


		# return dispersions

		

	def set_main_bounds(self, factor, wave_factor, x0, x0_vel, y0, y0_vel):
		"""
		Set basic configuration parameters for the kinematic model.

		Parameters
		----------
		factor : int
			Spatial oversampling factor
		wave_factor : int
			Wavelength oversampling factor
		x0, y0 : float
			Morphological centroid positions (pixels)
		x0_vel, y0_vel : float
			Velocity centroid positions (pixels)

		Notes
		-----
		All priors (morphological and kinematic) are set separately via
		set_priors_from_config() or set_parametric_priors().
		"""
		self.factor = factor
		self.wave_factor = wave_factor

		# Centroid positions
		self.x0 = x0
		self.y0 = y0
		self.x0_vel = x0_vel
		self.mu_y0_vel = y0_vel

		# Default velocity centroid to morphological centroid if not provided
		if self.mu_y0_vel is None:
			self.x0_vel = x0
			self.mu_y0_vel = y0

	def rescale_to_mask(self, array, mask):
		"""
			Rescale the bounds to the mask
		"""
		rescaled_array = []
		for a in array:
			a = a[jnp.where(mask == 1)]
			rescaled_array.append(a)
		return rescaled_array

@numpyro.handlers.reparam(
	config={"PA_radians": CircularReparam()} #, "i_radians": CircularReparam()} #, "y0_vel": TransformReparam()}
)

class Disk():
	"""
	Disk kinematic and morphological model for parametric fitting.

	Represents a single galactic disk with Sersic morphology and arctangent
	rotation curve. Handles prior setting, parameter sampling, and model
	evaluation for MCMC fitting.

	Parameters
	----------
	direct_shape : tuple or int
		Shape of the direct image
	factor : int
		Spatial oversampling factor
	x0_vel : float
		Initial guess for x-velocity center
	mu_y0_vel : float
		Initial guess for y-velocity center
	r_eff : float
		Effective radius in pixels

	Attributes
	----------
	im_shape : tuple
		Image dimensions
	factor : int
		Oversampling factor
	x0 : float
		Morphological x-center
	y0 : float
		Morphological y-center
	"""
	def __init__(self, direct_shape, factor,  x0_vel, mu_y0_vel, r_eff):
		print('Disk object created')

		#initialize all attributes with function parameters
		self.direct_shape = direct_shape


		self.x0_vel = direct_shape[1]//2
		self.mu_y0_vel = mu_y0_vel

		self.r_eff = r_eff

		self.factor = factor


		# self.print_priors()
	
	def print_priors(self):
		print('Priors for disk model')
		print('fluxes --- Truncated Normal w/ flux scaling')
		print('fluxes scaling --- Uniform w/ bounds: ' + str(0.05) + ' ' + str(2))
		print( 'PA --- Normal w/ mu: ' + str(self.mu_PA) + ' and sigma: ' + str(self.sigma_PA))
		print( 'i --- Truncated Normal w/ mu: ' + str(self.mu_i) + ' and sigma: ' + str(self.sigma_i) + ' and bounds: ' + str(self.i_bounds))
		print(f'Va --- Uniform w/ bounds: [{self.Va_min}, {self.Va_max}]')
		print(f'r_t --- TruncatedNormal w/ mu: {self.r_eff_mu} and bounds: [0.1, {self.r_eff_mu}]')
		print(f'sigma0 --- Uniform w/ bounds: [{self.sigma0_min}, {self.sigma0_max}]')
		print('y0_vel --- Truncated Normal w/ mu: ' + str(self.mu_y0_vel) + ' and sigma: ' + str(self.y0_std) + ' and bounds: ' + str(self.y_low) + ' ' + str(self.y_high))
		print('v0 --- Normal w/ mu: 0 and sigma: 100')

	def set_parametric_priors(self,py_table, flux_measurements, redshift, wavelength, delta_wave, theta_rot = 0.0, shape = 31):
		"""
		Set morphological and kinematic priors from PySersic fitting results.

		Extracts morphological parameters from PySersic Sersic profile fits and
		sets priors for both morphology (PA, inclination, r_eff, n, etc.) and
		kinematics (Va, sigma0 bounds). Handles coordinate rotation to align
		imaging and grism reference frames.

		Parameters
		----------
		py_table : astropy.table.Table
			PySersic fit results table with columns like 'r_eff_q50', 'ellip_q50', etc.
		flux_measurements : list of float
			[integrated_flux, flux_error] in erg/s/cm2
		redshift : float
			Spectroscopic redshift
		wavelength : float
			Observed emission line wavelength in microns
		delta_wave : float
			Wavelength pixel scale in microns at native resolution
		theta_rot : float, optional
			Rotation angle in radians to align image with grism (default: 0.0)
		shape : int, optional
			Size of model image (default: 31)

		Notes
		-----
		This method:
		- Converts PySersic results to geko parameter space
		- Rotates coordinates by theta_rot to match grism orientation
		- Sets Gaussian priors for morphology (PA, inc, r_eff, n, amplitude, xc, yc)
		- Sets uniform prior bounds for kinematics from config defaults
		- Stores all prior parameters as class attributes (e.g., self.PA_morph_mu)
		"""
		#need to set sizes in kpc before converting to arcsecs then pxs
		arcsec_per_kpc = cosmo.arcsec_per_kpc_proper(redshift).value
		kpc_per_pixel = 0.063/arcsec_per_kpc

		ellip = py_table['ellip_q50'][0] 
		# inclination = jnp.arccos(1-ellip)*180/jnp.pi
		inclination = utils.compute_inclination(ellip=ellip, q0 = 0.2) #q0=0.2 for a thick disk
		# ellip_err = ((py_table['ellip_q84'][0] - py_table['ellip_q50'][0]) + (py_table['ellip_q50'][0] - py_table['ellip_q16'][0]))/2
		# inclination_err = (((jnp.arccos(1-py_table['ellip_q84'][0]) - jnp.arccos(1-py_table['ellip_q50'][0])) + (jnp.arccos(1-py_table['ellip_q50'][0]) - jnp.arccos(1-py_table['ellip_q16'][0])))/2)*180/jnp.pi
		inclination_err = ( (utils.compute_inclination(ellip = py_table['ellip_q84'][0], q0 = 0.2) - inclination) + (inclination - utils.compute_inclination(ellip = py_table['ellip_q16'][0], q0 = 0.2)) )/2

		inclination_std = inclination_err #*2 #no x2 bc this is an accurate measurement!
		# ellip_std =   ellip_err/2.36

		#because the F115W is fit with the 0.03 resolution, r_eff is twice too big

		r_eff_UV = py_table['r_eff_q50'][0]/2
		r_eff_Ha = r_eff_UV
		r_eff_UV_err = ((py_table['r_eff_q84'][0] - py_table['r_eff_q50'][0]) + (py_table['r_eff_q50'][0] - py_table['r_eff_q16'][0]))/4
		#combine the uncertainties from measurements and scaling relation
		r_eff_std = np.maximum(3,r_eff_Ha) #r_eff_Ha*np.sqrt((r_eff_UV_err/r_eff_UV)**2 + (nUV_to_Ha_std/nUV_to_Ha)**2)*2 #adding uncertainity of 2 to broaden prior

		#compute hard bounds for r_eff in kpc to not be too small or too big
		r_eff_min_kpc = 0.1 
		r_eff_max_kpc = 10
		#convert to pixels
		r_eff_min = r_eff_min_kpc/kpc_per_pixel
		r_eff_max = r_eff_max_kpc/kpc_per_pixel

		n = py_table['n_q50'][0]
		n_err = ((py_table['n_q84'][0] - py_table['n_q50'][0]) + (py_table['n_q50'][0] - py_table['n_q16'][0]))/2
		n_std = 1

		#try taking n from grism too
		# n = py_grism_table['n_q50'][0]
		# n_err = ((py_grism_table['n_q84'][0] - py_grism_table['n_q50'][0]) + (py_grism_table['n_q50'][0] - py_grism_table['n_q16'][0]))/2
		# n_std = n_err/2.36

		#get the flux prior from the integrated line measurements
		int_flux, int_flux_err = flux_measurements
		amplitude =  utils.int_flux_to_flux_density(int_flux,wavelength, delta_wave) #convert the integrated flux to a flux density
		amplitude_std = utils.int_flux_to_flux_density(int_flux,wavelength, delta_wave) #convert the integrated flux to a flux density uncertainty

		#central pixel from image
		 #because the F115W is fit with the 0.03 resolution, the centroids are twice too big
		 #but also, the fit is done on a 40x40 image and we want the center on a 31x31 image 
		xc_morph_py = py_table['xc_q50'][0]/2
		xc_morph = xc_morph_py + (shape-20)/2  #convert to the center of the 31x31 image
		xc_err = ((py_table['xc_q84'][0] - py_table['xc_q50'][0]) + (py_table['xc_q50'][0] - py_table['xc_q16'][0]))/4
		#set the uncertainties in the scale of the effective radius
		xc_std = 0.25*r_eff_Ha #boosting the uncertainties on the centroids to have a looser prior

		yc_morph_py = py_table['yc_q50'][0]/2
		yc_morph = yc_morph_py + (shape-20)/2  #convert to the center of the 31x31 image
		yc_err = ((py_table['yc_q84'][0] - py_table['yc_q50'][0]) + (py_table['yc_q50'][0] - py_table['yc_q16'][0]))/4
		yc_std = 0.25*r_eff_Ha #boosting the uncertainties on the centroids to have a looser prior

		#rotate the prior according to theta rot
		xc,yc = (shape-1)/2, (shape-1)/2
		xc_morph_rot, yc_morph_rot = utils.rotate_coords(xc_morph, yc_morph, xc, yc, theta_rot)

		theta = py_table['theta_q50'][0]
		#rotate the prior according to theta rot (still in radians)
		print('Rotating the prior by ', theta_rot, ' radians, from ', theta, ' radians to ', theta - theta_rot, ' radians')
		theta_rot = (theta - theta_rot) % (2*jnp.pi) #it's a - because the rotation is CLOCKWISE and the PA is also defined in a CCW way in Pysersic

		PA = (theta_rot-jnp.pi/2) * (180/jnp.pi) #convert to degrees
		if PA < 0:
			print('Converting pysersic PA from ', PA, ' to ', PA + 180, ' degrees')
			PA += 180
		elif PA > 180:
			print('Converting pysersic PA from ', PA, ' to ', PA - 180, ' degrees')
			PA -= 180
		PA = 90 - PA #for the kinematics
		if PA < 0:
			PA += 180
		PA_mean_err = ((py_table['theta_q84'][0] - py_table['theta_q50'][0]) + (py_table['theta_q50'][0] - py_table['theta_q16'][0]))/2
		PA_std = (PA_mean_err)*(180/jnp.pi) #convert to degrees
		print('Setting parametric priors: ', PA, inclination, r_eff_Ha, n, amplitude, xc_morph, yc_morph)

		# Set kinematic prior bounds (use config defaults)
		from .config import KinematicPriors
		kin_defaults = KinematicPriors()
		self.Va_min = kin_defaults.Va_min
		self.Va_max = kin_defaults.Va_max
		self.sigma0_min = kin_defaults.sigma0_min
		self.sigma0_max = kin_defaults.sigma0_max

		# Set backward compatibility attributes
		self.V_max = self.Va_max
		self.D_max = self.sigma0_max

		#set class attributes for all of these values
		self.PA_morph_mu = PA
		self.PA_morph_std = PA_std
		# self.ellip_mu = ellip
		# self.ellip_std = ellip_std
		self.inc_mu = inclination
		self.inc_std = inclination_std

		self.r_eff_mu = r_eff_Ha
		self.r_eff_std = r_eff_std
		self.r_eff_min = r_eff_min
		self.r_eff_max = r_eff_max

		self.amplitude_mu = amplitude
		self.amplitude_std = amplitude_std
		self.n_mu = n 
		self.n_std = n_std
		self.xc_morph = xc_morph_rot
		self.xc_std = xc_std
		self.yc_morph = yc_morph_rot
		self.yc_std = yc_std

		self.xc_std_vel = self.xc_std
		self.yc_std_vel = self.yc_std
	

	def set_parametric_priors_test(self,priors):
		#set class attributes for all of these values
		self.PA_morph_mu = priors['PA']
		self.PA_morph_std = 5 #0.2*priors['PA']
		# self.ellip_mu = ellip
		# self.ellip_std = ellip_std
		self.inc_mu = priors['i']
		self.inc_std = 0.2*priors['i']
		self.r_eff_mu = (1.676/0.4)*priors['r_t']
		self.r_eff_std = np.maximum(3, self.r_eff_mu)
		self.r_eff_min = 0
		self.r_eff_max = 15
		self.n_mu = priors['n'] #1 #*2 #just testing for Erica's
		self.n_std = 1
		self.xc_morph = 15
		self.xc_std = 1
		self.yc_morph = 15
		self.yc_std = 1
		ellip = 1 - utils.compute_axis_ratio(60, 0.2)
		self.amplitude_mu = 200 #utils.Ie_to_flux(1, self.n_mu, self.r_eff_mu, ellip)
		self.amplitude_std = 40 #0.1*self.amplitude_mu

		self.V_max = 1000
		self.D_max = 600

		self.xc_std_vel = 2*self.xc_std
		self.yc_std_vel = 2*self.yc_std

		print('Set mock kinematic priors: ', self.PA_morph_mu, self.inc_mu, self.r_eff_mu, self.amplitude_mu, self.n_mu, self.xc_morph, self.yc_morph)

	def set_priors_from_config(self, config):
		"""Set ALL priors from FitConfiguration object (complete override)"""
		from .config import FitConfiguration

		if not isinstance(config, FitConfiguration):
			raise TypeError("config must be a FitConfiguration object")

		# Check that morphology priors are provided
		if config.morphology is None:
			raise ValueError(
				"Morphology priors must be provided in config when using set_priors_from_config(). "
				"Morphology priors should come from PySersic fitting or manual specification."
			)

		# Validate configuration
		issues = config.validate()
		errors = [issue for issue in issues if issue.startswith("ERROR")]
		if errors:
			raise ValueError(f"Configuration validation failed: {errors}")

		# Set morphological priors
		morph = config.morphology
		self.PA_morph_mu = morph.PA_mean
		self.PA_morph_std = morph.PA_std

		self.inc_mu = morph.inc_mean
		self.inc_std = morph.inc_std

		self.r_eff_mu = morph.r_eff_mean
		self.r_eff_std = morph.r_eff_std
		self.r_eff_min = morph.r_eff_min
		self.r_eff_max = morph.r_eff_max

		self.n_mu = morph.n_mean
		self.n_std = morph.n_std
		self.n_min = morph.n_min
		self.n_max = morph.n_max

		self.amplitude_mu = morph.amplitude_mean
		self.amplitude_std = morph.amplitude_std
		self.amplitude_min = morph.amplitude_min
		self.amplitude_max = morph.amplitude_max

		self.xc_morph = morph.xc_mean
		self.xc_std = morph.xc_std
		self.yc_morph = morph.yc_mean
		self.yc_std = morph.yc_std

		# Set kinematic priors
		kin = config.kinematics
		self.Va_min = kin.Va_min
		self.Va_max = kin.Va_max
		self.V_max = kin.Va_max  # For backward compatibility

		self.sigma0_min = kin.sigma0_min
		self.sigma0_max = kin.sigma0_max
		self.D_max = kin.sigma0_max  # For backward compatibility

		# Note: r_t is not set from config - it uses r_eff as max bound

		# Set velocity coordinate uncertainties
		self.xc_std_vel = 2 * self.xc_std
		self.yc_std_vel = 2 * self.yc_std

		print(f"Set priors from config: PA={self.PA_morph_min}-{self.PA_morph_max}°, "
		      f"inc={self.inc_min}-{self.inc_max}°, Va={self.Va_min}-{self.Va_max} km/s, "
		      f"sigma0={self.sigma0_min}-{self.sigma0_max} km/s")

	def apply_config_overrides(self, config):
		"""
		Apply only explicitly modified config parameters as selective overrides.

		This method checks which parameters were changed from defaults and only
		overrides those specific parameters, leaving PySersic or default priors
		intact for all other parameters.

		Parameters
		----------
		config : FitConfiguration
			Configuration object with potentially modified parameters
		"""
		from .config import FitConfiguration

		if not isinstance(config, FitConfiguration):
			raise TypeError("config must be a FitConfiguration object")

		# Get only the parameters that were explicitly modified
		modified = config.get_modified_params()

		overridden_params = []

		# Apply morphology overrides
		morph_map = {
			'PA_mean': ('PA_morph_mu', lambda v: v),
			'PA_std': ('PA_morph_std', lambda v: v),
			'inc_mean': ('inc_mu', lambda v: v),
			'inc_std': ('inc_std', lambda v: v),
			'r_eff_mean': ('r_eff_mu', lambda v: v),
			'r_eff_std': ('r_eff_std', lambda v: v),
			'r_eff_min': ('r_eff_min', lambda v: v),
			'r_eff_max': ('r_eff_max', lambda v: v),
			'n_mean': ('n_mu', lambda v: v),
			'n_std': ('n_std', lambda v: v),
			'n_min': ('n_min', lambda v: v),
			'n_max': ('n_max', lambda v: v),
			'amplitude_mean': ('amplitude_mu', lambda v: v),
			'amplitude_std': ('amplitude_std', lambda v: v),
			'amplitude_min': ('amplitude_min', lambda v: v),
			'amplitude_max': ('amplitude_max', lambda v: v),
			'xc_mean': ('xc_morph', lambda v: v),
			'xc_std': ('xc_std', lambda v: v),
			'yc_mean': ('yc_morph', lambda v: v),
			'yc_std': ('yc_std', lambda v: v),
		}

		for config_param, value in modified['morphology'].items():
			if config_param in morph_map:
				attr_name, transform = morph_map[config_param]
				setattr(self, attr_name, transform(value))
				overridden_params.append(f"{config_param}→{attr_name}")

		# Apply kinematic overrides
		kin_map = {
			'Va_min': ('Va_min', lambda v: v),
			'Va_max': ('Va_max', lambda v: v),
			'sigma0_min': ('sigma0_min', lambda v: v),
			'sigma0_max': ('sigma0_max', lambda v: v),
		}

		for config_param, value in modified['kinematics'].items():
			if config_param in kin_map:
				attr_name, transform = kin_map[config_param]
				setattr(self, attr_name, transform(value))
				overridden_params.append(f"{config_param}→{attr_name}")

				# Update backward compatibility attributes
				if config_param == 'Va_max':
					self.V_max = value
				elif config_param == 'sigma0_max':
					self.D_max = value

		# Update velocity coordinate uncertainties if morphology xc/yc changed
		if any('xc_std' in p or 'yc_std' in p for p in overridden_params):
			self.xc_std_vel = 2 * self.xc_std
			self.yc_std_vel = 2 * self.yc_std

		if overridden_params:
			print(f"Applied {len(overridden_params)} config overrides: {', '.join(overridden_params[:5])}" +
			      (f" and {len(overridden_params)-5} more..." if len(overridden_params) > 5 else ""))
		else:
			print("No config overrides applied (all parameters at default values)")


	def sample_fluxes_parametric(self):

		#sample the parameters needed for a disc model
		unscaled_amplitude = numpyro.sample('unscaled_amplitude', dist.TruncatedNormal(low = (0.0 - self.amplitude_mu)/self.amplitude_std))
		amplitude = numpyro.deterministic('amplitude', unscaled_amplitude*self.amplitude_std + self.amplitude_mu)

		unscaled_r_eff = numpyro.sample('unscaled_r_eff', dist.TruncatedNormal(low = (self.r_eff_min - self.r_eff_mu)/self.r_eff_std, high = (self.r_eff_max - self.r_eff_mu)/self.r_eff_std))
		r_eff = numpyro.deterministic('r_eff', unscaled_r_eff*self.r_eff_std + self.r_eff_mu)

		unscaled_n = numpyro.sample('unscaled_n', dist.TruncatedNormal(low = (0.36 - self.n_mu)/self.n_std, high = (8.0 - self.n_mu)/self.n_std))
		n = numpyro.deterministic('n', unscaled_n*self.n_std + self.n_mu)


		i_low = (0-self.inc_mu)/self.inc_std
		i_high = (90-self.inc_mu)/self.inc_std
		unscaled_i = numpyro.sample('unscaled_i', dist.TruncatedNormal(low = i_low, high = i_high))
		i = numpyro.deterministic('i', unscaled_i*self.inc_std + self.inc_mu)

		ellip = 1 - utils.compute_axis_ratio(inc = i, q0 = 0.2)

		unscaled_PA_morph = numpyro.sample('unscaled_PA_morph', dist.Normal()) #self.mu_PA*jnp.pi/180, 1/((self.sigma_PA*jnp.pi/180)**2)
		PA_morph = numpyro.deterministic('PA_morph', unscaled_PA_morph*self.PA_morph_std + self.PA_morph_mu)


		unscaled_xc_morph = numpyro.sample('unscaled_xc_morph', dist.Normal())
		xc_morph = numpyro.deterministic('xc_morph', unscaled_xc_morph*self.xc_std + self.xc_morph)
		# xc_morph = self.xc_morph

		unscaled_yc_morph = numpyro.sample('unscaled_yc_morph', dist.Normal())
		yc_morph = numpyro.deterministic('yc_morph', unscaled_yc_morph*self.yc_std + self.yc_morph)  
		# yc_morph = self.yc_morph                                 
					

		factor = self.factor
				
		sersic_factor = 25
		image_shape = self.direct_shape[0]

		x = jnp.linspace(0 - xc_morph, image_shape - xc_morph - 1, image_shape)
		y = jnp.linspace(0 - yc_morph, image_shape - yc_morph - 1, image_shape)
		x,y = jnp.meshgrid(x,y)

		amplitude_re = utils.flux_to_Ie(amplitude, n, r_eff, ellip)

		#-------------------------constant oversampling---------------------------------

		x_grid = image.resize(x, (image_shape*factor*sersic_factor, image_shape*factor*sersic_factor), method='linear')
		y_grid = image.resize(y, (image_shape*factor*sersic_factor, image_shape*factor*sersic_factor), method='linear')
		#the center is set at 0,0 because the grid is already centered at xc_morph, yc_morph
		model_image_highres = utils.sersic_profile(x_grid, y_grid, amplitude_re/(sersic_factor*factor)**2, r_eff, n,0.0,0.0, ellip, (90 - PA_morph)*jnp.pi/180)
		model_image = utils.resample(model_image_highres, int(sersic_factor), int(sersic_factor))

		#-------------------------adaptive oversampling---------------------------------
		# x_grid = image.resize(x, (image_shape*factor, image_shape*factor), method='linear')
		# y_grid = image.resize(y, (image_shape*factor, image_shape*factor), method='linear')
		# model_image = utils.compute_adaptive_sersic_profile(x_grid, y_grid, amplitude/factor**2, r_eff, n, 0.0,0.0, ellip, (90 - PA_morph)*jnp.pi/180)
		#------------------------------------------------------------------------------

		#mask the low fluxes of the model image
		model_image_masked = model_image #jnp.where(model_image>0.01*model_image.max(), model_image, 0.0)

		#the returned image has a shape of image_shape*factor
		return model_image_masked, r_eff, i, xc_morph, yc_morph


	def sample_params_parametric(self,r_eff = 0.0):
		"""
			Sample all of the parameters needed to model a disk velocity field
		"""

		unscaled_PA = numpyro.sample('unscaled_PA', dist.Normal())
		Pa = numpyro.deterministic('PA', unscaled_PA*self.PA_morph_std*2 + self.PA_morph_mu) #giving more freedom to the kinematic PA! it's really the morph one that has to be well constrained

		unscaled_Va = numpyro.sample('unscaled_Va', dist.Uniform())
		Va = numpyro.deterministic('Va', unscaled_Va*(self.Va_max - self.Va_min) + self.Va_min)

		unscaled_r_t = numpyro.sample('unscaled_r_t', dist.Uniform())
		r_t = numpyro.deterministic('r_t', unscaled_r_t*r_eff)


		unscaled_sigma0 = numpyro.sample('unscaled_sigma0', dist.Uniform())
		sigma0 = numpyro.deterministic('sigma0', unscaled_sigma0*(self.sigma0_max - self.sigma0_min) + self.sigma0_min)


		unscaled_x0_vel = numpyro.sample('unscaled_x0_vel', dist.Normal())
		x0_vel = numpyro.deterministic('x0_vel', unscaled_x0_vel*self.xc_std_vel + self.xc_morph)


		unscaled_y0_vel = numpyro.sample('unscaled_y0_vel', dist.Normal())
		y0_vel = numpyro.deterministic('y0_vel', unscaled_y0_vel*self.yc_std_vel + self.yc_morph)  

		unscaled_v0 = numpyro.sample('unscaled_v0', dist.Normal())
		v0 = numpyro.deterministic('v0', unscaled_v0*50)
		# v0 = 0


		return Pa, Va, r_t,sigma0, y0_vel, x0_vel, v0
	

	def compute_posterior_means_parametric(self, inference_data):
		"""
			Retreive the best sample from the MCMC chains for the main disk variables
		"""

		self.PA_mean = jnp.array(inference_data.posterior['PA'].median(dim=["chain", "draw"]))
		self.y0_vel_mean = jnp.array(inference_data.posterior['y0_vel'].median(dim=["chain", "draw"]))
		self.x0_vel_mean = jnp.array(inference_data.posterior['x0_vel'].median(dim=["chain", "draw"]))
		self.v0_mean = jnp.array(inference_data.posterior['v0'].median(dim=["chain", "draw"]))
		self.r_t_mean = jnp.array(inference_data.posterior['r_t'].median(dim=["chain", "draw"]))
		self.sigma0_mean_model = jnp.array(inference_data.posterior['sigma0'].median(dim=["chain", "draw"]))
		self.Va_mean = jnp.array(inference_data.posterior['Va'].median(dim=["chain", "draw"]))

		#save the percentiles as well
		self.PA_16 = jnp.array(inference_data.posterior['PA'].quantile(0.16, dim=["chain", "draw"]))
		self.PA_84 = jnp.array(inference_data.posterior['PA'].quantile(0.84, dim=["chain", "draw"]))

		self.v0_16 = jnp.array(inference_data.posterior['v0'].quantile(0.16, dim=["chain", "draw"]))
		self.v0_84 = jnp.array(inference_data.posterior['v0'].quantile(0.84, dim=["chain", "draw"]))
		self.r_t_16 = jnp.array(inference_data.posterior['r_t'].quantile(0.16, dim=["chain", "draw"]))
		self.r_t_84 = jnp.array(inference_data.posterior['r_t'].quantile(0.84, dim=["chain", "draw"]))
		self.sigma0_16 = jnp.array(inference_data.posterior['sigma0'].quantile(0.16, dim=["chain", "draw"]))
		self.sigma0_84 = jnp.array(inference_data.posterior['sigma0'].quantile(0.84, dim=["chain", "draw"]))
		self.Va_16 = jnp.array(inference_data.posterior['Va'].quantile(0.16, dim=["chain", "draw"]))
		self.Va_84 = jnp.array(inference_data.posterior['Va'].quantile(0.84, dim=["chain", "draw"]))

		self.x0_vel_16 = jnp.array(inference_data.posterior['x0_vel'].quantile(0.16, dim=["chain", "draw"]))
		self.x0_vel_84 = jnp.array(inference_data.posterior['x0_vel'].quantile(0.84, dim=["chain", "draw"]))
		self.y0_vel_16 = jnp.array(inference_data.posterior['y0_vel'].quantile(0.16, dim=["chain", "draw"]))
		self.y0_vel_84 = jnp.array(inference_data.posterior['y0_vel'].quantile(0.84, dim=["chain", "draw"]))

		return  self.PA_mean,self.Va_mean, self.r_t_mean, self.sigma0_mean_model, self.y0_vel_mean, self.x0_vel_mean, self.v0_mean

	def compute_parametrix_flux_posterior(self, inference_data):
		#compute means for parametric flux model
		self.amplitude_mean = jnp.array(inference_data.posterior['amplitude'].median(dim=["chain", "draw"]))
		self.amplitude_16 = jnp.array(inference_data.posterior['amplitude'].quantile(0.16, dim=["chain", "draw"]))
		self.amplitude_84 = jnp.array(inference_data.posterior['amplitude'].quantile(0.84, dim=["chain", "draw"]))
		self.r_eff_mean = jnp.array(inference_data.posterior['r_eff'].median(dim=["chain", "draw"]))
		self.n_mean = jnp.array(inference_data.posterior['n'].median(dim=["chain", "draw"]))
		self.n_16 = jnp.array(inference_data.posterior['n'].quantile(0.16, dim=["chain", "draw"]))
		self.n_84 = jnp.array(inference_data.posterior['n'].quantile(0.84, dim=["chain", "draw"]))
		# self.ellip_mean = jnp.array(inference_data.posterior['ellip'].median(dim=["chain", "draw"]))
		self.PA_morph_mean = jnp.array(inference_data.posterior['PA_morph'].median(dim=["chain", "draw"])) #- 45
		#compute the inclination prior posterior and median from the ellipticity
		num_samples = inference_data.posterior['i'].shape[1]
		num_chains = inference_data.posterior['i'].shape[0]
		num_samples_prior = inference_data.prior['i'].shape[1]

		inference_data.posterior['ellip'] = xr.DataArray(np.zeros((num_chains, num_samples)), dims = ('chain', 'draw'))
		inference_data.prior['ellip'] = xr.DataArray(np.zeros((1, num_samples_prior)), dims = ('chain', 'draw'))
		for i in range(num_chains):
			for sample in range(num_samples-1):
				inference_data.posterior['ellip'][i,int(sample)] = 1 - utils.compute_axis_ratio(inc = float(inference_data.posterior['i'][i,int(sample)].values), q0 = 0.2)

		# Process prior samples separately
		for sample in range(num_samples_prior-1):
			inference_data.prior['ellip'][0,int(sample)] = 1 - utils.compute_axis_ratio(inc = float(inference_data.prior['i'][0,int(sample)].values), q0 = 0.2)
		
		self.i_mean = jnp.array(inference_data.posterior['i'].median(dim=["chain", "draw"]))
		self.i_16 = jnp.array(inference_data.posterior['i'].quantile(0.16, dim=["chain", "draw"]))
		self.i_84 = jnp.array(inference_data.posterior['i'].quantile(0.84, dim=["chain", "draw"]))
		# self.ellip_mean = 1 - jnp.cos(jnp.radians(self.i_mean))
		self.ellip_mean = jnp.array(inference_data.posterior['ellip'].median(dim=["chain", "draw"]))
		self.ellip_16 = jnp.array(inference_data.posterior['ellip'].quantile(0.16, dim=["chain", "draw"]))
		self.ellip_84 = jnp.array(inference_data.posterior['ellip'].quantile(0.84, dim=["chain", "draw"]))
		#compute the fluxes for the parametric model
		# y, x = np.mgrid[0:self.direct_shape[0]*27, 0:self.direct_shape[1]*27]
		# fluxes_mean_high = utils.sersic_profile(x,y,amplitude=self.amplitude_mean, r_eff = self.r_eff_mean*27, n = self.n_mean, x_0 = self.direct_shape[0]//2*27 + 13 , y_0 = self.direct_shape[0]//2*27 +13, ellip = self.ellip_mean, theta=(90 - self.PA_morph_mean)*np.pi/180)/27**2 #function takes theta in rads
		# self.fluxes_mean = utils.resample(fluxes_mean_high, 27,27)

		self.r_eff_16 = jnp.array(inference_data.posterior['r_eff'].quantile(0.16, dim=["chain", "draw"]))
		self.r_eff_84 = jnp.array(inference_data.posterior['r_eff'].quantile(0.84, dim=["chain", "draw"]))

		self.xc_morph_mean = jnp.array(inference_data.posterior['xc_morph'].median(dim=["chain", "draw"]))
		self.xc_morph_16 = jnp.array(inference_data.posterior['xc_morph'].quantile(0.16, dim=["chain", "draw"]))
		self.xc_morph_84 = jnp.array(inference_data.posterior['xc_morph'].quantile(0.84, dim=["chain", "draw"]))

		self.yc_morph_mean = jnp.array(inference_data.posterior['yc_morph'].median(dim=["chain", "draw"]))
		self.yc_morph_16 = jnp.array(inference_data.posterior['yc_morph'].quantile(0.16, dim=["chain", "draw"]))
		self.yc_morph_84 = jnp.array(inference_data.posterior['yc_morph'].quantile(0.84, dim=["chain", "draw"]))

		#compute the fluxes in the sersic way
		factor = self.factor
				
		sersic_factor = 25
		image_shape = self.direct_shape[0]

		amplitude_re_mean = utils.flux_to_Ie(self.amplitude_mean,self.n_mean, self.r_eff_mean, self.ellip_mean)

		x = jnp.linspace(0 - self.xc_morph_mean, image_shape - self.xc_morph_mean - 1, image_shape)
		y = jnp.linspace(0 - self.yc_morph_mean, image_shape - self.yc_morph_mean - 1, image_shape)
		x,y = jnp.meshgrid(x,y)
		x_grid = image.resize(x, (image_shape*factor*sersic_factor, image_shape*factor*sersic_factor), method='linear')
		y_grid = image.resize(y, (image_shape*factor*sersic_factor, image_shape*factor*sersic_factor), method='linear')
		#testing the adaptive oversampling of the sersic profile
		fluxes_mean_high = utils.sersic_profile(x_grid, y_grid, amplitude_re_mean/(sersic_factor*factor)**2, self.r_eff_mean, self.n_mean, 0.0,0.0, self.ellip_mean, (90 - self.PA_morph_mean)*jnp.pi/180)
		self.fluxes_mean_high = utils.resample(fluxes_mean_high, sersic_factor, sersic_factor)
		self.fluxes_mean = utils.resample(fluxes_mean_high, factor*sersic_factor, factor*sersic_factor)
		self.fluxes_mean_masked = jnp.where(self.fluxes_mean>0.01*self.fluxes_mean.max(), self.fluxes_mean, 0.0)
		return inference_data, self.fluxes_mean_masked, self.fluxes_mean_high, self.amplitude_mean, self.r_eff_mean, self.n_mean, self.ellip_mean, self.PA_morph_mean, self.i_mean, self.xc_morph_mean, self.yc_morph_mean
	
	def v_rot(self, fluxes_mean, model_velocities, i_mean,factor):
		"""
			Compute the rotational velocity of the disk component

			If called from multiple component model, the 3 attributes of this function should be only from that component
		"""
		plt.imshow(fluxes_mean, origin='lower')
		plt.colorbar()
		plt.title('Fluxes mean')
		plt.show()
		plt.close()
		print(fluxes_mean.max())
		threshold = 0.4*fluxes_mean.max()
		mask = jnp.zeros_like(fluxes_mean)
		mask = mask.at[jnp.where(fluxes_mean>threshold)].set(1)
		model_velocities_low = jax.image.resize(model_velocities, (int(model_velocities.shape[0]/factor), int(model_velocities.shape[1]/factor)), method='nearest')
		model_v_rot = 0.5*(jnp.nanmax(jnp.where(mask == 1, model_velocities_low, jnp.nan)) - jnp.nanmin(jnp.where(mask == 1, model_velocities_low, jnp.nan)))/ jnp.sin( jnp.radians(i_mean)) 
		plt.imshow(jnp.where(mask ==1, fluxes_mean, np.nan), origin = 'lower')
		plt.title('Mask for v_rot comp')
		plt.show()
		plt.close()
		return model_v_rot

	def plot(self):

		"""
			Plot the disk model
		"""
		
		#plot the fluxes within the mask and the velocity centroid
		fluxes = jnp.zeros(self.direct_shape)
		fluxes = fluxes.at[self.masked_indices].set(self.mu)
		# fluxes = self.mu
		plt.imshow(fluxes, origin='lower')
		plt.colorbar()
		plt.scatter(self.x0_vel, self.mu_y0_vel, color='red')
		plt.title('Disk')
		plt.show()
		plt.close()



class DiskModel(KinModels):
	"""
		Class for the one component exponential disk model
	"""

	def __init__(self):
		print('Disk model created')

		#declare var and label names for plotting

		self.var_names = [ 'i', 'Va', 'sigma0'] #, 'fluxes_scaling']
		self.labels = [ r'$i$', r'$V_a$', r'$\sigma_0$'] #, r'$f_{scale}$']
		# self.var_names = ['PA', 'i', 'Va', 'r_t', 'sigma0_max', 'sigma0_scale', 'sigma0_const']
		# self.labels = [r'$PA$', r'$i$', r'$V_a$', r'$r_t$', r'$\sigma_{max}$', r'$\sigma_{scale}$', r'$\sigma_{const}$']

	def set_bounds(self, im_shape, factor, wave_factor, x0, x0_vel, y0, y0_vel):
		"""
		Set grism-specific configuration for the disk model.

		Parameters
		----------
		im_shape : tuple
			Shape of the image
		factor : int
			Spatial oversampling factor
		wave_factor : int
			Wavelength oversampling factor
		x0, y0 : float
			Morphological centroid positions (pixels)
		x0_vel, y0_vel : float
			Velocity centroid positions (pixels)

		Notes
		-----
		All priors (morphological and kinematic) should be set separately
		using set_priors_from_config() or set_parametric_priors() after this method.
		This method only handles grism configuration and centroid positions.
		"""
		# Set basic configuration
		self.set_main_bounds(factor, wave_factor, x0, x0_vel, y0, y0_vel)

		self.im_shape = im_shape

		# Initialize disk with default r_eff (will be updated by set_priors_from_config)
		self.disk = Disk(self.im_shape, self.factor, self.x0_vel, self.mu_y0_vel, self.r_eff if hasattr(self, 'r_eff') and self.r_eff is not None else 1.0)
		
		# self.disk.plot()



	
	def inference_model_parametric(self, grism_object, obs_map, obs_error, mask = None):
		"""

		Model used to infer the disk parameters from the data => called in fitting.py as the forward
		model used for the inference

		"""
		# fluxes = self.disk.sample_fluxes()
		fluxes,r_eff, i, xc_morph, yc_morph = self.disk.sample_fluxes_parametric() 
		Pa, Va, r_t, sigma0, y0_vel, x0_vel, v0 = self.disk.sample_params_parametric(r_eff=r_eff)      
		# i = utils.compute_inclination(ellip = ellip) 

		# #set the velocity centroid to the morph one so that we don't have to fit for it!
		# x0_vel = xc_morph
		# y0_vel = yc_morph

		fluxes_high = fluxes #utils.oversample(fluxes, grism_object.factor, grism_object.factor, method= 'bilinear')

		image_shape = self.im_shape[0]
		x= jnp.linspace(0 - x0_vel, image_shape - x0_vel - 1, image_shape)
		y = jnp.linspace(0 - y0_vel, image_shape - y0_vel - 1, image_shape)
		X, Y = jnp.meshgrid(x,y)

		X_grid = image.resize(X, (int(X.shape[0]*grism_object.factor), int(X.shape[1]*grism_object.factor)), method='linear')
		Y_grid = image.resize(Y, (int(Y.shape[0]*grism_object.factor), int(Y.shape[1]*grism_object.factor)), method='linear')

		velocities = jnp.asarray(self.v(X_grid, Y_grid, Pa, i, Va, r_t))

		velocities_scaled = velocities + v0

		dispersions = sigma0*jnp.ones_like(velocities_scaled)

		self.model_map = grism_object.disperse(fluxes_high, velocities_scaled, dispersions)

		self.model_map = utils.resample(self.model_map, grism_object.factor, self.wave_factor)


		self.error_scaling = 1 #numpyro.sample('error_scaling', dist.Uniform(0, 1))*5
		# SN_min = jnp.minimum((obs_map/obs_error).max()/10,5)
		# mask = jnp.where(obs_map/obs_error < SN_min, 0, 1)
		# model_masked = jnp.where(mask == 1, self.model_map, 0)
		# obs_masked = jnp.where(mask == 1, obs_map, 0)
		# obs_error_masked = jnp.where(mask == 1, obs_error, 1e6)

		obs_error_masked = obs_error #jnp.where(mask == 1, obs_error, 1e6)



		# numpyro.sample('obs', dist.Normal(self.model_map[5:26,:], self.error_scaling*obs_error[5:26,:]), obs=obs_map[5:26,:])
		numpyro.sample('obs', dist.Normal(self.model_map, self.error_scaling*obs_error_masked), obs=obs_map)


	def compute_model_parametric(self, inference_data, grism_object):
		"""

		Function used to post-process the MCMC samples and plot results from the model

		"""

		self.PA_mean,self.Va_mean, self.r_t_mean, self.sigma0_mean_model, self.y0_vel_mean,self.x0_vel_mean, self.v0_mean = self.disk.compute_posterior_means_parametric(inference_data)
		#save all of the percentile values
		self.PA_16 = self.disk.PA_16
		self.PA_84 = self.disk.PA_84
		self.Va_16 = self.disk.Va_16
		self.Va_84 = self.disk.Va_84
		self.r_t_16 = self.disk.r_t_16
		self.r_t_84 = self.disk.r_t_84
		self.sigma0_16 = self.disk.sigma0_16
		self.sigma0_84 = self.disk.sigma0_84
		self.y0_vel_16 = self.disk.y0_vel_16
		self.y0_vel_84 = self.disk.y0_vel_84
		self.x0_vel_16 = self.disk.x0_vel_16
		self.x0_vel_84 = self.disk.x0_vel_84
		self.v0_16 = self.disk.v0_16
		self.v0_84 = self.disk.v0_84

		# self.PA_mean,self.i_mean, self.Va_mean, self.r_t_mean, self.sigma0_max_mean, self.sigma0_scale_mean, self.sigma0_const_mean,self.y0_vel_mean, self.v0_mean = self.disk.compute_posterior_means(inference_data)

		# self.fluxes_mean, self.fluxes_scaling_mean = self.disk.compute_flux_posterior(inference_data, self.flux_type)
		inference_data,self.fluxes_mean, self.fluxes_mean_high, self.amplitude_mean, self.r_eff_mean, self.n_mean, self.ellip_mean, self.PA_morph_mean, self.i_mean, self.xc_morph_mean, self.yc_morph_mean = self.disk.compute_parametrix_flux_posterior(inference_data)

		self.amplitude_16 = self.disk.amplitude_16
		self.amplitude_84 = self.disk.amplitude_84

		self.n_16 = self.disk.n_16
		self.n_84 = self.disk.n_84

		self.r_eff_16 = self.disk.r_eff_16
		self.r_eff_84 = self.disk.r_eff_84

		self.xc_morph_mean = self.disk.xc_morph_mean
		self.xc_morph_16 = self.disk.xc_morph_16
		self.xc_morph_84 = self.disk.xc_morph_84

		self.yc_morph_mean = self.disk.yc_morph_mean
		self.yc_morph_16 = self.disk.yc_morph_16
		self.yc_morph_84 = self.disk.yc_morph_84

		self.ellip_mean = self.disk.ellip_mean
		self.ellip_16 = self.disk.ellip_16
		self.ellip_84 = self.disk.ellip_84
		self.i_16 = self.disk.i_16
		self.i_84 = self.disk.i_84
		# self.model_flux = utils.oversample(self.fluxes_mean, grism_object.factor, grism_object.factor, method= 'bicubic')
		self.model_flux = self.fluxes_mean_high

		image_shape =  self.im_shape[0]
		x= jnp.linspace(0 - self.x0_vel_mean, image_shape - self.x0_vel_mean - 1, image_shape)
		y = jnp.linspace(0 - self.y0_vel_mean, image_shape - self.y0_vel_mean - 1, image_shape)
		X, Y = jnp.meshgrid(x,y)

		X_grid = image.resize(X, (int(X.shape[0]*grism_object.factor), int(X.shape[1]*grism_object.factor)), method='nearest')
		Y_grid = image.resize(Y, (int(Y.shape[0]*grism_object.factor), int(Y.shape[1]*grism_object.factor)), method='nearest')

		self.model_velocities = jnp.asarray(self.v(X_grid, Y_grid, self.PA_mean,self.i_mean, self.Va_mean, self.r_t_mean))
		# self.model_velocities = image.resize(self.model_velocities, (int(self.model_velocities.shape[0]/10), int(self.model_velocities.shape[1]/10)), method='bicubic')

		self.model_velocities = self.model_velocities  + self.v0_mean

		self.model_dispersions = self.sigma0_mean_model *jnp.ones_like(self.model_velocities) #self.sigma0_mean_model *jnp.ones_like(self.model_velocities)

		self.model_map_high = grism_object.disperse(self.model_flux, self.model_velocities, self.model_dispersions)
		# self.model_map_high = grism_object.disperse(self.convolved_fluxes, self.convolved_velocities, self.convolved_dispersions)

		self.model_map = utils.resample(self.model_map_high, grism_object.factor, self.wave_factor)
		# print('Model vels:', self.model_velocities)
		#compute velocity grid in flux image resolution for plotting velocity maps
		self.model_velocities_low = image.resize(self.model_velocities, (int(self.model_velocities.shape[0]/grism_object.factor), int(self.model_velocities.shape[1]/grism_object.factor)), method='nearest')
		# print(self.fluxes_mean)
		self.model_velocities_low = np.where(self.fluxes_mean == 0, np.nan, self.model_velocities_low)
		self.model_dispersions_low = image.resize(self.model_dispersions, (int(self.model_dispersions.shape[0]/grism_object.factor), int(self.model_dispersions.shape[1]/grism_object.factor)), method='nearest')
		self.model_dispersions_low = jnp.where(self.fluxes_mean == 0, np.nan, self.model_dispersions_low)
		return inference_data, self.model_map, self.model_flux, self.fluxes_mean, self.model_velocities, self.model_dispersions
	
	def compute_model(self,inference_data, grism_object, parametric = False):
		"""

		Function used to post-process the MCMC samples and plot results from the model

		"""

		if parametric:
			return self.compute_model_parametric(inference_data, grism_object)
		else:
			raise NotImplementedError('Non-parametric flux model not implemented yet for DiskModel')

	def log_likelihood(self, grism_object, obs_map, obs_error, values = {}):
		Pa = values['PA']
		i = values['i']
		Va = values['Va']
		r_t = values['r_t']
		sigma0 = values['sigma0']

		fluxes = jnp.where(self.mask ==1, self.flux_prior, 0.0)

		fluxes_high = utils.oversample(fluxes, grism_object.factor, grism_object.factor)

		image_shape = fluxes.shape[0]
		# print(image_shape//2)
		x_10 = jnp.linspace(0 - image_shape//2, image_shape - image_shape//2 - 1, image_shape*grism_object.factor)
		y_10 = jnp.linspace(0 - image_shape//2, image_shape - image_shape//2 - 1, image_shape*grism_object.factor)
		X_10, Y_10 = jnp.meshgrid(x_10,y_10)

		
		velocities = jnp.array(self.v(X_10, Y_10, Pa, i, Va, r_t))


		velocities_scaled = velocities

		dispersions = sigma0*jnp.ones_like(velocities_scaled)

		self.model_map = grism_object.disperse(fluxes_high, velocities_scaled, dispersions)


		self.model_map = utils.resample(self.model_map, grism_object.y_factor*grism_object.factor, self.wave_factor)


		mask_obs = jnp.where(obs_map/obs_error > 5, 1, 0)
		model_mask = jnp.where(mask_obs == 1, self.model_map, 0.0)
		obs_mask = jnp.where(mask_obs == 1, obs_map, 0.0)
		obs_error_mask = jnp.where(mask_obs == 1, obs_error, 1e6)

		#compute the gaussian likelihood for the model
		log_likelihood = dist.Normal(model_mask, obs_error_mask).log_prob(obs_mask)

		log_likelihood_sum = jnp.sum(log_likelihood)

		print('Log likelihood: ', log_likelihood_sum)

		return log_likelihood_sum
	
	def log_prior(self, values = {}):
		Pa = values['PA']
		i = values['i']
		Va = values['Va']
		r_t = values['r_t']
		sigma0 = values['sigma0']
		fluxes = values['fluxes']
		fluxes_errors = values['fluxes_error']

		log_prior_PA = dist.TruncatedNormal(Pa, 5,low = -10,high = 100).log_prob(self.mu_PA)
		log_prior_i = dist.TruncatedNormal(i, 5,low = 0,high = 90).log_prob(self.mu_i)
		log_prior_Va = dist.Uniform(self.Va_min, self.Va_max).log_prob(Va)
		log_prior_r_t = dist.Normal(0,4).log_prob(r_t)
		log_prior_sigma0 = dist.Uniform(0, 400).log_prob(sigma0)
		log_prior_fluxes = dist.Normal(fluxes,fluxes_errors).log_prob(self.flux_prior)
		log_prior_fluxes_tot = jnp.sum(log_prior_fluxes)
		log_prior = log_prior_PA + log_prior_i + log_prior_Va + log_prior_r_t + log_prior_sigma0 + log_prior_fluxes_tot

		print('Log prior: ', log_prior)

		return log_prior
	
	def log_posterior(self, grism_object, obs_map, obs_error,values = {}):
		return -(self.log_likelihood(grism_object, obs_map, obs_error,values) + self.log_prior(values))
	def plot_summary(self, obs_map, obs_error, inf_data, wave_space, save_to_folder = None, name = None, v_re = None, PA = None, i = None, Va = None, r_t = None, sigma0 = None, obs_radius = None, ellip = None, theta_obs = None, theta_Ha =None, n = None, save_runs_path = None, ID = None):
		obs_radius = self.r_eff_mean
		ellip = self.ellip_mean
		theta_Ha = self.PA_morph_mean/(180/jnp.pi) + jnp.pi/2 #need to convert to radians and match plotting ref frame
		n = self.n_mean

		ymin,ymax = plotting.plot_disk_summary(obs_map, self.model_map, obs_error, self.model_velocities_low, self.model_dispersions_low, v_re, self.fluxes_mean, inf_data, wave_space, x0 = self.x0_vel_mean, y0 = self.y0_vel_mean, factor = 1, direct_image_size = self.im_shape[0], save_to_folder = save_to_folder, name = name, PA = PA, i = i, Va = Va, r_t = r_t, sigma0 = sigma0, obs_radius = obs_radius, ellip = ellip, theta_obs = theta_obs, theta_Ha =theta_Ha, n = n, save_runs_path  = save_runs_path, ID = ID)
		return ymin, ymax



