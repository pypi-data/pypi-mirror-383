"""A collection of toy effect models that are primarily used for testing."""

from lightcurvelynx.effects.effect_model import EffectModel


class ConstantDimming(EffectModel):
    """An effect that dims by a constant amount. Primarily used for testing.

    Attributes
    ----------
    flux_fraction : parameter
        The fraction of flux that is passed through.
    """

    def __init__(self, flux_fraction, **kwargs):
        super().__init__(**kwargs)
        self.add_effect_parameter("flux_fraction", flux_fraction)

    def apply(
        self,
        flux_density,
        times=None,
        wavelengths=None,
        flux_fraction=None,
        rng_info=None,
        **kwargs,
    ):
        """Apply the effect to observations (flux_density values).

        Parameters
        ----------
        flux_density : numpy.ndarray
            A length T X N matrix of flux density values (in nJy).
        times : numpy.ndarray, optional
            A length T array of times (in MJD). Not used for this effect.
        wavelengths : numpy.ndarray, optional
            A length N array of wavelengths (in angstroms). Not used for this effect.
        flux_fraction : float, optional
            The fraction of flux that is passed through. Raises an error if None is provided.
        rng_info : numpy.random._generator.Generator, optional
            A given numpy random number generator to use for this computation. If not
            provided, the function uses the node's random number generator.
        **kwargs : `dict`, optional
           Any additional keyword arguments, including any additional
           parameters needed to apply the effect.

        Returns
        -------
        flux_density : numpy.ndarray
            A length T x N matrix of flux densities after the effect is applied (in nJy).
        """
        if flux_fraction is None:
            raise ValueError("flux_fraction must be provided")
        return flux_density * flux_fraction

    def apply_bandflux(
        self,
        bandfluxes,
        *,
        times=None,
        filters=None,
        flux_fraction=None,
        rng_info=None,
        **kwargs,
    ):
        """Apply the effect to band fluxes.

        Parameters
        ----------
        bandfluxes : numpy.ndarray
            A length T array of band fluxes (in nJy).
        times : numpy.ndarray, optional
            A length T array of times (in MJD).
        filters : numpy.ndarray, optional
            A length N array of filters. If not provided, the effect is applied to all
            band fluxes.
        flux_fraction : float, optional
            The fraction of flux that is passed through. Raises an error if None is provided.
        rng_info : numpy.random._generator.Generator, optional
            A given numpy random number generator to use for this computation. If not
            provided, the function uses the node's random number generator.
        **kwargs : `dict`, optional
           Any additional keyword arguments, including any additional
           parameters needed to apply the effect.

        Returns
        -------
        bandfluxes : numpy.ndarray
            A length T array of band fluxes after the effect is applied (in nJy).
        """
        if flux_fraction is None:
            raise ValueError("flux_fraction must be provided")
        return bandfluxes * flux_fraction
