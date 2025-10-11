import copy
from typing import Optional

import numpy as np

from threeML.utils.spectrum.spectrum_likelihood import BinnedStatistic
from threeML.io.logging import setup_logger
from threeML.utils.numba_utils import nb_sum
from threeML.utils.statistics.likelihood_functions import half_chi2

log = setup_logger(__name__)

class GaussianObservedGaussianBackgroundStatistic(BinnedStatistic):
    def get_current_value(self, precalc_fluxes: Optional[np.array] = None):

        model_counts = self._spectrum_plugin.get_model(precalc_fluxes=precalc_fluxes)
        rescaled_background_counts = (
                self._spectrum_plugin.current_background_counts
                * self._spectrum_plugin.scale_factor
        )
        rescaled_background_count_errors = (
                self._spectrum_plugin.current_background_count_errors
                * self._spectrum_plugin.scale_factor
        )
        chi2_ = half_chi2(
            self._spectrum_plugin.current_observed_counts - rescaled_background_counts,
            np.sqrt(self._spectrum_plugin.current_observed_count_errors**2 +
                    rescaled_background_count_errors**2),
            model_counts,
        )

        assert np.all(np.isfinite(chi2_))

        return nb_sum(chi2_) * (-1), rescaled_background_counts

    def get_randomized_source_counts(self, source_model_counts):

        if not np.isfinite(source_model_counts[0]):
            source_model_counts[0] = 0

            log.warning("simulated spectrum had infinite counts in first channel")
            log.warning("setting to ZERO")

        idx = self._spectrum_plugin.observed_count_errors > 0

        randomized_source_counts = np.zeros_like(source_model_counts)

        randomized_source_counts[idx] = np.random.normal(
            loc=source_model_counts[idx],
            scale=self._spectrum_plugin.observed_count_errors[idx],
        )

        # Issue a warning if the generated background is less than zero, and fix it by placing it at zero
        # This is not ok if the spectrum is a polarization spectrum (Q or U) since it can be negative

        #idx = randomized_source_counts < 0  # type: np.ndarray

        #negative_source_n = nb_sum(idx)

        #if negative_source_n > 0:
        #    log.warning(
        #        "Generated source has negative counts "
        #        "in %i channels. Fixing them to zero" % (negative_source_n)
        #    )

        #    randomized_source_counts[idx] = 0

        return randomized_source_counts

    def get_randomized_source_errors(self):
        return self._spectrum_plugin.observed_count_errors

    def get_randomized_background_counts(self):
        # Now randomize the expectations.

        _, background_model_counts = self.get_current_value()

        # We cannot generate variates with zero sigma. They variates from those channel will always be zero
        # This is a limitation of this whole idea. However, remember that by construction an error of zero
        # it is only allowed when the background counts are zero as well.
        idx = self._spectrum_plugin.background_count_errors > 0

        randomized_background_counts = np.zeros_like(background_model_counts)

        randomized_background_counts[idx] = np.random.normal(
            loc=background_model_counts[idx],
            scale=self._spectrum_plugin.background_count_errors[idx],
        )

        # Issue a warning if the generated background is less than zero, and fix it by placing it at zero
        # This is not ok if the spectrum is a polarization spectrum (Q or U) since it can be negative

        #idx = randomized_background_counts < 0  # type: np.ndarray
        #negative_background_n = nb_sum(idx)
        #if negative_background_n > 0:
        #    log.warning(
        #        "Generated background has negative counts "
        #        "in %i channels. Fixing them to zero" % (negative_background_n)
        #    )
        # randomized_background_counts[idx] = 0

        return randomized_background_counts
    
    def get_randomized_background_errors(self):
        return copy.copy(self._spectrum_plugin.background_count_errors)
