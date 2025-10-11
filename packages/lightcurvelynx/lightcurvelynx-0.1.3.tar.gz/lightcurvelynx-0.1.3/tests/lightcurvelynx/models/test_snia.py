import numpy as np
from lightcurvelynx.example_runs.simulate_snia import run_snia_end2end


def test_snia_end2end(oversampled_observations, passbands_dir):
    """Test that the end to end run works."""
    rng = np.random.default_rng(123)

    solid_angle = 0.0001
    res_list, passbands = run_snia_end2end(
        oversampled_observations,
        passbands_dir,
        solid_angle=solid_angle,
        nsample=4,
        rng_info=rng,
    )
    assert len(passbands) == 2
    assert len(res_list) == 4

    num_samples = 1
    res_list, passbands = run_snia_end2end(
        oversampled_observations,
        passbands_dir,
        solid_angle=solid_angle,
        nsample=num_samples,
        rng_info=rng,
    )
    assert len(res_list) == num_samples
    assert len(passbands) == 2
