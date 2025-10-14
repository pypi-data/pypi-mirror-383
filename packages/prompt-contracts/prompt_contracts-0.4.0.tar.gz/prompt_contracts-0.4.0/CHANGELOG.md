# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-01-15

### Added

#### Statistical Rigor Enhancement
- **Benjamini-Hochberg FDR Correction**: Multiple comparison correction for controlling False Discovery Rate
  - `benjamini_hochberg_correction()` function with monotonicity enforcement
  - More powerful than Bonferroni correction for multiple hypotheses
  - Integrated into system comparison workflows
- **Politis-White Estimator**: Data-driven optimal block length selection for block bootstrap
  - `politis_white_block_size()` function with spectral density estimation
  - Automatic block size estimation via `auto_block=True` parameter
  - Handles dependent data from repairs and batching
- **CI Calibration Framework**: Comprehensive simulation studies for confidence interval validation
  - `calibrate_ci_coverage()` for empirical vs. nominal coverage validation
  - `compare_ci_methods()` for method comparison across Wilson, Jeffreys, Bootstrap
  - `generate_calibration_report()` for comprehensive calibration analysis
- **Pre-registration Validation**: Framework for validating evaluations against preregistered specifications
  - `PreregistrationValidator` class for hypothesis, sample size, and endpoint validation
  - `create_preregistration_template()` for creating preregistration files
  - Integrity hashing and compliance checking

#### Enhanced Block Bootstrap
- **Automatic Block Size**: `percentile_bootstrap_ci()` now supports `auto_block=True`
- **Spectral Density Estimation**: Parzen window-based spectral density calculation
- **Dependency Detection**: Automatic handling of temporal dependencies in evaluation data

#### Multiple Comparison Correction
- **FDR Control**: Benjamini-Hochberg procedure for multiple hypothesis testing
- **Monotonicity Enforcement**: Ensures adjusted p-values maintain proper ordering
- **Integration**: Seamless integration with existing McNemar and bootstrap tests

### Changed

#### Statistical Methods
- **Default CI Method**: Wilson score interval remains default for n ≥ 10
- **Block Bootstrap**: Now supports automatic optimal block size estimation
- **Multiple Comparisons**: FDR correction available for multi-task evaluations
- **Calibration**: Comprehensive validation of CI methods through simulation

#### API Enhancements
- **New Parameters**: `auto_block` parameter in `percentile_bootstrap_ci()`
- **Extended Exports**: All new statistical functions available via `promptcontracts.stats`
- **Validation Framework**: Pre-registration validation integrated into evaluation workflow

### Documentation

#### Statistical Methodology
- **FDR Correction**: Complete documentation with examples and interpretation guidelines
- **Politis-White**: Mathematical foundations and implementation details
- **CI Calibration**: Simulation study protocols and validation procedures
- **Pre-registration**: Framework documentation with compliance checking

#### Code Examples
```python
# FDR Correction
from promptcontracts.stats import benjamini_hochberg_correction
p_values = [0.001, 0.01, 0.03, 0.05, 0.1]
adjusted = benjamini_hochberg_correction(p_values, alpha=0.05)

# Automatic Block Size
from promptcontracts.stats import percentile_bootstrap_ci
ci_lower, ci_upper = percentile_bootstrap_ci(
    values, B=1000, auto_block=True, seed=42
)

# CI Calibration
from promptcontracts.stats import calibrate_ci_coverage
results = calibrate_ci_coverage('wilson', n_sims=10000, seed=42)

# Pre-registration Validation
from promptcontracts.stats import PreregistrationValidator
validator = PreregistrationValidator('preregistration.json')
report = validator.generate_validation_report(actual_data)
```

### Testing

#### New Test Suites
- **FDR Correction Tests**: `tests/test_fdr_correction.py` (7 tests)
- **Politis-White Tests**: `tests/test_politis_white.py` (8 tests)
- **Calibration Tests**: `tests/test_calibration.py` (10 tests)
- **Integration Tests**: Cross-module functionality validation

#### Test Coverage
- **Statistical Functions**: 95%+ coverage for new statistical methods
- **Edge Cases**: Comprehensive testing of boundary conditions
- **Reproducibility**: All tests use fixed seeds for deterministic results

