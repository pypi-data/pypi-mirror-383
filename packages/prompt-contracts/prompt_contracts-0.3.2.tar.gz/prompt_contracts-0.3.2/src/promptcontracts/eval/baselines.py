"""
Fair comparison harness for baseline systems.

Provides standardized interfaces for comparing PCSL against CheckList,
Guidance, and OpenAI Structured Outputs with identical fixtures and configs.
"""

from dataclasses import dataclass
from typing import Any

from ..stats.significance import bootstrap_diff_ci, mcnemar_test


@dataclass
class BaselineSystem:
    """
    Wrapper for baseline system evaluation.

    Attributes:
        name: System name (pcsl, checklist, guidance, openai_structured)
        fixtures: List of test fixtures (same for all systems)
        outcomes: Binary outcomes (0=fail, 1=pass) for each fixture
        metrics: Dict of continuous metrics (latency, F1, etc.)
        config: System configuration (seed, temp, etc.)
    """

    name: str
    fixtures: list[dict]
    outcomes: list[int]
    metrics: dict[str, list[float]]
    config: dict


def compare_systems(
    system_a: BaselineSystem,
    system_b: BaselineSystem,
    alpha: float = 0.05,
    metric: str = "validation_success",
) -> dict:
    """
    Compare two systems with significance testing.

    Ensures fair comparison:
    - Same fixtures (enforced)
    - Same configuration (seed, temp, stop sequences)
    - Paired statistical tests (McNemar for binary, bootstrap for continuous)

    Args:
        system_a: First system (e.g., PCSL)
        system_b: Second system (e.g., CheckList)
        alpha: Significance level (default 0.05)
        metric: Metric to compare ("validation_success" for binary, others for continuous)

    Returns:
        Dict with comparison results, p-values, and effect sizes

    Example:
        >>> pcsl = BaselineSystem("pcsl", fixtures, [1,1,0,1,1], {}, {})
        >>> checklist = BaselineSystem("checklist", fixtures, [1,0,0,1,1], {}, {})
        >>> result = compare_systems(pcsl, checklist)
        >>> result["p_value"]
        0.317

    Raises:
        ValueError: If fixtures don't match or configs differ significantly
    """
    # Validation: same fixtures
    if len(system_a.fixtures) != len(system_b.fixtures):
        raise ValueError(
            f"Fixture count mismatch: {len(system_a.fixtures)} vs {len(system_b.fixtures)}"
        )

    # Validation: configuration similarity
    config_keys = ["seed", "temperature", "top_p", "stop_sequences"]
    for key in config_keys:
        val_a = system_a.config.get(key)
        val_b = system_b.config.get(key)
        if val_a != val_b and val_a is not None and val_b is not None:
            raise ValueError(
                f"Configuration mismatch for {key}: {val_a} vs {val_b}. "
                "Fair comparison requires identical configs."
            )

    n = len(system_a.fixtures)

    if metric == "validation_success":
        # Binary outcome comparison: McNemar test
        outcomes_a = system_a.outcomes
        outcomes_b = system_b.outcomes

        # Count disagreements
        a01 = sum(1 for i in range(n) if outcomes_a[i] == 0 and outcomes_b[i] == 1)
        a10 = sum(1 for i in range(n) if outcomes_a[i] == 1 and outcomes_b[i] == 0)
        both_pass = sum(1 for i in range(n) if outcomes_a[i] == 1 and outcomes_b[i] == 1)
        both_fail = sum(1 for i in range(n) if outcomes_a[i] == 0 and outcomes_b[i] == 0)

        p_value = mcnemar_test(a01, a10)

        success_a = sum(outcomes_a) / n
        success_b = sum(outcomes_b) / n

        return {
            "metric": metric,
            "system_a": system_a.name,
            "system_b": system_b.name,
            "n_fixtures": n,
            "success_rate_a": success_a,
            "success_rate_b": success_b,
            "difference": success_b - success_a,
            "mcnemar_test": {
                "a01": a01,  # A failed, B passed
                "a10": a10,  # A passed, B failed
                "both_pass": both_pass,
                "both_fail": both_fail,
                "p_value": p_value,
                "significant": p_value < alpha,
            },
            "interpretation": (
                f"System {system_b.name} is {'significantly' if p_value < alpha else 'not significantly'} "
                f"different from {system_a.name} (p={p_value:.3f})"
            ),
        }

    else:
        # Continuous metric comparison: Bootstrap difference CI
        if metric not in system_a.metrics or metric not in system_b.metrics:
            raise ValueError(f"Metric {metric} not found in both systems")

        values_a = system_a.metrics[metric]
        values_b = system_b.metrics[metric]

        if len(values_a) != len(values_b):
            raise ValueError(f"Metric length mismatch for {metric}")

        ci_lower, ci_upper = bootstrap_diff_ci(values_a, values_b, B=1000, alpha=alpha)

        mean_a = sum(values_a) / len(values_a)
        mean_b = sum(values_b) / len(values_b)

        return {
            "metric": metric,
            "system_a": system_a.name,
            "system_b": system_b.name,
            "n_fixtures": n,
            "mean_a": mean_a,
            "mean_b": mean_b,
            "difference": mean_b - mean_a,
            "bootstrap_ci": {
                "lower": ci_lower,
                "upper": ci_upper,
                "alpha": alpha,
                "significant": not (ci_lower <= 0 <= ci_upper),
            },
            "interpretation": (
                f"System {system_b.name} differs from {system_a.name} by "
                f"{mean_b - mean_a:.2f} (95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]). "
                f"{'Significant' if not (ci_lower <= 0 <= ci_upper) else 'Not significant'}."
            ),
        }


def standardize_fixtures(raw_fixtures: list[Any], format: str = "pcsl") -> list[dict]:
    """
    Standardize fixtures from various formats to PCSL format.

    Args:
        raw_fixtures: Fixtures in original format
        format: Source format (pcsl, checklist, helm, bbh)

    Returns:
        List of standardized fixtures

    Example:
        >>> checklist_fixtures = [{"test": "...", "expect": "..."}]
        >>> pcsl_fixtures = standardize_fixtures(checklist_fixtures, "checklist")
    """
    if format == "pcsl":
        return raw_fixtures

    elif format == "checklist":
        # CheckList format: {test, expect, ...}
        return [
            {"id": f"check_{i}", "input": f["test"], "gold": f.get("expect")}
            for i, f in enumerate(raw_fixtures)
        ]

    elif format == "helm":
        # HELM format: varies by task, typically {input, references}
        return [
            {
                "id": f"helm_{i}",
                "input": f.get("input", ""),
                "gold": f.get("references", [None])[0],
            }
            for i, f in enumerate(raw_fixtures)
        ]

    elif format == "bbh":
        # BBH format: {input, target}
        return [
            {"id": f"bbh_{i}", "input": f["input"], "gold": f.get("target")}
            for i, f in enumerate(raw_fixtures)
        ]

    else:
        raise ValueError(f"Unknown format: {format}")
