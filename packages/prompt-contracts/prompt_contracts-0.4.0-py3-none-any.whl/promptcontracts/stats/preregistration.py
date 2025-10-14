"""
Pre-registration Framework

Implements validation of preregistered hypotheses, endpoints, and sample sizes
to ensure reproducibility and prevent p-hacking.

References:
- OSF (Open Science Framework) preregistration standards
- Nosek et al. (2018). "The preregistration revolution."
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class PreregistrationValidator:
    """Validates evaluation against preregistered specifications."""

    def __init__(self, prereg_file: str | Path):
        """
        Initialize validator with preregistration file.

        Args:
            prereg_file: Path to preregistration JSON file
        """
        self.prereg_file = Path(prereg_file)
        self.prereg_data = self._load_preregistration()

    def _load_preregistration(self) -> dict[str, Any]:
        """Load preregistration data from JSON file."""
        if not self.prereg_file.exists():
            raise FileNotFoundError(f"Preregistration file not found: {self.prereg_file}")

        with open(self.prereg_file) as f:
            return json.load(f)

    def validate_hypotheses(self, actual_hypotheses: list[str]) -> dict[str, Any]:
        """
        Validate actual hypotheses against preregistered ones.

        Args:
            actual_hypotheses: List of hypotheses tested

        Returns:
            Validation results
        """
        prereg_hypotheses = self.prereg_data.get("hypotheses", [])

        # Check for exact matches
        exact_matches = []
        new_hypotheses = []
        missing_hypotheses = []

        for hyp in actual_hypotheses:
            if hyp in prereg_hypotheses:
                exact_matches.append(hyp)
            else:
                new_hypotheses.append(hyp)

        for hyp in prereg_hypotheses:
            if hyp not in actual_hypotheses:
                missing_hypotheses.append(hyp)

        return {
            "preregistered_count": len(prereg_hypotheses),
            "actual_count": len(actual_hypotheses),
            "exact_matches": exact_matches,
            "new_hypotheses": new_hypotheses,
            "missing_hypotheses": missing_hypotheses,
            "compliance_rate": len(exact_matches) / max(len(prereg_hypotheses), 1),
            "valid": len(new_hypotheses) == 0 and len(missing_hypotheses) == 0,
        }

    def validate_sample_sizes(self, actual_samples: dict[str, int]) -> dict[str, Any]:
        """
        Validate actual sample sizes against preregistered ones.

        Args:
            actual_samples: Dict mapping task names to sample sizes

        Returns:
            Validation results
        """
        prereg_samples = self.prereg_data.get("sample_sizes", {})

        validation_results = {}
        total_compliance = 0

        for task, prereg_n in prereg_samples.items():
            actual_n = actual_samples.get(task, 0)

            # Allow some flexibility (±10%)
            tolerance = max(1, int(prereg_n * 0.1))
            compliant = abs(actual_n - prereg_n) <= tolerance

            validation_results[task] = {
                "preregistered_n": prereg_n,
                "actual_n": actual_n,
                "difference": actual_n - prereg_n,
                "tolerance": tolerance,
                "compliant": compliant,
            }

            if compliant:
                total_compliance += 1

        return {
            "task_validations": validation_results,
            "total_tasks": len(prereg_samples),
            "compliant_tasks": total_compliance,
            "compliance_rate": total_compliance / max(len(prereg_samples), 1),
            "valid": total_compliance == len(prereg_samples),
        }

    def validate_endpoints(self, actual_endpoints: dict[str, Any]) -> dict[str, Any]:
        """
        Validate actual endpoints against preregistered ones.

        Args:
            actual_endpoints: Dict of actual endpoint specifications

        Returns:
            Validation results
        """
        prereg_endpoints = self.prereg_data.get("endpoints", {})

        validation_results = {}

        for endpoint_name, prereg_spec in prereg_endpoints.items():
            actual_spec = actual_endpoints.get(endpoint_name, {})

            # Check key specifications
            checks = {}
            for key in ["metric", "threshold", "method"]:
                prereg_val = prereg_spec.get(key)
                actual_val = actual_spec.get(key)
                checks[key] = {
                    "preregistered": prereg_val,
                    "actual": actual_val,
                    "match": prereg_val == actual_val,
                }

            validation_results[endpoint_name] = {
                "specification_checks": checks,
                "all_match": all(check["match"] for check in checks.values()),
            }

        total_endpoints = len(prereg_endpoints)
        matching_endpoints = sum(1 for v in validation_results.values() if v["all_match"])

        return {
            "endpoint_validations": validation_results,
            "total_endpoints": total_endpoints,
            "matching_endpoints": matching_endpoints,
            "compliance_rate": matching_endpoints / max(total_endpoints, 1),
            "valid": matching_endpoints == total_endpoints,
        }

    def generate_validation_report(self, actual_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate comprehensive validation report.

        Args:
            actual_data: Dict containing actual hypotheses, samples, endpoints

        Returns:
            Complete validation report
        """
        hypotheses_validation = self.validate_hypotheses(actual_data.get("hypotheses", []))

        sample_validation = self.validate_sample_sizes(actual_data.get("sample_sizes", {}))

        endpoint_validation = self.validate_endpoints(actual_data.get("endpoints", {}))

        overall_valid = (
            hypotheses_validation["valid"]
            and sample_validation["valid"]
            and endpoint_validation["valid"]
        )

        return {
            "preregistration_file": str(self.prereg_file),
            "validation_timestamp": datetime.now().isoformat(),
            "overall_valid": overall_valid,
            "hypotheses": hypotheses_validation,
            "sample_sizes": sample_validation,
            "endpoints": endpoint_validation,
            "summary": {
                "hypotheses_compliant": hypotheses_validation["valid"],
                "sample_sizes_compliant": sample_validation["valid"],
                "endpoints_compliant": endpoint_validation["valid"],
                "overall_compliance": overall_valid,
            },
        }