### Reproducibility

#### Enhanced Reproducibility
- **Fixed Seeds**: All statistical functions use deterministic random seeds
- **Calibration Studies**: 10,000+ simulation runs for robust validation
- **Pre-registration**: Framework for hypothesis preregistration and validation
- **Integrity Hashing**: SHA-256 hashes for preregistration file integrity

#### Statistical Validation
- **Empirical Coverage**: Wilson intervals achieve 94.8% empirical coverage (target: 95%)
- **Method Comparison**: Comprehensive comparison across CI methods
- **Power Analysis**: Sample size calculations with effect size reporting

### Backward Compatibility

- **API Compatibility**: All v0.3.2 functionality preserved
- **Parameter Compatibility**: New parameters are optional with sensible defaults
- **Output Compatibility**: Extended JSON output maintains backward compatibility
- **CLI Compatibility**: No breaking changes to command-line interface

### Known Limitations

- **FDR Correction**: Requires sufficient sample size for reliable approximation
- **Politis-White**: Performance depends on data characteristics and sample size
- **Calibration**: Simulation studies require significant computational resources
- **Pre-registration**: Requires manual creation of preregistration files

### References

Statistical methods implemented from:
- Benjamini & Hochberg (1995). "Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing." J. R. Stat. Soc. B 57:289-300.
- Politis & White (2003). "Block bootstrap for time series." Journal of Econometrics, 117(1):1-18.
- Brown, Cai & DasGupta (2001). "Interval Estimation for a Binomial Proportion." Statistical Science.
- McNemar (1947). "Note on the sampling error of the difference between correlated proportions."

---

## [0.3.2] - 2025-01-10

### Added

#### Statistical Rigor
- **Wilson Score Intervals**: Default CI method for proportions (n >= 10)
- **Jeffreys Intervals**: Bayesian CI for small n or boundary cases (successes in {0, n})
- **Block Bootstrap**: Handle dependencies from repairs or batching (Künsch 1989)
- **McNemar Test**: Paired binary outcome comparison for system evaluations
- **Bootstrap Difference CI**: Continuous metric comparison with confidence bounds
- **Power Analysis**: Sample size calculation via required_n_for_proportion
- **Effect Size**: Cohen's h for proportion differences

#### Evaluation Infrastructure
- **Repair Analysis Module** (eval/repair_analysis.py):
  - RepairEvent dataclass with semantic_diff flag
  - estimate_semantic_change: Heuristic + optional embedding-based detection
  - generate_repair_sensitivity_report: Compare off/syntactic/full repair policies
  - analyze_repair_events: Aggregate repair statistics
- **Baseline Comparison Harness** (eval/baselines.py):
  - BaselineSystem wrapper for fair comparisons
  - compare_systems: Standardized comparison with McNemar or bootstrap tests
  - standardize_fixtures: Convert CheckList/HELM/BBH formats to PCSL
- **Benchmark Loaders** (eval/bench_loaders.py):
  - load_helm_subset: HELM benchmark integration (user-supplied paths)
  - load_bbh_subset: BIG-Bench Hard integration
  - create_ep_for_benchmark: Auto-generate PCSL EPs from benchmarks
- **Audit Harness** (eval/audit_harness.py):
  - create_audit_bundle: ZIP with SHA-256 hashes + optional GPG signature
  - create_audit_manifest: Tamper-evident audit trails
  - verify_audit_bundle: Third-party verification with checksum validation

#### Judge Protocols
- **LLM-as-Judge with Bias Control** (judge/protocols.py):
  - create_judge_prompt: Standardized prompts with criteria
  - randomize_judge_order: Prevent order bias
  - mask_provider_metadata: Remove provider-identifying hints
  - cross_family_judge_config: Multi-provider judges (OpenAI, Anthropic, Google)
  - cohens_kappa: Inter-rater agreement (binary)
  - fleiss_kappa: Multi-rater agreement (3+ raters)

#### Composition Semantics
- **Contract Composition** (core/composition.py):
  - compose_contracts_variance_bound: Upper bound under independence
  - aggregate_confidence_intervals_intersection: Conservative joint CI
  - aggregate_confidence_intervals_delta_method: Normal approximation for product
  - compose_contracts_sequential: Multi-stage validation CI aggregation
  - compose_contracts_parallel: Majority voting or any-of composition

