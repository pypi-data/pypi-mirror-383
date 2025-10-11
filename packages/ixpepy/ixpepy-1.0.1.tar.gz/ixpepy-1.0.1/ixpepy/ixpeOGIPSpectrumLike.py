"""
IXPE OGIP Spectrum Plugin Module.

This module provides classes to load and analyze IXPE spectral data using
the OGIP format. It supports Stokes I, Q, and U spectra from all three
IXPE detector units (DU1, DU2, DU3) and interfaces with the 3ML analysis
framework.
"""

from threeML.plugins.OGIPLike import OGIPLike

import os
import numpy
import itertools
from astropy.io import fits

from threeML.plugin_prototype import PluginPrototype
from threeML.utils.OGIP.pha import PHAII
from threeML.utils.spectrum.pha_spectrum import PHASpectrum
from threeML.data_list import DataList

from astromodels import *

__instrument_name = "IXPE"

# Mapping from FITS header Stokes filter to Stokes parameter name
STOKES_DICT = {'Stokes:0' : 'I',
               'Stokes:1' : 'Q',
               'Stokes:2' : 'U'}

# Import utility function for backward compatibility
from ixpepy.utils.process_raw_data import load_raw_detector_files



class ixpeOGIPSpectrumLike():
    """
    IXPE OGIP Spectrum Likelihood Manager.
    
    This class manages multiple IXPE spectral plugins (one for each detector
    unit and Stokes parameter) and provides methods to load data, apply
    rebinning, set energy ranges, and perform joint spectral analysis.
    
    Attributes
    ----------
    detector_stokes : dict
        Mapping from plugin name to (detector_unit, stokes_parameter) tuple
    plugins : list
        List of ixpeOGIPSpectrumPlugin instances
    use_poisson : bool
        Whether to use Poisson statistics for Stokes I spectra
    energy_range : str
        Energy range for analysis (format: 'emin-emax' in keV)
    caldb : str or None
        Path to IXPE calibration database
    
    Examples
    --------
    Load IXPE data files for spectral analysis:
    
    >>> ixpe = ixpeOGIPSpectrumLike(energy_range='2-8')
    >>> file_list = ['obs_det1_pha1.fits', 'obs_det1_pha1q.fits', ...]
    >>> ixpe.load_file_list(file_list)
    >>> datalist = ixpe.get_datalist()
    """

    def __init__(self, energy_range='2-8', caldb=None, use_poisson=True):
        """
        Initialize IXPE OGIP spectrum manager.
        
        Parameters
        ----------
        energy_range : str, optional
            Energy range for analysis (format: 'emin-emax' in keV).
            Default is '2-8'
        caldb : str, optional
            Path to IXPE calibration database. If None, uses paths from
            FITS headers. Default is None
        use_poisson : bool, optional
            If True, use Poisson statistics for Stokes I spectra and Gaussian
            for Q/U. If False, use Gaussian for all. Default is True
        """
        self.detector_stokes = {}
        self.plugins      = []
        self.use_poisson  = use_poisson
        self.energy_range = energy_range
        self.caldb        = caldb

    def from_basename(self, datadir, basename, suffix='_'):
        """
        Load IXPE data files using a basename pattern (ixpeobssim format).
        
        Automatically constructs file paths for all 9 files (3 detector units
        × 3 Stokes parameters) based on a common basename. This assumes the
        naming convention used by ixpeobssim simulations with 'du' prefix.
        
        Parameters
        ----------
        datadir : str
            Directory containing the IXPE data files
        basename : str
            Base name of the observation files (without detector/Stokes suffix)
        suffix : str, optional
            Separator between basename and 'pha1'. Default is '_'
        
        Returns
        -------
        None
            Plugins are added to self.plugins
        
        Notes
        -----
        This method is designed for ixpeobssim simulated data which uses 'du'
        (detector unit) naming. For real IXPE data using a different naming 
        convention, or to specify background files, use `load_file_list()` 
        directly.
        
        Examples
        --------
        For simulated files like 'source_obs_du1_pha1.fits', 'source_obs_du1_pha1q.fits':
        
        >>> ixpe.from_basename(datadir='/data', basename='source_obs')
        """
        obs_file = os.path.join(datadir, '%s_du{}%spha1{}.fits' % (basename,suffix))
        obs_list = [obs_file.format(d, s) for (d, s) in 
            itertools.product([1,2,3], ['', 'q', 'u'])]
        return self.load_file_list(file_list = obs_list, bkg_file_list = None)

    def load_file_list(self, file_list, bkg_file_list=None, name='ixpe'):
        """
        Load a list of IXPE PHA1 FITS files with optional background files.
        
        Parameters
        ----------
        file_list : list of str
            List of source spectrum file paths
        bkg_file_list : list of str, optional
            List of background spectrum file paths. Must match length of
            file_list if provided. Default is None (no background)
        name : str, optional
            Base name for plugin identification. Default is 'ixpe'
        
        Returns
        -------
        None
            Plugins are added to self.plugins
        """
        if bkg_file_list is None:
            for file_path in file_list:
                self._load_file(file_path, name=name)
        else:
            assert len(file_list) == len(bkg_file_list)
            for file_path, bkg_file_path in zip(file_list,bkg_file_list):
                self._load_file(file_path,bkg_file_path, name=name)

    def get_pha_spectrum(self, file_path, name='ixpe'):
        assert str(file_path).endswith('.fits'), f'file {file_path} does not end with fits'
        log.info('Loading the spectrum file: %s' % file_path)
        is_gaussian = True
        with fits.open(file_path, mode='update') as hdul:
            hdu = hdul['SPECTRUM']
            stokes = STOKES_DICT[hdu.header['XFLT0001']]
            if self.use_poisson:
                if stokes == 'I':
                    is_gaussian = False
                    log.info('ixpeOGIPSpectrumLike will use Poisson errors for I')
                    hdu.header["POISSERR"] = True
                else:
                    is_gaussian = True
                    hdu.header["POISSERR"] = False
                    # hdu.data['STAT_ERR'][hdu.data['STAT_ERR'] == 0] = numpy.sqrt(0.75)
            else:
                is_gaussian = True
                hdu.header["POISSERR"] = False
                pass
            # Change something in hdul.
            hdul.flush()  # changes are written back to original.fits

        pha = PHAII.from_fits_file(file_path)
        hdu = pha._hdu_list['SPECTRUM']
        self._sanitize_hdu(hdu)

        du = hdu.header['DETNAM']
        stokes = STOKES_DICT[hdu.header['XFLT0001']]
        backscal = hdu.header['BACKSCAL']
        if backscal!= 1:
            log.info('BACKSCAL for %s, Stokes %s = %s' % (du, stokes, backscal))
        #log.info('EXPOSURE for DU%s, %s = %s' % (du, stokes, hdu.header['EXPOSURE']))

        name = '%s_%s_%s' % (name, du, stokes)
        rsp_file, arf_file = self.get_irfs(hdu.header)
        self.detector_stokes[name]=(du, stokes)
        return name, stokes, du, is_gaussian, PHASpectrum(file_path, rsp_file=rsp_file, arf_file=arf_file)

    def set_energy_range(self, energy_range):
        """
        Set the energy range for all loaded plugins.
        
        Parameters
        ----------
        energy_range : str
            Energy range string (format: 'emin-emax' in keV, e.g., '2-8')
        """
        self.energy_range = energy_range
        for plugin in self.plugins:
            plugin.set_active_measurements(energy_range)

    def rebin_on_source(self, min_number_of_counts: int) -> None:
        """
        Rebin all spectra to have minimum counts per bin.
        
        Uses Stokes I spectrum to determine binning, then applies the same
        binning to Q and U spectra for each detector unit. This ensures
        consistent energy bins across all Stokes parameters.
        
        Parameters
        ----------
        min_number_of_counts : int
            Minimum number of source counts required per energy bin
        
        Notes
        -----
        The rebinning is done in two passes:
        1. Rebin Stokes I spectra and save the binning scheme
        2. Apply the same binning to Q and U spectra for each detector
        """
        rebinners = {}
        # First pass: collect rebinners for 'I' stokes and store them
        for plugin in self.plugins:
            du = plugin._du
            stokes = plugin._stokes
            if stokes == 'I':
                log.info(f'Rebinning {du} I')
                rebinners[du] = plugin.rebin_on_source(min_number_of_counts)
        # Second pass: apply rebinners to non-'I' stokes
        for plugin in self.plugins:
            du = plugin._du
            stokes = plugin._stokes
            if stokes != 'I' and du in rebinners:
                plugin._apply_rebinner(rebinners[du])

    def _load_file(self, file_path, bkg_file_path=None, name='ixpe'):
        assert os.path.exists(file_path),f'{file_path} does not exist!'
        bkg_spectrum = None

        plugin_name, stokes, du, is_gaussian, pha_spectrum =\
            self.get_pha_spectrum(file_path, name=name)

        if bkg_file_path is not None and os.path.exists(bkg_file_path):
            _,_,_,_,bkg_spectrum = self.get_pha_spectrum(bkg_file_path, name=name)

        #self.use_poisson = False
        plugin = ixpeOGIPSpectrumPlugin(plugin_name, observation=pha_spectrum, background=bkg_spectrum, stokes=stokes, du=du)
        log.info('Plugin assigned to: %s' % stokes)
        plugin.set_active_measurements(self.energy_range)
        if is_gaussian: # this remove channels with observed_count_errors 0 counts
            log.info('Remove channels with 0 counts for spectrum %s' % stokes)
            plugin._mask = (plugin.observed_counts!=0)*plugin._mask
            plugin._apply_mask_to_original_vectors()

        self.plugins.append(plugin)

    def apply_area_correction(self, area_corrections):
        """
        Apply effective area corrections to all detector units.
        
        Applies detector-specific multiplicative corrections to the effective
        area to account for calibration uncertainties or systematic effects.
        
        Parameters
        ----------
        area_corrections : dict
            Dictionary mapping detector unit names to correction factors.
            Example: {'DU1': 0.850, 'DU2': 0.800, 'DU3': 0.782}
        
        Notes
        -----
        The corrections are fixed (not fitted) and typically derived from
        calibration observations or cross-calibration with other instruments.
        """
        for p in self.plugins:
            du = self.detector_stokes[p.name][0]
            ac = area_corrections[du]
            log.info('Using an effective area correction for %s of %.3f' % (du,ac))
            p.use_effective_area_correction(0.5,1.2)
            p.fix_effective_area_correction(ac)

    @staticmethod
    def _fit_area_correction(model, data, min_value=0.5, max_value=1.2, 
    name='ixpe', quiet=True, sim_name='_sim'):
        ''' This function is used to fit the area correction for each DU and Stokes. This is called directly only when genereating simulated data for gof estimation.
        '''
        for plugin in data.values():
            if not isinstance(plugin, ixpeOGIPSpectrumPlugin):
                continue
            du = plugin._du
            stokes = plugin._stokes
            if not quiet:
                log.info('Fitting an effective area correction for %s' % (du))
            plugin.use_effective_area_correction(min_value,max_value)
            if du == 'DU1':
                plugin.fix_effective_area_correction(1.0)
            if stokes != 'I':
                model.link(model['cons_%s_%s_%s%s' % (name, du, stokes, sim_name)], model["cons_%s_%s_I%s" % (name, du, sim_name)])

    def fit_area_correction(self, model, min_value=0.5, max_value=1.2, 
    name='ixpe', quiet=False, sim_name=''):
        """
        Enable fitting of effective area corrections for each detector unit.
        
        Creates correction parameters that allow detector effective areas to be
        adjusted during the fit. DU1 is fixed as reference, Q/U are linked to I.
        
        Parameters
        ----------
        model : Model
            Astromodels Model object
        min_value : float, optional
            Minimum correction value. Default is 0.5
        max_value : float, optional
            Maximum correction value. Default is 1.2
        name : str, optional
            Base name for plugins. Default is 'ixpe'
        quiet : bool, optional
            Suppress messages. Default is False
        sim_name : str, optional
            Suffix for parameter names. Default is ''
        
        Notes
        -----
        Must be called AFTER creating the JointLikelihood to associate model
        and data. The corrections are multiplicative: 1.0 = nominal area.
        
        Examples
        --------
        >>> jl = JointLikelihood(model, ixpe.get_datalist())
        >>> ixpe.fit_area_correction(model, min_value=0.8, max_value=1.2)
        >>> jl.fit()
        """
        ixpeOGIPSpectrumLike._fit_area_correction(model, self.get_datalist(), min_value, max_value, name, quiet, sim_name)

    def get_datalist(self):
        """
        Get a 3ML DataList containing all loaded plugins.
        
        Returns
        -------
        DataList
            3ML DataList object with all IXPE plugins for joint analysis
        """
        return DataList(*self.plugins)
    
    def get_number_of_data_points(self):
        """
        Get the total number of data points across all plugins.
        
        Returns
        -------
        int
            Total number of active energy bins summed over all plugins
        """
        return sum([p.n_data_points for p in self.plugins])

    def _sanitize_hdu(self, hdu):
        """ Sanitize the SPECTRUM extension (if needed) """
        zero_idx = hdu.data['STAT_ERR'] == 0
        if numpy.sum(zero_idx) > 0:
            log.warn('Found %d energy channels where STAT_ERR is 0: %s' % (numpy.sum(zero_idx), numpy.where(zero_idx)))
            log.warn('Forcing the corresponding RATE channels to 0!')
            hdu.data['RATE'][zero_idx] = 0
        #hdu.data['STAT_ERR'][zero_idx]  = numpy.sqrt(0.75)

    def get_irfs(self, hdr):
        rsp_file = hdr['RESPFILE']
        arf_file = hdr['ANCRFILE']

        if self.caldb is not None:
            rsp_file = os.path.join(self.caldb, rsp_file.split('caldb/')[1])
            arf_file = os.path.join(self.caldb, arf_file.split('caldb/')[1])
        return rsp_file, arf_file

    def get_simulated_dataset(self, model):
        assert( model is not None ), 'set a model to simulate around'

        self.sim_plugins = []

        for i in self.plugins:
            #still based in data using the data-dir plugins and overlaying new data -- create blank histogram?

            i.set_model(model)
            self.sim_plugins.append(i.get_simulated_dataset())

        return DataList(*self.sim_plugins)
 
