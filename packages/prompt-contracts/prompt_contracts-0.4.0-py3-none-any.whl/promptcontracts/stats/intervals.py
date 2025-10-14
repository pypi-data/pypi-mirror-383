"""
Confidence interval methods for proportions.

Implements exact binomial intervals (Wilson, Jeffreys) and bootstrap validation
with support for block bootstrap to handle dependencies from repairs/batching.
Includes Politis-White estimator for optimal block length selection.

References:
- Brown, Cai & DasGupta (2001). "Interval Estimation for a Binomial Proportion."
  Statistical Science, 16(2):101-133.
- Efron & Tibshirani (1993). "An Introduction to the Bootstrap."
- Politis & White (2003). "Block bootstrap for time series."
"""

import math

import numpy as np
from scipy import stats


def politis_white_block_size(data: np.ndarray, max_block_size: int = 50) -> int:
    """
    Politis-White estimator for optimal block length in block bootstrap.

    Estimates the optimal block size for dependent data by minimizing
    the asymptotic mean squared error of the bootstrap variance estimator.

    Args:
        data: Time series or dependent data
        max_block_size: Maximum allowed block size (default 50)

    Returns:
        Optimal block size (integer)

    Example:
        >>> data = np.random.randn(100)
        >>> block_size = politis_white_block_size(data)
        >>> block_size
        8

    References:
        Politis & White (2003). "Block bootstrap for time series."
        Journal of Econometrics, 117(1):1-18.
    """
    n = len(data)
    if n < 10:
        return min(3, n)

    # Center the data
    centered_data = data - np.mean(data)

    # Estimate autocovariance function
    max_lag = min(n // 4, 20)  # Reasonable upper bound
    autocov = np.zeros(max_lag + 1)

    for lag in range(max_lag + 1):
        if lag == 0:
            autocov[lag] = np.mean(centered_data**2)
        else:
            autocov[lag] = np.mean(centered_data[:-lag] * centered_data[lag:])

    # Estimate spectral density at zero (using Parzen window)
    def parzen_window(k: int, m: int) -> float:
        """Parzen window function."""
        if abs(k) > m:
            return 0.0
        x = abs(k) / m
        if x <= 0.5:
            return 1 - 6 * x**2 + 6 * x**3
        else:
            return 2 * (1 - x) ** 3

    # Estimate spectral density
    m = max_lag // 2
    spectral_density = 0.0
    for k in range(-m, m + 1):
        if abs(k) <= max_lag:
            spectral_density += parzen_window(k, m) * autocov[abs(k)]

    # Estimate second derivative of spectral density
    second_derivative = 0.0
    for k in range(-m, m + 1):
        if abs(k) <= max_lag:
            # Simplified second derivative approximation
            weight = parzen_window(k, m) * (k**2)
            second_derivative += weight * autocov[abs(k)]

    # Politis-White formula
    if abs(second_derivative) < 1e-10:
        # Fallback to simple rule
        block_size = int(np.sqrt(n))
    else:
        # Optimal block size formula
        block_size = int(
            (2 * spectral_density**2 / abs(second_derivative)) ** (1 / 3) * n ** (1 / 3)
        )

    # Ensure reasonable bounds
    block_size = max(2, min(block_size, max_block_size, n // 2))

    return block_size


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Wilson score interval for binomial proportion.

    More reliable than normal approximation for small n or extreme proportions.
    Recommended as default for n >= 10.

    Args:
        successes: Number of successes
        n: Total number of trials
        confidence: Confidence level (default 0.95)

    Returns:
        Tuple (lower_bound, upper_bound)

    Example:
        >>> wilson_interval(85, 100, 0.95)
        (0.770, 0.910)

    References:
        Wilson (1927). "Probable Inference, the Law of Succession, and Statistical
        Inference." JASA 22:209-212.
    """
    if n == 0:
        return (0.0, 1.0)

    p_hat = successes / n
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    z_sq = z * z

    denominator = 1 + z_sq / n
    center = (p_hat + z_sq / (2 * n)) / denominator
    margin = z * math.sqrt(p_hat * (1 - p_hat) / n + z_sq / (4 * n * n)) / denominator

    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)

    return (lower, upper)


def jeffreys_interval(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """
    Jeffreys interval for binomial proportion using Beta posterior.

    Uses Jeffreys prior Beta(0.5, 0.5) which is invariant to reparameterization.
    Preferred for very small n (< 10) or when successes ∈ {0, n}.

    Args:
        successes: Number of successes
        n: Total number of trials
        confidence: Confidence level (default 0.95)

    Returns:
        Tuple (lower_bound, upper_bound)

    Example:
        >>> jeffreys_interval(3, 5, 0.95)
        (0.188, 0.950)

    References:
        Brown, Cai & DasGupta (2001), Section 4.
    """
    if n == 0:
        return (0.0, 1.0)

    alpha = (1 - confidence) / 2
    a = successes + 0.5
    b = n - successes + 0.5

    lower = stats.beta.ppf(alpha, a, b) if successes > 0 else 0.0
    upper = stats.beta.ppf(1 - alpha, a, b) if successes < n else 1.0

    return (lower, upper)


def percentile_bootstrap_ci(
    values: list[float],
    B: int = 1000,
    alpha: float = 0.05,
    block: int | None = None,
    auto_block: bool = False,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Percentile bootstrap confidence interval.

    Supports block bootstrap for dependent data (e.g., when repairs introduce
    dependencies or when batching affects samples). Can automatically estimate
    optimal block size using Politis-White estimator.

    Args:
        values: Observed values (e.g., per-sample success indicators)
        B: Number of bootstrap resamples (default 1000)
        alpha: Significance level (default 0.05 for 95% CI)
        block: Block size for block bootstrap (None = standard bootstrap)
        auto_block: If True, automatically estimate optimal block size
        seed: Random seed for reproducibility

    Returns:
        Tuple (lower_bound, upper_bound) of (1-alpha) CI

    Example:
        >>> values = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0]  # 7/10 success
        >>> percentile_bootstrap_ci(values, B=1000)
        (0.4, 1.0)

        >>> # With automatic block size estimation
        >>> percentile_bootstrap_ci(values, auto_block=True)
        (0.3, 1.0)

    Notes:
        Block bootstrap (Künsch 1989) handles dependencies by resampling
        contiguous blocks instead of individual observations.
        Politis-White estimator provides data-driven optimal block size.
    """
    np.random.seed(seed)
    values = np.array(values)
    n = len(values)

    if n == 0:
        return (0.0, 1.0)

    # Auto-estimate block size if requested
    if auto_block and block is None:
        block = politis_white_block_size(values)
        print(f"Auto-estimated block size: {block}")

    bootstrap_means = []

    for _ in range(B):
        if block is None:
            # Standard bootstrap: resample with replacement
            resample = np.random.choice(values, size=n, replace=True)
        else:
            # Block bootstrap: resample blocks
            num_blocks = math.ceil(n / block)
            blocks = []
            for _ in range(num_blocks):
                start_idx = np.random.randint(0, max(1, n - block + 1))
                blocks.append(values[start_idx : start_idx + block])
            resample = np.concatenate(blocks)[:n]

        bootstrap_means.append(np.mean(resample))

    lower = np.percentile(bootstrap_means, 100 * alpha / 2)
    upper = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))

    return (float(lower), float(upper))