def create_preregistration_template(
    output_file: str | Path,
    hypotheses: list[str],
    sample_sizes: dict[str, int],
    endpoints: dict[str, dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Create a preregistration template file.

    Args:
        output_file: Path to output JSON file
        hypotheses: List of preregistered hypotheses
        sample_sizes: Dict mapping tasks to sample sizes
        endpoints: Dict of endpoint specifications
        metadata: Optional metadata (author, date, etc.)
    """
    if metadata is None:
        metadata = {
            "author": "Researcher",
            "date": datetime.now().isoformat(),
            "version": "1.0",
            "osf_url": "https://osf.io/xyz",
        }

    prereg_data = {
        "metadata": metadata,
        "hypotheses": hypotheses,
        "sample_sizes": sample_sizes,
        "endpoints": endpoints,
        "statistical_methods": {
            "confidence_intervals": "Wilson (n≥10), Jeffreys (n<10)",
            "significance_tests": "McNemar for binary, Bootstrap for continuous",
            "multiple_comparisons": "Benjamini-Hochberg FDR correction",
            "effect_sizes": "Cohen's h for proportions",
        },
        "preregistration_hash": None,  # Will be computed after creation
    }

    # Compute hash for integrity
    prereg_json = json.dumps(prereg_data, sort_keys=True, indent=2)
    prereg_hash = hashlib.sha256(prereg_json.encode()).hexdigest()
    prereg_data["preregistration_hash"] = prereg_hash

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(prereg_data, f, indent=2, sort_keys=True)

    print(f"Preregistration template created: {output_path}")
    print(f"Integrity hash: {prereg_hash}")


# Example usage and template creation
def create_example_preregistration():
    """Create example preregistration file."""
    hypotheses = [
        "PCSL validation success rate ≥ 90% (Wilson CI)",
        "PCSL significantly outperforms CheckList (McNemar p < 0.05)",
        "Repair policies maintain semantic invariance (< 5% change rate)",
        "Cross-family judge agreement κ ≥ 0.8 (substantial)",
    ]

    sample_sizes = {
        "classification_en": 100,
        "classification_de": 100,
        "extraction_finance": 100,
        "summarization_news": 100,
        "rag_qa_wiki": 120,
    }

    endpoints = {
        "validation_success": {
            "metric": "proportion",
            "threshold": 0.90,
            "method": "Wilson interval",
        },
        "system_comparison": {
            "metric": "binary_outcome",
            "threshold": 0.05,
            "method": "McNemar test",
        },
        "semantic_change": {"metric": "proportion", "threshold": 0.05, "method": "Wilson interval"},
        "judge_agreement": {"metric": "kappa", "threshold": 0.8, "method": "Cohen's kappa"},
    }

    metadata = {
        "author": "Philippos Melikidis",
        "date": "2024-01-15",
        "version": "1.0",
        "osf_url": "https://osf.io/xyz",
        "study_title": "PCSL v0.4.0 Framework Validation",
    }

    create_preregistration_template(
        "preregistration/pcsl_v0.4.0_preregistration.json",
        hypotheses,
        sample_sizes,
        endpoints,
        metadata,
    )


if __name__ == "__main__":
    create_example_preregistration()