#### Documentation
- **FAIR_COMPARISON.md**: Complete protocol for baseline comparisons
  - Fixture standardization requirements
  - Configuration equivalence verification
  - Statistical significance guidelines (McNemar, bootstrap)
  - Setup time measurement protocol
  - Reproducibility requirements (Docker, pinned deps)
- **COMPLIANCE.md v1.2.0**: Expanded with v0.3.2 features
  - Wilson/Jeffreys intervals regulatory value
  - Block bootstrap for dependent data
  - McNemar test for system comparisons
  - Cross-family judge validation protocol
  - Repair risk analysis section
  - Enhanced audit bundles with GPG signatures
  - Statistical compliance matrix

#### Tests
- **test_intervals.py**: Wilson, Jeffreys, percentile bootstrap (block mode)
- **test_significance.py**: McNemar, bootstrap difference CI
- **test_repair_analysis.py**: Semantic change detection, sensitivity reports
- **test_composition.py**: Variance bounds, CI aggregation (intersection, delta method)
- **test_power.py**: Sample size calculation, Cohen's h effect size

### Changed

#### Confidence Intervals
- **Default CI Method**: Wilson score interval (replacing percentile bootstrap as default)
- **CI Selection Logic**:
  - n >= 10: Wilson interval (default)
  - n < 10: Jeffreys interval
  - Dependent data: Block bootstrap with user-specified block size
- **Bootstrap Validation**: Bootstrap CI computed alongside exact intervals for validation

#### Metrics JSON Output
Extended run.json with:
```json
{
  "ci": {
    "wilson": {"lo": 0.770, "hi": 0.910},
    "jeffreys": {"lo": 0.765, "hi": 0.915},
    "bootstrap": {"lo": 0.772, "hi": 0.908, "B": 1000, "block": null}
  },
  "power": {
    "alpha": 0.05,
    "target": 0.8,
    "required_n": 85,
    "actual_n": 100
  },
  "repair_analysis": {
    "semantic_change_rate": 0.03,
    "events": [...]
  }
}
```

#### CLI
- **Comparison Command** (planned):
  ```bash
  prompt-contracts compare \
    --suite classification_en \
    --systems pcsl,checklist,guidance \
    --metric validation_success \
    --sig mcnemar
  ```
- **Repair Policy Flag** (planned):
  - --repair-policy off|syntactic|full
  - --log-repairs: Enable per-sample repair event logging

### Documentation

#### Statistical Methodology
All statistical methods documented with:
- Mathematical foundations and assumptions
- References to peer-reviewed literature
- Example code with expected outputs
- Interpretation guidelines (effect sizes, p-values, kappa)
- Regulatory compliance mapping

#### Benchmark Integration
HELM and BBH loaders documented with:
- Download instructions
- License information (Apache 2.0)
- Example EP creation
- Fixture count and domain metadata

#### Audit Trails
Complete audit bundle workflow:
1. Run evaluation with --save-io
2. Generate audit manifest with checksums
3. Optionally sign with GPG
4. Package as ZIP for distribution
5. Third-party verification instructions

### Reproducibility

#### Statistical Reproducibility
- Fixed random seeds throughout (default: 42)
- Bootstrap B=1000 (configurable)
- Block bootstrap for dependent data (explicit block size)
- Deterministic CI computation (Wilson, Jeffreys)

#### Dependencies
Added to requirements.txt:
- scipy>=1.10.0 (stats.norm, stats.beta, stats.chi2 for intervals and tests)

### Technical Notes

#### Wilson vs Jeffreys
**When to use**:
- n >= 10 and successes not in {0, n}: Wilson (default)
- n < 10 or boundary cases: Jeffreys
- Dependent data: Block bootstrap

**Example**:
```python
from promptcontracts.stats import wilson_interval, jeffreys_interval

# Typical case
wilson_ci = wilson_interval(85, 100)  # (0.770, 0.910)

# Small n
jeffreys_ci = jeffreys_interval(3, 5)  # (0.188, 0.950)
```

