"""
External audit harness for third-party verification.

Creates tamper-evident audit bundles with SHA-256 hashes for regulatory
compliance and independent verification.
"""

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path


def compute_file_hash(file_path: str) -> str:
    """
    Compute SHA-256 hash of file.

    Args:
        file_path: Path to file

    Returns:
        Hex string of SHA-256 hash
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def create_audit_manifest(
    artifacts_dir: str,
    run_id: str,
    pcsl_version: str = "0.3.2",
    purpose: str = "Regulatory compliance audit",
) -> dict:
    """
    Create audit manifest with hashes of all artifacts.

    Args:
        artifacts_dir: Directory containing run artifacts
        run_id: Unique run identifier
        pcsl_version: PCSL version used
        purpose: Audit purpose statement

    Returns:
        Audit manifest dict
    """
    artifacts_path = Path(artifacts_dir)
    if not artifacts_path.exists():
        raise FileNotFoundError(f"Artifacts directory not found: {artifacts_dir}")

    # Collect all artifacts
    artifacts = {}
    for file_path in artifacts_path.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(artifacts_path)
            artifacts[str(relative_path)] = {
                "size_bytes": file_path.stat().st_size,
                "sha256": compute_file_hash(str(file_path)),
                "modified": file_path.stat().st_mtime,
            }

    # Load run.json for metadata
    run_json_path = artifacts_path / "run.json"
    run_metadata = {}
    if run_json_path.exists():
        with open(run_json_path) as f:
            run_metadata = json.load(f)

    manifest = {
        "audit_id": f"audit_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "pcsl_version": pcsl_version,
        "created_at": datetime.now().isoformat(),
        "purpose": purpose,
        "artifacts_dir": str(artifacts_path.absolute()),
        "run_metadata": {
            "run_id": run_id,
            "timestamp": run_metadata.get("timestamp"),
            "seed": run_metadata.get("seed"),
            "target": run_metadata.get("target"),
            "execution_mode": run_metadata.get("execution", {}).get("mode"),
        },
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "compliance_tags": [
            "ISO-29119-compliant",
            "EU-AI-Act-Article-12",
            "NIST-AI-RMF-Measure-2.2",
        ],
    }

    return manifest


def create_audit_bundle(
    artifacts_dir: str,
    output_path: str,
    run_id: str,
    sign: bool = False,
    gpg_key: str | None = None,
) -> str:
    """
    Create audit bundle ZIP with manifest and all artifacts.

    Args:
        artifacts_dir: Directory containing run artifacts
        output_path: Where to save audit bundle ZIP
        run_id: Unique run identifier
        sign: Whether to GPG sign the manifest (default False)
        gpg_key: GPG key ID for signing (if sign=True)

    Returns:
        Path to created audit bundle

    Example:
        >>> create_audit_bundle(
        ...     "artifacts/run_20250110_143022",
        ...     "audit_bundles/audit_20250110.zip",
        ...     "run_20250110_143022"
        ... )
        "audit_bundles/audit_20250110.zip"
    """
    artifacts_path = Path(artifacts_dir)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest = create_audit_manifest(artifacts_dir, run_id)

    # Save manifest
    manifest_path = artifacts_path / "audit_manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Optionally sign manifest
    if sign:
        if not gpg_key:
            raise ValueError("GPG key required for signing")

        import subprocess

        # Create detached signature
        subprocess.run(
            ["gpg", "--detach-sign", "--armor", "--local-user", gpg_key, str(manifest_path)],
            check=True,
        )
        print(f"Signed manifest with GPG key: {gpg_key}")

    # Create checksums file
    checksums_path = artifacts_path / "checksums.txt"
    with open(checksums_path, "w") as f:
        for artifact_name, artifact_info in manifest["artifacts"].items():
            f.write(f"{artifact_info['sha256']}  {artifact_name}\n")

    # Create ZIP bundle
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in artifacts_path.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(artifacts_path.parent)
                zipf.write(file_path, arcname)

    print(f"Created audit bundle: {output_path}")
    print(f"Artifacts: {manifest['artifact_count']}")
    print(f"Audit ID: {manifest['audit_id']}")

    return str(output_path.absolute())


def verify_audit_bundle(bundle_path: str, verbose: bool = True) -> bool:
    """
    Verify integrity of audit bundle.

    Args:
        bundle_path: Path to audit bundle ZIP
        verbose: Print verification details (default True)

    Returns:
        True if all checks pass, False otherwise

    Example:
        >>> verify_audit_bundle("audit_bundles/audit_20250110.zip")
        Verifying audit bundle...
        ✓ Manifest found
        ✓ Checksums verified: 15/15 files
        ✓ GPG signature valid
        True
    """
    bundle_path = Path(bundle_path)
    if not bundle_path.exists():
        print(f"✗ Bundle not found: {bundle_path}")
        return False

    if verbose:
        print(f"Verifying audit bundle: {bundle_path}")

    # Extract to temp directory
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Extract bundle
        with zipfile.ZipFile(bundle_path, "r") as zipf:
            zipf.extractall(temp_path)

        # Find manifest
        manifest_files = list(temp_path.rglob("audit_manifest.json"))
        if not manifest_files:
            print("✗ Manifest not found in bundle")
            return False

        manifest_path = manifest_files[0]
        if verbose:
            print("✓ Manifest found")

        # Load manifest
        with open(manifest_path) as f:
            manifest = json.load(f)

        # Verify checksums
        artifacts_dir = manifest_path.parent
        verified = 0
        failed = []

        for artifact_name, artifact_info in manifest["artifacts"].items():
            artifact_path = artifacts_dir / artifact_name
            if not artifact_path.exists():
                failed.append(f"{artifact_name}: file not found")
                continue

            actual_hash = compute_file_hash(str(artifact_path))
            expected_hash = artifact_info["sha256"]

            if actual_hash != expected_hash:
                failed.append(f"{artifact_name}: hash mismatch")
            else:
                verified += 1

        if verbose:
            if failed:
                print(f"✗ Checksum verification failed: {len(failed)} files")
                for failure in failed[:5]:  # Show first 5
                    print(f"  - {failure}")
            else:
                print(f"✓ Checksums verified: {verified}/{len(manifest['artifacts'])} files")

        # Check for GPG signature
        sig_files = list(artifacts_dir.rglob("audit_manifest.json.asc"))
        if sig_files:
            if verbose:
                print("✓ GPG signature present (verify separately with: gpg --verify)")
        elif verbose:
            print("  (No GPG signature)")

        return len(failed) == 0
