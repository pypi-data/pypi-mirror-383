"""
Repair policy risk analysis for PCSL v0.3.2.

Provides tools for analyzing repair transformations and their impact
on semantic content and validation outcomes.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class RepairEvent:
    """
    Represents a single repair transformation.

    Attributes:
        type: Type of repair (strip_markdown_fences, strip_whitespace, etc.)
        before: Content before repair
        after: Content after repair
        changed_fields: List of JSON fields that changed (if applicable)
        semantic_diff: Whether semantic content changed (heuristic)
    """

    type: str
    before: str
    after: str
    changed_fields: list[str]
    semantic_diff: bool


def estimate_semantic_change(
    before: str, after: str, threshold: float = 0.95, use_embedding: bool = False
) -> bool:
    """
    Estimate if repair caused semantic change.

    Uses heuristic approach:
    - If only whitespace/fences changed: no semantic change
    - If JSON parseable before and after: compare semantic content
    - Optional: embedding similarity (requires embedding adapter)

    Args:
        before: Text before repair
        after: Text after repair
        threshold: Similarity threshold below which change is semantic (default 0.95)
        use_embedding: Use embedding similarity instead of heuristic (default False)

    Returns:
        True if semantic change detected, False otherwise

    Example:
        >>> before = '```json\\n{"key": "value"}\\n```'
        >>> after = '{"key": "value"}'
        >>> estimate_semantic_change(before, after)
        False

        >>> before = '{"status": "fail"}'
        >>> after = '{"status": "pass"}'
        >>> estimate_semantic_change(before, after)
        True
    """
    # Quick check: if strings are identical, no change
    if before == after:
        return False

    # Normalize whitespace for comparison
    before_normalized = " ".join(before.split())
    after_normalized = " ".join(after.split())

    if before_normalized == after_normalized:
        return False  # Only whitespace changed

    # Try JSON parsing to compare semantic content
    try:
        import json

        before_json = json.loads(before)
        after_json = json.loads(after)

        # If both parse successfully, compare
        if before_json == after_json:
            return False  # Semantically identical
        else:
            return True  # JSON content differs

    except (json.JSONDecodeError, ValueError):
        # Not valid JSON, fall back to string similarity
        pass

    if use_embedding:
        # Embedding-based similarity (requires adapter)
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            emb_before = model.encode(before)
            emb_after = model.encode(after)

            # Cosine similarity
            similarity = np.dot(emb_before, emb_after) / (
                np.linalg.norm(emb_before) * np.linalg.norm(emb_after)
            )

            return similarity < threshold

        except ImportError:
            pass  # Fall through to string-based heuristic

    # Fallback: character-level similarity
    # If > 95% of characters are the same, assume no semantic change
    from difflib import SequenceMatcher

    ratio = SequenceMatcher(None, before, after).ratio()
    return ratio < threshold


def generate_repair_sensitivity_report(
    results_off: dict, results_syntactic: dict, results_full: dict
) -> dict:
    """
    Generate repair sensitivity analysis report.

    Compares validation success and task accuracy across three repair policies:
    - off: No repair
    - syntactic: Only syntactic normalizations (fences, whitespace)
    - full: All repairs including semantic transformations

    Args:
        results_off: Results with repair_policy=off
        results_syntactic: Results with repair_policy=syntactic
        results_full: Results with repair_policy=full

    Returns:
        Dict with sensitivity metrics and tables

    Example:
        >>> report = generate_repair_sensitivity_report(
        ...     {"validation_success": 0.78, "task_accuracy": 0.94},
        ...     {"validation_success": 0.92, "task_accuracy": 0.94},
        ...     {"validation_success": 0.95, "task_accuracy": 0.93}
        ... )
        >>> report["delta_syntactic"]
        0.14
    """
    val_off = results_off.get("validation_success", 0.0)
    val_syn = results_syntactic.get("validation_success", 0.0)
    val_full = results_full.get("validation_success", 0.0)

    acc_off = results_off.get("task_accuracy")
    acc_syn = results_syntactic.get("task_accuracy")
    acc_full = results_full.get("task_accuracy")

    report = {
        "validation_success": {
            "off": val_off,
            "syntactic": val_syn,
            "full": val_full,
        },
        "delta_syntactic": val_syn - val_off,
        "delta_full": val_full - val_off,
        "delta_syn_to_full": val_full - val_syn,
    }

    if acc_off is not None:
        report["task_accuracy"] = {
            "off": acc_off,
            "syntactic": acc_syn,
            "full": acc_full,
        }
        report["accuracy_invariance"] = (
            abs(acc_off - acc_syn) <= 0.01 and abs(acc_syn - acc_full) <= 0.01
        )

    # Recommendations
    accuracy_inv = report.get("accuracy_invariance", True)

    # Prefer syntactic if it improves and maintains accuracy
    if val_syn > val_off and accuracy_inv:
        report["recommendation"] = "syntactic"
        report["rationale"] = "Syntactic repair improves validation without affecting task accuracy"
    # If full changes semantics (not accuracy_inv) and val_syn helps, use syntactic
    elif val_full > val_syn and not accuracy_inv and val_syn > val_off:
        report["recommendation"] = "syntactic"
        report["rationale"] = "Full repair changes task accuracy; syntactic repair safer"
    # If repair hurts accuracy, don't use it
    elif not accuracy_inv:
        report["recommendation"] = "off"
        report["rationale"] = "Repair changes task accuracy; use off"
    else:
        report["recommendation"] = "full"
        report["rationale"] = (
            "Full repair provides best validation success with acceptable accuracy"
        )

    return report


def analyze_repair_events(events: list[RepairEvent]) -> dict:
    """
    Analyze collection of repair events.

    Args:
        events: List of RepairEvent objects

    Returns:
        Dict with statistics and examples

    Example:
        >>> events = [
        ...     RepairEvent("strip_markdown_fences", "```json...", "{...}", [], False),
        ...     RepairEvent("strip_whitespace", "  {...}  ", "{...}", [], False),
        ... ]
        >>> stats = analyze_repair_events(events)
        >>> stats["total_repairs"]
        2
    """
    if not events:
        return {
            "total_repairs": 0,
            "by_type": {},
            "semantic_change_count": 0,
            "semantic_change_rate": 0.0,
        }

    total = len(events)
    by_type = {}
    semantic_changes = 0

    for event in events:
        by_type[event.type] = by_type.get(event.type, 0) + 1
        if event.semantic_diff:
            semantic_changes += 1

    return {
        "total_repairs": total,
        "by_type": by_type,
        "semantic_change_count": semantic_changes,
        "semantic_change_rate": semantic_changes / total if total > 0 else 0.0,
        "most_common_type": max(by_type, key=by_type.get) if by_type else None,
    }
