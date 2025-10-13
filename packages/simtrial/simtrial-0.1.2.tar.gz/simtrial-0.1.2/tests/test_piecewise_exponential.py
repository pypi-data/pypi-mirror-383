import math
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import cast

import numpy as np
import pytest
from numpy.typing import NDArray

import simtrial.piecewise_exponential as piecewise_module
from simtrial.piecewise_exponential import PiecewiseExponential, set_random_seed

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class DeterministicRng:
    """
    Deterministic generator that replays predefined uniform variates.

    Args:
        uniforms: Sequence of uniform random variates in the [0, 1) interval.
    """

    def __init__(self, uniforms: Iterable[float]) -> None:
        self._uniforms = np.asarray(list(uniforms), dtype=float)
        if self._uniforms.ndim != 1:
            raise ValueError("uniforms must be a one-dimensional sequence")
        self._index = 0

    def uniform(self, size: int | tuple[int, ...] | None = None) -> float | np.ndarray:
        """
        Return deterministically replayed uniform draws.

        Args:
            size: Shape of the requested draws.

        Returns:
            Either a scalar or an array of uniform values.
        """

        if size is None:
            if self._index >= self._uniforms.size:
                raise RuntimeError("Not enough uniform values provided")
            value = float(self._uniforms[self._index])
            self._index += 1
            return value

        if isinstance(size, tuple):
            count = int(np.prod(size, dtype=int))
            shape = size
        else:
            count = int(size)
            shape = (size,)

        if self._index + count > self._uniforms.size:
            raise RuntimeError("Not enough uniform values provided")

        values = self._uniforms[self._index : self._index + count]
        self._index += count
        return values.reshape(shape)


@pytest.mark.parametrize("seed", [42, 2077])
def test_set_random_seed_reproducibility(seed: int) -> None:
    """
    Verify that seeding produces reproducible draws.
    """

    durations = [1.0]
    rates = [2.0]

    set_random_seed(seed)
    first = PiecewiseExponential(durations, rates).sample(size=5)

    set_random_seed(seed)
    second = PiecewiseExponential(durations, rates).sample(size=5)

    np.testing.assert_allclose(first, second)


@pytest.mark.parametrize("rate", [0.5, 1.5, 10.0])
def test_single_interval_matches_numpy_exponential(rate: float) -> None:
    """
    Ensure a single-interval sampler aligns with NumPy's exponential draws.
    """

    rng_for_sample = np.random.default_rng(123)
    dist = PiecewiseExponential([1.0], [rate], rng=rng_for_sample)
    samples = dist.sample(size=8)

    rng_for_expected = np.random.default_rng(123)
    uniforms = rng_for_expected.uniform(size=8)
    expected = -np.log(uniforms) / rate

    np.testing.assert_allclose(samples, expected)


@pytest.mark.parametrize(
    "durations,rates",
    [
        ([0.5, 0.5, 1.0], [1.0, 3.0, 10.0]),
        ([0.25, 0.25, 0.25, 0.25], [2.0, 0.5, 1.5, 4.0]),
    ],
)
def test_multi_interval_samples_follow_inverse_cdf(
    durations: Sequence[float], rates: Sequence[float]
) -> None:
    """
    Compare samples against a manual inverse-CDF computation.
    """

    seed = 789
    rng_for_sample = np.random.default_rng(seed)
    dist = PiecewiseExponential(durations, rates, rng=rng_for_sample)
    draws = dist.sample(size=6)

    rng_for_expected = np.random.default_rng(seed)
    uniforms = rng_for_expected.uniform(size=6)
    hazards = -np.log(uniforms)

    durations_arr = np.asarray(durations, dtype=float)
    rates_arr = np.asarray(rates, dtype=float)
    cum_time = np.concatenate(([0.0], np.cumsum(durations_arr[:-1])))
    cum_hazard = np.concatenate(([0.0], np.cumsum(durations_arr[:-1] * rates_arr[:-1])))

    expected = []
    for hazard in hazards:
        index = int(np.searchsorted(cum_hazard, hazard, side="right") - 1)
        expected.append(
            cum_time[index] + (hazard - cum_hazard[index]) / rates_arr[index]
        )

    np.testing.assert_allclose(draws, expected)


