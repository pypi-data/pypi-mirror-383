"""
Confidence interval methods for proportions.

Implements exact binomial intervals (Wilson, Jeffreys) and bootstrap validation
with support for block bootstrap to handle dependencies from repairs/batching.

References:
- Brown, Cai & DasGupta (2001). "Interval Estimation for a Binomial Proportion."
  Statistical Science, 16(2):101-133.
- Efron & Tibshirani (1993). "An Introduction to the Bootstrap."
"""

import math

import numpy as np
from scipy import stats


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
    seed: int = 42,
) -> tuple[float, float]:
    """
    Percentile bootstrap confidence interval.

    Supports block bootstrap for dependent data (e.g., when repairs introduce
    dependencies or when batching affects samples).

    Args:
        values: Observed values (e.g., per-sample success indicators)
        B: Number of bootstrap resamples (default 1000)
        alpha: Significance level (default 0.05 for 95% CI)
        block: Block size for block bootstrap (None = standard bootstrap)
        seed: Random seed for reproducibility

    Returns:
        Tuple (lower_bound, upper_bound) of (1-alpha) CI

    Example:
        >>> values = [1, 1, 0, 1, 1, 0, 1, 1, 1, 0]  # 7/10 success
        >>> percentile_bootstrap_ci(values, B=1000)
        (0.4, 1.0)

    Notes:
        Block bootstrap (Künsch 1989) handles dependencies by resampling
        contiguous blocks instead of individual observations.
    """
    np.random.seed(seed)
    values = np.array(values)
    n = len(values)

    if n == 0:
        return (0.0, 1.0)

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
