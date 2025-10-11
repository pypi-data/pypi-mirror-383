import numpy as np
import pytest
from lightcurvelynx.utils.wave_extrapolate import (
    ConstantExtrapolation,
    ExponentialDecay,
    LastValueExtrapolation,
    LinearDecay,
    WaveExtrapolationModel,
)


def test_wave_extrapolation_model():
    """Test the base class for the extrapolation methods."""
    # Create an instance of the base class
    extrapolator = WaveExtrapolationModel()

    # Test that the __call__ method returns a zero matrix
    last_wave = 1000.0
    last_flux = np.array([100.0, 200.0, 300.0])
    query_waves = np.array([1000.0, 1025.0, 1050.0, 1200.0])
    result = extrapolator(last_wave, last_flux, query_waves)
    expected_result = np.zeros((3, 4))
    np.testing.assert_allclose(result, expected_result)


def test_constant_extrapolation():
    """Test that the constant extrapolation function works."""
    # Create an instance of the ConstantExtrapolation class
    extrapolator = ConstantExtrapolation(value=100.0)

    # Test extrapolation past the last valid point.
    last_wave = 1000.0
    last_flux = np.array([100.0, 200.0, 300.0])
    query_waves = np.array([1000.0, 1025.0, 1050.0, 1200.0])
    expected_flux = np.full((3, 4), 100.0)
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)

    # Test that we fail if the value is not positive
    with pytest.raises(ValueError):
        _ = ConstantExtrapolation(value=-1)


def test_last_value_extrapolation():
    """Test that the last value extrapolation function works."""
    # Create an instance of the LastValueExtrapolation class
    extrapolator = LastValueExtrapolation()

    # Test extrapolation past the last valid point.
    last_wave = 1000.0
    last_flux = np.array([100.0, 200.0, 300.0])
    query_waves = np.array([1000.0, 1025.0, 1050.0, 1200.0])
    expected_flux = np.array(
        [
            [100.0, 100.0, 100.0, 100.0],
            [200.0, 200.0, 200.0, 200.0],
            [300.0, 300.0, 300.0, 300.0],
        ]
    )
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)


def test_linear_decay_extrapolate():
    """Test that the linear decay function works."""
    decay_width = 100.0
    extrapolator = LinearDecay(decay_width=decay_width)

    # Test extrapolation past the last valid point.
    last_wave = 1000.0
    last_flux = np.array([100.0, 200.0, 300.0])
    query_waves = np.array([1000.0, 1025.0, 1050.0, 1075.0, 1100.0, 1150.0])
    expected_flux = np.array(
        [
            [100.0, 75.0, 50.0, 25.0, 0.0, 0.0],
            [200.0, 150.0, 100.0, 50.0, 0.0, 0.0],
            [300.0, 225.0, 150.0, 75.0, 0.0, 0.0],
        ]
    )
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)

    # Test extrapolation before the first valid point.
    query_waves = np.array([1000.0, 975.0, 950.0, 925.0, 900.0, 850.0])
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)

    # Test that we fail if the decay width is not positive
    with pytest.raises(ValueError):
        _ = LinearDecay(decay_width=-1.0)


def test_exponential_decay_extrapolate():
    """Test that the exponential decay function works."""
    extrapolator = ExponentialDecay(rate=0.1)

    # Test extrapolation past the last valid point.
    last_wave = 1000.0
    last_flux = np.array([100.0, 200.0, 300.0])
    query_waves = np.array([1000.0, 1025.0, 1050.0, 1075.0, 1100.0, 1150.0])

    t0_flux = 100.0 * np.exp([-0.0, -2.5, -5.0, -7.5, -10.0, -15.0])
    expected_flux = np.vstack((t0_flux, t0_flux * 2, t0_flux * 3))
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)

    # Test extrapolation before the first valid point.
    query_waves = np.array([1000.0, 975.0, 950.0, 925.0, 900.0, 850.0])
    result = extrapolator(last_wave, last_flux, query_waves)
    np.testing.assert_allclose(result, expected_flux)

    # Test that we fail if the decay rate is not positive
    with pytest.raises(ValueError):
        _ = ExponentialDecay(rate=-0.1)
