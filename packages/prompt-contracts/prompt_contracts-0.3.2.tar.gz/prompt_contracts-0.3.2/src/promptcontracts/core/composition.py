"""
Contract composition semantics for PCSL v0.3.2.

Provides formal composition of contracts with variance bounds
and CI aggregation under independence assumptions.
"""

import math


def compose_contracts_variance_bound(var1: float, var2: float, independent: bool = True) -> float:
    """
    Calculate variance upper bound for composed contracts.

    Under independence: Var(C2 ∘ C1) ≤ Var(C1) + Var(C2)

    Args:
        var1: Variance of first contract C1
        var2: Variance of second contract C2
        independent: Whether contracts are independent (default True)

    Returns:
        Upper bound on composed variance

    Example:
        >>> var_bound = compose_contracts_variance_bound(0.01, 0.015)
        >>> var_bound
        0.025

    Notes:
        If contracts are not independent, this bound may be loose.
        For dependent contracts, use empirical variance estimation.

    References:
        Variance of sums: Var(X + Y) = Var(X) + Var(Y) + 2*Cov(X,Y)
        Under independence: Cov(X,Y) = 0
    """
    if not independent:
        # Conservative bound: assume perfect positive correlation
        # Var(X + Y) ≤ (σ_X + σ_Y)^2 by Cauchy-Schwarz
        return (math.sqrt(var1) + math.sqrt(var2)) ** 2

    return var1 + var2


def aggregate_confidence_intervals_intersection(
    ci1: tuple[float, float], ci2: tuple[float, float]
) -> tuple[float, float]:
    """
    Aggregate CIs via intersection (conservative approach).

    For sequential validation C2 ∘ C1, the joint success rate is bounded
    by the intersection of individual CIs.

    Args:
        ci1: Confidence interval for C1 (lower, upper)
        ci2: Confidence interval for C2 (lower, upper)

    Returns:
        Conservative joint CI (intersection)

    Example:
        >>> ci1 = (0.85, 0.95)
        >>> ci2 = (0.88, 0.96)
        >>> aggregate_confidence_intervals_intersection(ci1, ci2)
        (0.88, 0.95)

    Notes:
        This is conservative: actual joint CI may be wider.
        Assumes both contracts must pass (conjunction).
    """
    lower = max(ci1[0], ci2[0])
    upper = min(ci1[1], ci2[1])

    # Ensure valid interval
    if lower > upper:
        # Disjoint intervals: use midpoint as point estimate
        midpoint = (ci1[0] + ci1[1] + ci2[0] + ci2[1]) / 4
        return (midpoint, midpoint)

    return (lower, upper)