class ixpeOGIPSpectrumPlugin(OGIPLike):
    """
    IXPE-specific OGIP spectrum plugin.
    
    Extends the 3ML OGIPLike plugin to handle IXPE-specific features
    including Stokes parameter tracking and detector unit identification.
    
    Attributes
    ----------
    _stokes : str
        Stokes parameter ('I', 'Q', 'U', or 'V')
    _du : str
        Detector unit identifier (e.g., 'DU1', 'DU2', 'DU3')
    """

    def __init__(self, name: str, observation, background=None, response=None, 
                 arf_file=None, spectrum_number=None, verbose=True, 
                 stokes=None, du=None):
        """
        Initialize IXPE OGIP spectrum plugin.
        
        Parameters
        ----------
        name : str
            Plugin name (usually format: '{basename}_{du}_{stokes}')
        observation : PHASpectrum
            Observation spectrum object
        background : PHASpectrum, optional
            Background spectrum object. Default is None
        response : str, optional
            Path to response file. Default is None
        arf_file : str, optional
            Path to auxiliary response file. Default is None
        spectrum_number : int, optional
            Spectrum number for PHAII files. Default is None
        verbose : bool, optional
            Enable verbose output. Default is True
        stokes : str
            Stokes parameter ('I', 'Q', 'U', or 'V')
        du : str
            Detector unit identifier (e.g., 'DU1')
        
        Raises
        ------
        AssertionError
            If stokes is not one of 'I', 'Q', 'U', 'V'
        """
        OGIPLike.__init__(self, name=name, observation=observation, 
                          background=background, response=response, 
                          arf_file=arf_file, spectrum_number=spectrum_number, 
                          verbose=verbose)
        assert stokes in ['I', 'Q', 'U', 'V']
        self._stokes = stokes
        self._du = du

    def get_simulated_dataset(self, name):
        """
        Generate a simulated dataset based on the current model.
        
        Parameters
        ----------
        name : str
            Name for the simulated dataset
        
        Returns
        -------
        ixpeOGIPSpectrumPlugin
            New plugin instance with simulated data
        """
        return super(ixpeOGIPSpectrumPlugin, self).get_simulated_dataset(
            name, stokes=self._stokes, du=self._du,
        )

