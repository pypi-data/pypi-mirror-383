"""
Power analysis and effect size calculations for proportion comparisons.

Helps determine required sample sizes for adequate statistical power
in prompt contract evaluations.
"""

import math

from scipy import stats


def required_n_for_proportion(p0: float, p1: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """
    Calculate required sample size for detecting difference in proportions.

    Uses normal approximation for two-proportion z-test.

    Args:
        p0: Baseline proportion (e.g., 0.5)
        p1: Alternative proportion (e.g., 0.7)
        alpha: Significance level (default 0.05)
        power: Desired power (default 0.8 = 80%)

    Returns:
        Required sample size per group

    Example:
        >>> required_n_for_proportion(0.5, 0.7, alpha=0.05, power=0.8)
        49

    Notes:
        This is a conservative estimate. For small effects or extreme proportions,
        consider increasing n by 10-20% to account for discreteness.

    References:
        Rosner (2015). "Fundamentals of Biostatistics", 8th ed., Section 10.3.
    """
    if not (0 < p0 < 1 and 0 < p1 < 1):
        raise ValueError("Proportions must be strictly between 0 and 1")

    if p0 == p1:
        raise ValueError("p0 and p1 must differ for power calculation")

    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    p_avg = (p0 + p1) / 2
    numerator = (
        z_alpha * math.sqrt(2 * p_avg * (1 - p_avg))
        + z_beta * math.sqrt(p0 * (1 - p0) + p1 * (1 - p1))
    ) ** 2

    denominator = (p1 - p0) ** 2

    n = numerator / denominator

    return math.ceil(n)


def effect_size_cohens_h(p1: float, p2: float) -> float:
    """
    Cohen's h effect size for difference in proportions.

    Measures the distance between two proportions on the arcsin-transformed scale.

    Args:
        p1: First proportion
        p2: Second proportion

    Returns:
        Cohen's h effect size

    Interpretation (Cohen's conventions):
        |h| < 0.2: small effect
        0.2 <= |h| < 0.5: medium effect
        |h| >= 0.5: large effect

    Example:
        >>> effect_size_cohens_h(0.7, 0.5)
        0.411

    References:
        Cohen (1988). "Statistical Power Analysis for the Behavioral Sciences", 2nd ed.
    """
    if not (0 <= p1 <= 1 and 0 <= p2 <= 1):
        raise ValueError("Proportions must be in [0, 1]")

    phi1 = 2 * math.asin(math.sqrt(p1))
    phi2 = 2 * math.asin(math.sqrt(p2))

    return abs(phi1 - phi2)
