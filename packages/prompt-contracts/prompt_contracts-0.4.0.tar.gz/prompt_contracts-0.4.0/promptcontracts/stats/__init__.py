"""
Statistical utilities for PCSL v0.4.0.

Provides exact confidence intervals, bootstrap validation, power analysis,
significance testing, multiple comparison correction, and calibration tools
for rigorous evaluation.
"""

from .calibration import calibrate_ci_coverage, compare_ci_methods, generate_calibration_report
from .intervals import (
    jeffreys_interval,
    percentile_bootstrap_ci,
    politis_white_block_size,
    wilson_interval,
)
from .power import effect_size_cohens_h, required_n_for_proportion
from .preregistration import PreregistrationValidator, create_preregistration_template
from .significance import benjamini_hochberg_correction, bootstrap_diff_ci, mcnemar_test

__all__ = [
    # Confidence intervals
    "wilson_interval",
    "jeffreys_interval",
    "percentile_bootstrap_ci",
    "politis_white_block_size",
    # Significance tests
    "mcnemar_test",
    "bootstrap_diff_ci",
    "benjamini_hochberg_correction",
    # Power analysis
    "required_n_for_proportion",
    "effect_size_cohens_h",
    # Calibration
    "calibrate_ci_coverage",
    "compare_ci_methods",
    "generate_calibration_report",
    # Pre-registration
    "PreregistrationValidator",
    "create_preregistration_template",
]