#### McNemar Test
**Use case**: Compare two systems on same fixtures (paired binary outcomes)

**Interpretation**:
- p < 0.05: Systems differ significantly
- p >= 0.05: No significant difference detected
- Requires a01 + a10 >= 10 for reliable approximation

**Example**:
```python
from promptcontracts.stats import mcnemar_test

a01 = 15  # System A failed, B passed
a10 = 5   # System A passed, B failed

p_value = mcnemar_test(a01, a10)  # 0.026 (significant)
```

#### Block Bootstrap
**Use case**: Repairs introduce dependencies between samples

**Example**:
```python
from promptcontracts.stats import percentile_bootstrap_ci

values = [1, 1, 0, 1, 1, 0, ...]  # Binary outcomes
ci = percentile_bootstrap_ci(values, B=1000, block=10, seed=42)
```

#### Cross-Family Judges
**Bias mitigation**:
1. Use judges from different providers (OpenAI, Anthropic, Google)
2. Randomize evaluation order per fixture
3. Mask provider-identifying metadata
4. Report inter-rater reliability (Cohen's κ or Fleiss' κ)

**Example**:
```python
from promptcontracts.judge import cross_family_judge_config, cohens_kappa

config = cross_family_judge_config(
    primary_model="gpt-4o",
    secondary_model="claude-3-sonnet"
)

# After evaluation
rater1 = [1, 1, 0, 1, 0]
rater2 = [1, 0, 0, 1, 0]
kappa = cohens_kappa(rater1, rater2)  # 0.615 (substantial)
```

### Peer Review Addressed

This release addresses seven specific review points:

1. **Statistical Foundations**: Wilson/Jeffreys intervals, block bootstrap
2. **Expanded Evaluation**: Hooks for HELM/BBH, multilingual fixtures (classification_en/de)
3. **Repair Policy Risk**: Semantic change detection, sensitivity analysis
4. **Fair Comparisons**: McNemar tests, standardized setup time protocol
5. **LLM-Judge Protocol**: Cross-family validation, randomization, κ reliability
6. **Composition Bounds**: Variance upper bounds, CI aggregation (intersection, delta method)
7. **Compliance Mapping**: Enhanced audit bundles, risk matrix, human oversight roles

### Backward Compatibility

- All v0.3.1 functionality preserved
- New statistical methods additive (old bootstrap CI still computed)
- CLI flags optional (no breaking changes)
- Metrics JSON extended but backward-compatible

### Known Limitations

- HELM/BBH loaders require user-supplied datasets (not bundled due to size/licensing)
- Cross-family judges require API keys for multiple providers
- Block bootstrap block size must be manually specified (no auto-detection)
- Repair semantic change detection is heuristic-based (not perfect)
- Multiple comparison correction not yet implemented (planned for v0.4.0)

### References

Statistical methods implemented from:
- Brown, Cai & DasGupta (2001). "Interval Estimation for a Binomial Proportion." Statistical Science.
- McNemar (1947). "Note on the sampling error of the difference between correlated proportions."
- Künsch (1989). "The Jackknife and the Bootstrap for General Stationary Observations."
- Landis & Koch (1977). "The Measurement of Observer Agreement for Categorical Data."
- Cohen (1988). "Statistical Power Analysis for the Behavioral Sciences."

---

## [0.3.0] - 2025-01-09

### Added

#### Core Features
- **Probabilistic Sampling**: N-sampling with configurable aggregation policies (majority, all, any, first)
- **Bootstrap Confidence Intervals**: Statistical confidence bounds for pass rates
- **Formal Capability Negotiation**: μ(Acap, Mreq) -> Mactual mapping with detailed logs
- **Enhanced Parsing**: json_loose() for fault-tolerant JSON extraction, regex_extract() utilities
- **Repair Policy Framework**: Structured repair_policy with allowed steps and max_steps
- **Metrics Module**: Comprehensive metrics including validation_success, task_accuracy, repair_rate, latency_ms, overhead_pct, provider_consistency

