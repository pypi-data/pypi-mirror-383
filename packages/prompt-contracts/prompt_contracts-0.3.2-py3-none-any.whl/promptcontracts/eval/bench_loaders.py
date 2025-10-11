"""
Cross-dataset benchmark loaders for HELM, BBH, and other public benchmarks.

Provides hooks for loading user-supplied benchmark datasets and normalizing
them into PCSL format. Full datasets not included; users must provide paths.
"""

import json
from pathlib import Path
from typing import Optional


def load_helm_subset(
    task_name: str,
    data_path: str,
    max_fixtures: Optional[int] = 100,
    seed: int = 42,
) -> list[dict]:
    """
    Load HELM benchmark subset.

    HELM (Holistic Evaluation of Language Models) provides diverse tasks.
    Users must download HELM data separately.

    Args:
        task_name: HELM task name (e.g., "mmlu", "boolq", "hellaswag")
        data_path: Path to HELM data directory
        max_fixtures: Maximum fixtures to load (default 100)
        seed: Random seed for sampling (default 42)

    Returns:
        List of PCSL-format fixtures with gold labels

    Example:
        >>> # After downloading HELM data
        >>> fixtures = load_helm_subset(
        ...     "mmlu",
        ...     "/path/to/helm_data",
        ...     max_fixtures=50
        ... )

    Notes:
        Download HELM: https://github.com/stanford-crfm/helm
        License: Apache 2.0 (check individual tasks)

    Raises:
        FileNotFoundError: If data_path doesn't exist
        ValueError: If task_name not found
    """
    import random

    data_dir = Path(data_path)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"HELM data directory not found: {data_path}\n"
            "Download from: https://github.com/stanford-crfm/helm"
        )

    task_file = data_dir / f"{task_name}.jsonl"
    if not task_file.exists():
        raise ValueError(
            f"Task {task_name} not found in {data_path}\n"
            f"Available tasks: {list(data_dir.glob('*.jsonl'))}"
        )

    # Load JSONL
    fixtures = []
    with open(task_file) as f:
        for line in f:
            item = json.loads(line)
            fixtures.append(
                {
                    "id": item.get("id", f"helm_{task_name}_{len(fixtures)}"),
                    "input": item.get("input", ""),
                    "gold": item.get("references", [None])[0],
                    "metadata": {"source": "helm", "task": task_name},
                }
            )

    # Sample if needed
    if max_fixtures and len(fixtures) > max_fixtures:
        random.seed(seed)
        fixtures = random.sample(fixtures, max_fixtures)

    return fixtures


def load_bbh_subset(
    task_name: str,
    data_path: str,
    max_fixtures: Optional[int] = 100,
    seed: int = 42,
) -> list[dict]:
    """
    Load BIG-Bench Hard (BBH) subset.

    BBH provides challenging tasks for language models.
    Users must download BBH data separately.

    Args:
        task_name: BBH task name (e.g., "boolean_expressions", "causal_judgement")
        data_path: Path to BBH data directory
        max_fixtures: Maximum fixtures to load (default 100)
        seed: Random seed for sampling (default 42)

    Returns:
        List of PCSL-format fixtures with gold labels

    Example:
        >>> # After downloading BBH data
        >>> fixtures = load_bbh_subset(
        ...     "boolean_expressions",
        ...     "/path/to/bbh_data",
        ...     max_fixtures=50
        ... )

    Notes:
        Download BBH: https://github.com/suzgunmirac/BIG-Bench-Hard
        License: Apache 2.0

    Raises:
        FileNotFoundError: If data_path doesn't exist
        ValueError: If task_name not found
    """
    import random

    data_dir = Path(data_path)
    if not data_dir.exists():
        raise FileNotFoundError(
            f"BBH data directory not found: {data_path}\n"
            "Download from: https://github.com/suzgunmirac/BIG-Bench-Hard"
        )

    task_file = data_dir / f"{task_name}.json"
    if not task_file.exists():
        raise ValueError(
            f"Task {task_name} not found in {data_path}\n"
            f"Available tasks: {list(data_dir.glob('*.json'))}"
        )

    # Load JSON
    with open(task_file) as f:
        data = json.load(f)

    fixtures = []
    examples = data.get("examples", [])
    for i, item in enumerate(examples):
        fixtures.append(
            {
                "id": f"bbh_{task_name}_{i}",
                "input": item.get("input", ""),
                "gold": item.get("target", ""),
                "metadata": {"source": "bbh", "task": task_name},
            }
        )

    # Sample if needed
    if max_fixtures and len(fixtures) > max_fixtures:
        random.seed(seed)
        fixtures = random.sample(fixtures, max_fixtures)

    return fixtures


def create_ep_for_benchmark(
    benchmark_name: str, task_name: str, fixtures: list[dict], output_path: str
) -> None:
    """
    Create PCSL Evaluation Profile for benchmark fixtures.

    Args:
        benchmark_name: Benchmark name (helm, bbh)
        task_name: Task name
        fixtures: Loaded fixtures
        output_path: Where to save EP JSON

    Example:
        >>> fixtures = load_helm_subset("mmlu", "/path/to/helm")
        >>> create_ep_for_benchmark("helm", "mmlu", fixtures, "ep_helm_mmlu.json")
    """
    ep = {
        "pcsl": "0.3.2",
        "id": f"{benchmark_name}.{task_name}",
        "version": "1.0.0",
        "description": f"{benchmark_name.upper()} {task_name} evaluation",
        "targets": [
            {
                "type": "openai",
                "model": "gpt-4o-mini",
                "params": {"temperature": 0.0, "seed": 42},
            }
        ],
        "execution": {"mode": "assist", "strict_enforce": False},
        "sampling": {"n": 1, "seed": 42},
        "fixtures": fixtures[:10],  # Sample for EP
        "metadata": {
            "source": benchmark_name,
            "task": task_name,
            "total_fixtures": len(fixtures),
            "note": "Full fixture set loaded separately",
        },
    }

    with open(output_path, "w") as f:
        json.dump(ep, f, indent=2)

    print(f"Created EP: {output_path}")
    print(f"Fixtures: {len(fixtures)} total, {len(ep['fixtures'])} in EP sample")