@pytest.mark.parametrize(
    "durations,rates,error_message",
    [
        ([], [], "at least one interval"),
        ([1.0], [1.0, 2.0], "same length"),
        ([0.0, 1.0], [1.0, 1.0], "positive"),
        ([1.0, 1.0], [1.0, -0.5], "positive"),
        ([math.inf, 1.0], [1.0, 1.0], "finite"),
        ([[1.0, 1.0]], [1.0], "one-dimensional"),
        ([1.0, 1.0], [[1.0, 1.0]], "one-dimensional"),
        ([1.0, 0.0], [1.0, 1.0], "final duration must be positive"),
        ([1.0, math.nan], [1.0, 1.0], "finite or math.inf"),
        ([1.0], [0.0], "strictly positive"),
        ([1.0], [math.nan], "finite"),
    ],
)
def test_invalid_parameters_raise(
    durations: Sequence[float], rates: Sequence[float], error_message: str
) -> None:
    """
    Confirm invalid inputs raise informative errors.
    """

    with pytest.raises(ValueError, match=error_message):
        PiecewiseExponential(durations, rates)


def test_infinite_final_duration_is_supported() -> None:
    """
    Ensure an infinite final duration emulates the R implementation's open tail.
    """

    dist = PiecewiseExponential([1.0, math.inf], [0.5, 1.0])
    draws = cast(NDArray[np.float64], dist.sample(size=5))

    assert draws.shape == (5,)
    assert np.all(np.isfinite(draws))


def test_sample_supports_scalar_and_shape() -> None:
    """
    Confirm scalar and shaped sampling requests succeed.
    """

    dist = PiecewiseExponential([1.0, 1.0], [0.5, 1.0])

    scalar = dist.sample()
    assert isinstance(scalar, float)

    shaped = dist.sample(size=(2, 3))
    assert isinstance(shaped, np.ndarray)
    assert shaped.shape == (2, 3)
    assert shaped.dtype == np.float64


def test_default_rng_lazy_initialization() -> None:
    """
    Ensure the default RNG is created on first use when unset.
    """

    piecewise_module._RANDOM_STATE = None
    dist = PiecewiseExponential([1.0], [1.0])
    draws = dist.sample(size=3)

    assert isinstance(draws, np.ndarray)
    assert draws.shape == (3,)


@pytest.mark.parametrize(
    "fixture_name,durations,rates",
    [
        ("pwexp_single_seed_123_n20.txt", [1.0], [2.0]),
        ("pwexp_multi_seed_456_n30.txt", [0.5, 0.5, 1.0], [1.0, 3.0, 10.0]),
    ],
)
def test_python_matches_r_reference_samples(
    fixture_name: str, durations: Sequence[float], rates: Sequence[float]
) -> None:
    """
    Validate Python sampler against R reference uniforms and event times.
    """

    data = np.loadtxt(FIXTURES_DIR / fixture_name)
    uniforms = data[:, 0]
    expected = data[:, 1]

    rng = DeterministicRng(uniforms.tolist())
    dist = PiecewiseExponential(durations, rates)
    samples = dist.sample(
        size=expected.shape[0],
        rng=cast(np.random.Generator, rng),
    )

    np.testing.assert_allclose(samples, expected)


def test_scalar_sampling_with_deterministic_rng() -> None:
    """
    Confirm scalar sampling honours the provided RNG override.
    """

    data = np.loadtxt(FIXTURES_DIR / "pwexp_single_seed_123_n20.txt")
    uniform_value = float(data[0, 0])
    expected_time = float(data[0, 1])

    dist = PiecewiseExponential([1.0], [2.0])
    rng = DeterministicRng([uniform_value])
    draw = dist.sample(rng=cast(np.random.Generator, rng))

    assert math.isclose(draw, expected_time)