#### Semantic Checks
- **pc.check.contains_all**: Verify all required substrings present
- **pc.check.contains_any**: Verify at least one option present
- **pc.check.regex_present**: Pattern matching with flags support
- **pc.check.similarity**: Semantic similarity using embeddings (requires sentence-transformers)
- **pc.check.judge**: LLM-as-judge for subjective quality evaluation

#### Adapters
- **embeddings_local.py**: Local embedding adapter using sentence-transformers MiniLM
- **judge_openai.py**: OpenAI-based LLM-as-judge adapter
- Enhanced OpenAI/Ollama adapters with seed, top_p support

#### CLI Enhancements
- **--n**: Override sampling count per fixture
- **--seed**: Set random seed for reproducibility
- **--temperature**: Override generation temperature
- **--top-p**: Override top-p sampling parameter
- **--baseline**: Experimental baseline comparison mode

#### Documentation
- **COMPLIANCE.md**: Mapping to ISO/IEC/IEEE 29119, EU AI Act, NIST AI RMF
- **MIGRATION_0.2_to_0.3.md**: Comprehensive migration guide
- Dockerfile for reproducible environments
- Makefile targets: setup, eval-small, eval-full, docker-build

#### Examples
- extraction: Contact info extraction with probabilistic sampling
- summarization: Article summarization with semantic checks

#### Testing
- Unit tests for sampling.py (aggregation policies, bootstrap CI)
- Unit tests for parser.py (json_loose, regex_extract)
- Unit tests for semantic checks

### Changed

- **Runner Architecture**: Completely rewritten to integrate sampling, parsing, and repair
- **Execution Results**: Enhanced with sampling_metadata, repair_ledger, negotiation_log
- **Reporters**: Updated CLI/JSON/JUnit to display sampling info, confidence intervals, repair ledgers
- **Status Values**: Simplified to PASS/FAIL (REPAIRED deprecated, tracked in repair_ledger)
- **CheckRegistry**: Extended with new semantic and judge check types

### Deprecated

- **max_retries**: Use sampling.n instead (still works for backward compatibility)
- **REPAIRED status**: Repairs now tracked in repair_ledger, status is PASS or FAIL

### Fixed

- Improved JSON parsing resilience with json_loose()
- Better error messages in capability negotiation
- More robust repair tracking with structured ledger

### Technical Details

#### API Changes
- ContractRunner accepts optional embedding_adapter and judge_adapter
- SamplingConfig dataclass for N-sampling configuration
- ProviderCapabilities with extended fields (supports_seed, supports_temperature, supports_top_p)

#### Performance
- Parallel sample execution (when n > 1)
- Bootstrap CI computed only when bootstrap_samples > 0
- Optimized JSON schema derivation

### Compliance

This release enables compliance with:
- ISO/IEC/IEEE 29119 (Software Testing Standards)
- EU AI Act Articles 9, 10, 12, 13, 14, 15
- IEEE 730 (Software Quality Assurance)
- NIST AI Risk Management Framework

See docs/COMPLIANCE.md for detailed mapping.

## [0.3.1] - 2025-01-09

### Added

#### Dataset and Reproducibility
- **fixtures/ directory**: Comprehensive evaluation fixtures for 5 tasks (classification, extraction, RAG Q&A, summarization, tool calls)
- **DATA_CARD.md**: Complete dataset documentation with annotation protocol, inter-rater reliability (κ), and quality metrics
- **Fixture metadata**: Each task includes metadata.json with seed=42, statistics, and annotation details
- **CC BY 4.0 licensing**: All fixtures released under Creative Commons Attribution 4.0

#### Compliance and Audit
- **Risk Matrix Example**: Template for EU AI Act Article 9 compliance with PCSL mitigation strategies
- **Human Oversight Roles**: Documentation mapping Article 14 roles to PCSL modes
- **Audit Bundle Structure**: Complete audit package format with audit_manifest.json
- **SHA256 Hash Computation**: Functions and examples for tamper detection (prompt_hash, artifact_hash)
- **Compliance Statement Template**: Ready-to-use template for regulated environments
- **Detailed compliance mapping**: Extended COMPLIANCE.md to v1.1.0 with practical examples

#### Testing
- **test_repair_sensitivity.py**: Comprehensive test suite comparing validation with/without repair
- **Repair impact analysis**: Tests for false positive rate, task accuracy invariance, repair benefit ranking
- **Statistical comparison**: Fixtures and utilities for repair sensitivity analysis

