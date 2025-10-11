import numpy as np
from lightcurvelynx.astro_utils.noise_model import poisson_bandflux_std
from numpy.testing import assert_allclose


def test_poisson_flux_std_flux():
    """Test poisson_flux_std for photon noise dominated regime"""
    # The results should be independent of some input parameters
    rng = np.random.default_rng(None)

    flux = 10 ** rng.uniform(0.0, 5.0, 100)
    expected_flux_err = np.sqrt(flux)

    flux_err = poisson_bandflux_std(
        bandflux=flux,
        total_exposure_time=rng.uniform(),
        exposure_count=rng.integers(1, 100),
        psf_footprint=rng.uniform(),
        sky=0.0,
        zp=1.0,
        readout_noise=0.0,
        dark_current=0.0,
    )

    assert_allclose(flux_err, expected_flux_err, rtol=1e-10)


def test_poisson_flux_std_sky():
    """Test poisson_flux_std for sky noise dominated regime"""
    # The results should be independent of some input parameters
    rng = np.random.default_rng(None)

    n = 100

    zp = 10.0
    sky = 10 ** rng.uniform(-2.0, 2.0, n)
    psf_footprint = 10 ** rng.uniform(0.0, 2.0, n)
    expected_flux_err = np.sqrt(sky * psf_footprint) * zp

    flux_err = poisson_bandflux_std(
        bandflux=0.0,
        total_exposure_time=rng.uniform(),
        exposure_count=rng.integers(1, 100),
        psf_footprint=psf_footprint,
        sky=sky,
        zp=zp,
        readout_noise=0.0,
        dark_current=0.0,
    )

    assert_allclose(flux_err, expected_flux_err, rtol=1e-10)


def test_poisson_flux_std_readout():
    """Test poisson_flux_std for readout noise dominated regime"""
    # The results should be independent of some input parameters
    rng = np.random.default_rng(None)

    n = 100

    readout_noise = 10 ** rng.uniform(-2.0, 2.0, n)
    psf_footprint = 10 ** rng.uniform(0.0, 2.0, n)
    exposure_count = rng.integers(1, 100, n)
    expected_flux_err = readout_noise * np.sqrt(psf_footprint) * np.sqrt(exposure_count)

    flux_err = poisson_bandflux_std(
        bandflux=0.0,
        total_exposure_time=rng.uniform(),
        exposure_count=exposure_count,
        psf_footprint=psf_footprint,
        sky=0.0,
        zp=1.0,
        readout_noise=readout_noise,
        dark_current=0.0,
    )

    assert_allclose(flux_err, expected_flux_err, rtol=1e-10)


def test_poisson_flux_std_dark():
    """Test poisson_flux_std for dark current noise dominated regime"""
    # The results should be independent of some input parameters
    rng = np.random.default_rng(None)

    n = 100

    dark_current = 10 ** rng.uniform(-2.0, 2.0, n)
    total_exposure_time = rng.uniform(1.0, 3.0, n)
    psf_footprint = 10 ** rng.uniform(0.0, 2.0, n)

    dark_current_total = dark_current * total_exposure_time * psf_footprint
    expected_flux_err = np.sqrt(dark_current_total)

    flux_err = poisson_bandflux_std(
        bandflux=0.0,
        total_exposure_time=total_exposure_time,
        exposure_count=rng.integers(1, 100, n),
        psf_footprint=psf_footprint,
        sky=0.0,
        zp=1.0,
        readout_noise=0.0,
        dark_current=dark_current,
    )

    assert_allclose(flux_err, expected_flux_err, rtol=1e-10)


def readout_noise_function(exptime):
    """Readout noise function"""
    return 10.0 * exptime


def test_readout_noise_from_function():
    """Test poisson_flux_std for readout noise dominated regime,
    with readout noise given as a function of exposure times"""
    # The results should be independent of some input parameters
    rng = np.random.default_rng(None)

    n = 100

    psf_footprint = 10 ** rng.uniform(0.0, 2.0, n)
    exposure_time = rng.uniform(30, 100, n)
    expected_flux_err = readout_noise_function(exptime=exposure_time)

    flux_err = poisson_bandflux_std(
        bandflux=0.0,
        total_exposure_time=exposure_time,
        exposure_count=1,
        psf_footprint=psf_footprint,
        sky=0.0,
        zp=1.0,
        readout_noise=readout_noise_function,
        dark_current=0.0,
    )

    assert_allclose(flux_err, expected_flux_err, rtol=1e-10)
