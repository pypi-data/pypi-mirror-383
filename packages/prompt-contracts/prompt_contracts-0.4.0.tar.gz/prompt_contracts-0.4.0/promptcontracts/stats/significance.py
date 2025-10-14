"""
Significance testing for paired comparisons of systems.

Provides McNemar's test for binary outcomes, bootstrap-based
difference CIs for continuous metrics, and multiple comparison correction.
"""

import numpy as np
from scipy import stats


def benjamini_hochberg_correction(p_values: list[float], alpha: float = 0.05) -> list[float]:
    """
    Benjamini-Hochberg procedure for controlling False Discovery Rate (FDR).

    Controls the expected proportion of false discoveries among all discoveries.
    More powerful than Bonferroni correction for multiple comparisons.

    Args:
        p_values: List of p-values from multiple tests
        alpha: Desired FDR level (default 0.05)

    Returns:
        List of adjusted p-values

    Example:
        >>> p_values = [0.001, 0.01, 0.03, 0.05, 0.1]
        >>> adjusted = benjamini_hochberg_correction(p_values, alpha=0.05)
        >>> adjusted
        [0.005, 0.025, 0.05, 0.0625, 0.1]

    References:
        Benjamini & Hochberg (1995). "Controlling the False Discovery Rate:
        A Practical and Powerful Approach to Multiple Testing." J. R. Stat. Soc. B 57:289-300.
    """
    if not p_values:
        return []

    p_values = np.array(p_values)
    n = len(p_values)

    # Sort p-values and get original indices
    sorted_indices = np.argsort(p_values)
    sorted_p_values = p_values[sorted_indices]

    # Calculate adjusted p-values
    adjusted_p_values = np.zeros(n)
    for i in range(n):
        # BH procedure: p_adj = p * n / rank
        rank = i + 1
        adjusted_p_values[i] = sorted_p_values[i] * n / rank

    # Ensure monotonicity (adjusted p-values should be non-decreasing)
    for i in range(n - 2, -1, -1):
        adjusted_p_values[i] = min(adjusted_p_values[i], adjusted_p_values[i + 1])

    # Cap at 1.0
    adjusted_p_values = np.minimum(adjusted_p_values, 1.0)

    # Restore original order
    final_adjusted = np.zeros(n)
    final_adjusted[sorted_indices] = adjusted_p_values

    return final_adjusted.tolist()


def mcnemar_test(a01: int, a10: int, continuity_correction: bool = True) -> float:
    """
    McNemar's test for paired binary outcomes.

    Tests null hypothesis that two related proportions are equal.
    Appropriate for comparing two systems on the same fixtures where
    outcomes are pass/fail.

    Args:
        a01: Count where system A failed and system B passed
        a10: Count where system A passed and system B failed
        continuity_correction: Apply continuity correction (default True)

    Returns:
        p-value (two-tailed)

    Example:
        >>> # System A: 80 pass, System B: 85 pass, same 100 fixtures
        >>> # Disagreements: A passed but B failed: 5, A failed but B passed: 10
        >>> mcnemar_test(a01=10, a10=5)
        0.166

    Interpretation:
        p < 0.05: significant difference between systems
        p >= 0.05: no significant difference detected

    Notes:
        Requires a01 + a10 >= 10 for reasonable approximation.
        For very small counts, use exact binomial test instead.

    References:
        McNemar (1947). "Note on the sampling error of the difference between
        correlated proportions or percentages." Psychometrika 12:153-157.
    """
    if a01 + a10 == 0:
        return 1.0  # No disagreements, perfect agreement

    if continuity_correction:
        # Apply continuity correction for better small-sample approximation
        chi_sq = (abs(a01 - a10) - 1) ** 2 / (a01 + a10)
    else:
        chi_sq = (a01 - a10) ** 2 / (a01 + a10)

    p_value = 1 - stats.chi2.cdf(chi_sq, df=1)

    return p_value


def bootstrap_diff_ci(
    metric1: list[float],
    metric2: list[float],
    B: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float]:
    """
    Bootstrap confidence interval for difference of means (metric2 - metric1).

    Useful for comparing continuous metrics (e.g., latency, F1 scores)
    between two systems on the same fixtures.

    Args:
        metric1: Values from system 1 (e.g., latencies or scores)
        metric2: Values from system 2 (same fixtures as metric1)
        B: Number of bootstrap resamples (default 1000)
        alpha: Significance level (default 0.05 for 95% CI)
        seed: Random seed for reproducibility

    Returns:
        Tuple (lower_bound, upper_bound) for difference (metric2 - metric1)

    Example:
        >>> latencies_a = [100, 120, 110, 105, 115]
        >>> latencies_b = [95, 110, 100, 98, 108]
        >>> bootstrap_diff_ci(latencies_a, latencies_b, B=1000)
        (-15.2, -3.8)

    Interpretation:
        If CI does not contain 0, the difference is statistically significant
        at the alpha level.

    Notes:
        This is a paired comparison: metric1[i] and metric2[i] must correspond
        to the same fixture.
    """
    if len(metric1) != len(metric2):
        raise ValueError("metric1 and metric2 must have same length (paired data)")

    if len(metric1) == 0:
        return (0.0, 0.0)

    np.random.seed(seed)
    metric1 = np.array(metric1)
    metric2 = np.array(metric2)
    n = len(metric1)

    differences = metric2 - metric1
    bootstrap_diffs = []

    for _ in range(B):
        # Resample pairs (preserve pairing)
        indices = np.random.choice(n, size=n, replace=True)
        resample_diff = differences[indices]
        bootstrap_diffs.append(np.mean(resample_diff))

    lower = np.percentile(bootstrap_diffs, 100 * alpha / 2)
    upper = np.percentile(bootstrap_diffs, 100 * (1 - alpha / 2))

    return (float(lower), float(upper))