#### Docker and Reproducibility
- **Pinned dependencies**: Python 3.11.7, pip 24.0, torch 2.0.1, sentence-transformers 2.2.2
- **Reproducibility environment variables**: PYTHONHASHSEED=42, PCSL_DEFAULT_SEED=42
- **Rate limiting configuration**: OPENAI_MAX_RETRIES, OPENAI_TIMEOUT, OPENAI_RETRY_DELAY
- **Health check**: Docker HEALTHCHECK for container monitoring
- **docker-eval-full target**: Run full evaluation inside Docker with seed=42

#### Makefile Enhancements
- **eval-full across 5 tasks**: Complete evaluation suite (classification, extraction, summarization, product recommendation, support ticket)
- **Per-task artifacts**: Organized output in artifacts/eval-full/<task>/
- **Fixed seed and temperature**: All evaluations use seed=42 and appropriate temperatures per task

### Changed

- **Dockerfile version**: Updated to v0.3.1 with fully pinned dependencies
- **Docker images tagged**: Both 0.3.1 and latest tags
- **Makefile release-check**: Updated version references to v0.3.1
- **COMPLIANCE.md**: Expanded from 209 to 486 lines with practical examples

### Documentation

#### Fixtures
Each task directory (classification, extraction, rag_qa, summarization, tool_calls) includes:
- README.md with task description, statistics, and schema
- LICENSE.txt (CC BY 4.0)
- metadata.json with seed, annotation metrics (Cohen's κ / Fleiss' κ), and statistics

#### Data Card Highlights
- 250 total fixtures (50 per task)
- Overall κ = 0.88 (substantial agreement per Landis & Koch, 1977)
- Annotator training protocol documented
- Quality control measures: pilot phase, consistency checks, outlier detection

#### Compliance Examples
- Medical diagnosis assistant risk assessment
- Audit bundle generation and verification scripts
- Python code for SHA256 hash computation
- Compliance statement template for regulatory submission

### Reproducibility

All evaluations now fully reproducible with:
- Fixed seed (42) across data generation, evaluation, and bootstrap
- Pinned package versions in Docker
- Deterministic environment variables (PYTHONHASHSEED)
- Rate-limit handling configuration
- Complete documentation in DATA_CARD.md

### Technical Notes

#### Test Coverage
- test_repair_sensitivity.py: 14 test functions covering:
  - JSON fence removal
  - Whitespace normalization
  - Validation success delta
  - False positive rate
  - Task accuracy invariance
  - Repair rate metrics

#### Bootstrap Parameters
- Default: B=1000 iterations
- Confidence level: δ=0.95
- Method: Percentile bootstrap (BCa available but not default)

#### Annotation Reliability
- Cohen's κ for pairwise agreement
- Fleiss' κ for 3+ annotators
- All tasks achieve κ ≥ 0.80 (substantial agreement threshold)

### Peer Review Addressed

This release addresses peer-review feedback focused on:
- Transparency: Complete dataset documentation and annotation protocol
- Reproducibility: Fixed seeds, pinned dependencies, Docker environment
- Statistical Clarity: Bootstrap parameters documented, no multiple-comparison correction (future work)
- Compliance: Practical examples with risk matrices and audit bundles

## [Unreleased]

## [0.2.3] - 2025-10-09

### Fixed
- strict_enforce semantics now properly returns NONENFORCEABLE status instead of silent fallback when schema enforcement is requested but unavailable
- Absolute artifact paths now included in JSON reporter and run.json under "artifact_paths" field
- Enum case-insensitive comparison now works consistently without mutating payload

### Changed
- CLI help text enhanced with examples and usage patterns
- Exit codes clarified and documented (0=success, 1=failure/nonenforceable, 2=validation error, 3=runtime error)
- effective_mode now logged in CLI output and included in all run.json files
- Verbose mode added with -v/--verbose flag for detailed output
- Improved error messages with better categorization (validation vs runtime errors)

### Documentation
- README updated with CLI syntax and exit code table
- TROUBLESHOOTING.md added with common issues and solutions
- All documentation synchronized with actual implementation behavior
- Examples section expanded with real output snippets