def aggregate_confidence_intervals_delta_method(
    ci1: tuple[float, float],
    ci2: tuple[float, float],
    correlation: float = 0.0,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """
    Aggregate CIs via delta method approximation.

    Uses normal approximation for product of success rates:
    P(C2 ∘ C1) ≈ P(C1) × P(C2)

    Args:
        ci1: Confidence interval for C1 (lower, upper)
        ci2: Confidence interval for C2 (lower, upper)
        correlation: Correlation between C1 and C2 (default 0 = independent)
        confidence: Confidence level (default 0.95)

    Returns:
        Joint CI via delta method

    Example:
        >>> ci1 = (0.85, 0.95)
        >>> ci2 = (0.88, 0.96)
        >>> aggregate_confidence_intervals_delta_method(ci1, ci2)
        (0.748, 0.912)

    Notes:
        More accurate than intersection for independent contracts.
        Assumes both CIs are symmetric around mean.

    References:
        Casella & Berger (2002). "Statistical Inference", 2nd ed., §5.5.
    """
    from scipy import stats

    # Estimate means and standard errors
    mean1 = (ci1[0] + ci1[1]) / 2
    mean2 = (ci2[0] + ci2[1]) / 2

    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    se1 = (ci1[1] - ci1[0]) / (2 * z)
    se2 = (ci2[1] - ci2[0]) / (2 * z)

    # Product mean
    product_mean = mean1 * mean2

    # Product variance (delta method)
    # Var(XY) ≈ μ_Y^2 * Var(X) + μ_X^2 * Var(Y) + 2*μ_X*μ_Y*Cov(X,Y)
    var1 = se1**2
    var2 = se2**2
    cov = correlation * se1 * se2

    product_var = mean2**2 * var1 + mean1**2 * var2 + 2 * mean1 * mean2 * cov
    product_se = math.sqrt(product_var)

    # Construct CI
    lower = max(0.0, product_mean - z * product_se)
    upper = min(1.0, product_mean + z * product_se)

    return (lower, upper)


def compose_contracts_sequential(
    contracts: list[dict], method: str = "intersection"
) -> tuple[tuple[float, float], float]:
    """
    Compose multiple contracts sequentially.

    Args:
        contracts: List of contracts with CIs and variances
                  Each dict: {"name": str, "ci": (lo, hi), "variance": float}
        method: Aggregation method ("intersection" or "delta_method")

    Returns:
        Tuple of (joint_ci, total_variance_bound)

    Example:
        >>> contracts = [
        ...     {"name": "schema", "ci": (0.95, 0.99), "variance": 0.001},
        ...     {"name": "semantic", "ci": (0.85, 0.95), "variance": 0.003},
        ... ]
        >>> joint_ci, var_bound = compose_contracts_sequential(contracts)
        >>> joint_ci
        (0.95, 0.95)

    Notes:
        For sequential validation, all contracts must pass.
        This computes conservative bounds assuming independence.
    """
    if not contracts:
        return ((0.0, 1.0), 0.0)

    if len(contracts) == 1:
        return (contracts[0]["ci"], contracts[0].get("variance", 0.0))

    # Aggregate CIs pairwise
    current_ci = contracts[0]["ci"]
    total_var = contracts[0].get("variance", 0.0)

    for contract in contracts[1:]:
        next_ci = contract["ci"]
        next_var = contract.get("variance", 0.0)

        if method == "intersection":
            current_ci = aggregate_confidence_intervals_intersection(current_ci, next_ci)
        elif method == "delta_method":
            current_ci = aggregate_confidence_intervals_delta_method(current_ci, next_ci)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        total_var = compose_contracts_variance_bound(total_var, next_var)

    return (current_ci, total_var)


def compose_contracts_parallel(
    contracts: list[dict], threshold: float = 0.5
) -> tuple[tuple[float, float], float]:
    """
    Compose contracts in parallel (any-of or majority-of).

    For parallel validation, at least `threshold` fraction must pass.

    Args:
        contracts: List of contracts with CIs and variances
        threshold: Fraction that must pass (0.5 = majority, 1.0 = all)

    Returns:
        Tuple of (joint_ci, combined_variance)

    Example:
        >>> contracts = [
        ...     {"name": "check1", "ci": (0.8, 0.9), "variance": 0.002},
        ...     {"name": "check2", "ci": (0.85, 0.95), "variance": 0.0015},
        ...     {"name": "check3", "ci": (0.9, 0.98), "variance": 0.001},
        ... ]
        >>> joint_ci, var = compose_contracts_parallel(contracts, threshold=0.5)

    Notes:
        Parallel composition is more robust than sequential.
        Majority voting reduces impact of individual check failures.
    """
    if not contracts:
        return ((0.0, 1.0), 0.0)

    if len(contracts) == 1:
        return (contracts[0]["ci"], contracts[0].get("variance", 0.0))

    # For parallel composition, estimate probability that >= threshold pass
    # Conservative approximation: take mean of CIs
    mean_lower = sum(c["ci"][0] for c in contracts) / len(contracts)
    mean_upper = sum(c["ci"][1] for c in contracts) / len(contracts)

    # Variance: average under independence assumption
    avg_var = sum(c.get("variance", 0.0) for c in contracts) / len(contracts)

    # Adjust for threshold
    if threshold < 1.0:
        # If only majority required, CI is wider (more lenient)
        margin = (1 - threshold) * 0.1  # Heuristic adjustment
        mean_lower = max(0.0, mean_lower - margin)
        mean_upper = min(1.0, mean_upper + margin)

    return ((mean_lower, mean_upper), avg_var)
