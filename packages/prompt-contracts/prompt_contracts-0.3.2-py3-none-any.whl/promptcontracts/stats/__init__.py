"""
Statistical utilities for PCSL v0.3.2.

Provides exact confidence intervals, bootstrap validation, power analysis,
and significance testing for rigorous evaluation.
"""

from .intervals import jeffreys_interval, percentile_bootstrap_ci, wilson_interval
from .power import effect_size_cohens_h, required_n_for_proportion
from .significance import bootstrap_diff_ci, mcnemar_test

__all__ = [
    "wilson_interval",
    "jeffreys_interval",
    "percentile_bootstrap_ci",
    "required_n_for_proportion",
    "effect_size_cohens_h",
    "mcnemar_test",
    "bootstrap_diff_ci",
]
