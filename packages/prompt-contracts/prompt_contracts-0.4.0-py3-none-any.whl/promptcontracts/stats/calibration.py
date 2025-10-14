"""
CI Calibration Module

Implements simulation studies to validate empirical vs. nominal coverage
of confidence interval methods (Wilson, Jeffreys, Bootstrap).

References:
- Brown, Cai & DasGupta (2001). "Interval Estimation for a Binomial Proportion."
- Efron & Tibshirani (1993). "An Introduction to the Bootstrap."
"""

import numpy as np

from .intervals import jeffreys_interval, percentile_bootstrap_ci, wilson_interval


def calibrate_ci_coverage(
    method: str,
    n_sims: int = 10000,
    n_range: tuple[int, int] = (10, 200),
    p_range: tuple[float, float] = (0.1, 0.9),
    confidence: float = 0.95,
    seed: int = 42,
) -> dict:
    """
    Calibrate confidence interval coverage through simulation.

    Simulates binomial data and computes empirical coverage rates
    to validate CI methods against nominal coverage.

    Args:
        method: CI method ('wilson', 'jeffreys', 'bootstrap')
        n_sims: Number of simulation runs
        n_range: Range of sample sizes to test (min, max)
        p_range: Range of true proportions to test (min, max)
        confidence: Nominal confidence level
        seed: Random seed for reproducibility

    Returns:
        Dict with calibration results including empirical coverage

    Example:
        >>> results = calibrate_ci_coverage('wilson', n_sims=1000)
        >>> results['empirical_coverage']
        0.948
    """
    np.random.seed(seed)

    # Generate test scenarios
    n_values = np.random.randint(n_range[0], n_range[1] + 1, n_sims)
    p_values = np.random.uniform(p_range[0], p_range[1], n_sims)

    coverage_count = 0
    ci_widths = []
    edge_cases = {"n_small": 0, "p_extreme": 0, "boundary": 0}

    for i in range(n_sims):
        n = n_values[i]
        p_true = p_values[i]

        # Generate binomial data
        successes = np.random.binomial(n, p_true)

        # Compute CI based on method
        if method == "wilson":
            ci_lower, ci_upper = wilson_interval(successes, n, confidence)
        elif method == "jeffreys":
            ci_lower, ci_upper = jeffreys_interval(successes, n, confidence)
        elif method == "bootstrap":
            # Generate binary outcomes for bootstrap
            outcomes = np.concatenate([np.ones(successes), np.zeros(n - successes)])
            ci_lower, ci_upper = percentile_bootstrap_ci(
                outcomes.tolist(), B=1000, alpha=1 - confidence
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        # Check coverage
        if ci_lower <= p_true <= ci_upper:
            coverage_count += 1

        # Track CI width
        ci_widths.append(ci_upper - ci_lower)

        # Track edge cases
        if n < 10:
            edge_cases["n_small"] += 1
        if p_true < 0.05 or p_true > 0.95:
            edge_cases["p_extreme"] += 1
        if successes == 0 or successes == n:
            edge_cases["boundary"] += 1

    empirical_coverage = coverage_count / n_sims
    mean_width = np.mean(ci_widths)
    width_std = np.std(ci_widths)

    return {
        "method": method,
        "nominal_coverage": confidence,
        "empirical_coverage": empirical_coverage,
        "coverage_error": empirical_coverage - confidence,
        "mean_ci_width": mean_width,
        "ci_width_std": width_std,
        "n_simulations": n_sims,
        "edge_cases": edge_cases,
        "calibration_status": "good" if abs(empirical_coverage - confidence) < 0.02 else "poor",
    }


def compare_ci_methods(
    n_sims: int = 10000,
    methods: list[str] = None,
    confidence: float = 0.95,
    seed: int = 42,
) -> dict:
    """
    Compare multiple CI methods through calibration.

    Args:
        n_sims: Number of simulation runs
        methods: List of methods to compare
        confidence: Nominal confidence level
        seed: Random seed

    Returns:
        Dict with comparison results for all methods
    """
    if methods is None:
        methods = ["wilson", "jeffreys", "bootstrap"]

    results = {}

    for method in methods:
        results[method] = calibrate_ci_coverage(
            method=method, n_sims=n_sims, confidence=confidence, seed=seed
        )

    # Find best method (closest to nominal coverage)
    best_method = min(
        results.keys(), key=lambda m: abs(results[m]["empirical_coverage"] - confidence)
    )

    return {
        "methods": results,
        "best_method": best_method,
        "nominal_coverage": confidence,
        "summary": {
            method: {
                "empirical_coverage": results[method]["empirical_coverage"],
                "coverage_error": results[method]["coverage_error"],
                "mean_width": results[method]["mean_ci_width"],
            }
            for method in methods
        },
    }


def generate_calibration_report(
    n_sims: int = 10000,
    confidence: float = 0.95,
    seed: int = 42,
) -> str:
    """
    Generate a comprehensive CI calibration report.

    Returns:
        Formatted string report
    """
    results = compare_ci_methods(n_sims=n_sims, confidence=confidence, seed=seed)

    report = f"""
CI Calibration Report
====================

Nominal Coverage: {confidence:.1%}
Simulations: {n_sims:,}

Method Comparison:
"""

    for method, data in results["methods"].items():
        report += f"""
{method.upper()}:
  Empirical Coverage: {data['empirical_coverage']:.3f} ({data['empirical_coverage']:.1%})
  Coverage Error: {data['coverage_error']:+.3f}
  Mean CI Width: {data['mean_ci_width']:.3f}
  Status: {data['calibration_status'].upper()}
"""

    report += f"""
Best Method: {results['best_method'].upper()}
Recommendation: Use {results['best_method']} for n≥10, Jeffreys for n<10
"""

    return report
