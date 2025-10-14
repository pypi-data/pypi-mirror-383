"""
Evaluation utilities for PCSL v0.3.2.

Provides repair analysis, baseline comparisons, benchmark loaders,
and audit harness for regulatory compliance.
"""

from .audit_harness import create_audit_bundle, create_audit_manifest, verify_audit_bundle
from .baselines import BaselineSystem, compare_systems, standardize_fixtures
from .bench_loaders import create_ep_for_benchmark, load_bbh_subset, load_helm_subset
from .repair_analysis import (
    RepairEvent,
    analyze_repair_events,
    estimate_semantic_change,
    generate_repair_sensitivity_report,
)

__all__ = [
    "RepairEvent",
    "estimate_semantic_change",
    "generate_repair_sensitivity_report",
    "analyze_repair_events",
    "BaselineSystem",
    "compare_systems",
    "standardize_fixtures",
    "load_helm_subset",
    "load_bbh_subset",
    "create_ep_for_benchmark",
    "create_audit_bundle",
    "create_audit_manifest",
    "verify_audit_bundle",
]