## [0.2.2] - 2025-10-08

### Added
- **BEST_PRACTICES.md**: Comprehensive production guide covering:
  - Contract design principles
  - Execution mode selection strategies
  - Writing effective prompts
  - Designing expectation suites
  - Fixture strategies
  - Auto-repair configuration
  - Tolerance tuning
  - Production deployment patterns
  - Testing & CI/CD integration
  - Monitoring & observability
  - Common pitfalls and solutions
  - 3 real-world examples (content moderation, financial transactions, sentiment analysis)
- New comprehensive examples:
  - `email_classification/`: All 4 execution modes with sentiment analysis
  - `product_recommendation/`: Personalized product recommendations
- Enhanced documentation:
  - Detailed execution modes explanation in README.md
  - Comprehensive mode comparison in QUICKSTART.md
  - Complete examples overview in examples/README.md
  - All documentation translated to English

### Changed
- Improved README.md structure with Examples section
- Enhanced QUICKSTART.md with detailed mode guides, decision trees, and production recommendations
- Updated Table of Contents to include Best Practices guide

### Documentation
- All documentation now in English for international audience
- Professional production-ready guidance
- Real-world use case examples

## [0.2.1] - 2025-10-08

### Added
- Public Python API: `run_contract()` and `validate_artifact()`
- Execution modes: `observe`, `assist`, `enforce`, `auto` with capability negotiation
- Auto-repair utilities: markdown fence stripping, JSONPath field lowercasing
- Retry logic with exponential backoff
- Comprehensive error classes: `SpecValidationError`, `AdapterError`, `ExecutionError`, `CheckFailure`
- Artifact saving with `--save-io` flag (input_final.txt, output_raw.txt, output_norm.txt, run.json)
- Status codes: `PASS`, `REPAIRED`, `FAIL`, `NONENFORCEABLE`
- Case-insensitive enum checks
- GitHub issue templates (bug report, feature request, release checklist)
- Pull request template
- Contributing guidelines (CONTRIBUTING.md)
- Code owners configuration (CODEOWNERS)
- CI/CD pipeline (GitHub Actions)
- Pre-commit hooks configuration
- EditorConfig for consistent code style
- Comprehensive utility modules (errors, normalization, retry, hashing, timestamps)

### Changed
- Version bumped to 0.2.1
- Refactored package structure with `utils/` module
- Enhanced EP schema to support `execution` configuration
- Improved adapter interface with `capabilities()` method
- Updated documentation with professional structure

### Fixed
- Module import issues with Python 3.13 editable installs

## [0.1.0] - 2025-10-08

### Added
- Initial release of prompt-contracts
- PCSL (Prompt Contract Specification Language) v0.1
- Core artifacts: Prompt Definition (PD), Expectation Suite (ES), Evaluation Profile (EP)
- JSON Schema validation for all artifacts
- Built-in checks:
  - `pc.check.json_valid` - JSON validity
  - `pc.check.json_required` - Required fields
  - `pc.check.enum` - Enum value validation
  - `pc.check.regex_absent` - Regex pattern absence
  - `pc.check.token_budget` - Token budget enforcement
  - `pc.check.latency_budget` - Latency budget enforcement
- LLM adapters:
  - OpenAI adapter (gpt-4o-mini, gpt-3.5-turbo)
  - Ollama adapter (local models)
- Reporters:
  - CLI reporter (human-readable output)
  - JSON reporter (machine-readable)
  - JUnit reporter (CI integration)
- CLI with `validate` and `run` subcommands
- Conformance levels: L1 (Structural), L2 (Semantic), L3 (Differential)
- Example contracts for support ticket classification
- Basic test suite
- README and QUICKSTART documentation

### Technical Details
- Python 3.10+ support
- YAML and JSON artifact support
- JSONPath-based field extraction
- Tolerance-based pass/fail gates

---

## Release Tags

- [Unreleased]: https://github.com/PhilipposMelikidis/prompt-contracts/compare/v0.1.0...HEAD
- [0.1.0]: https://github.com/PhilipposMelikidis/prompt-contracts/releases/tag/v0.1.0
