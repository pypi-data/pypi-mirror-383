#!/usr/bin/env python3
"""List and verify built distribution artifacts."""

import hashlib
from pathlib import Path


def list_artifacts():
    """List all built artifacts with details."""
    print("Built Artifacts Summary")
    print("=" * 50)

    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Error: dist/ directory not found")
        return False

    artifacts = list(dist_dir.glob("*"))
    if not artifacts:
        print("Error: No artifacts found in dist/")
        return False

    total_size = 0

    for artifact in sorted(artifacts):
        if artifact.is_file():
            size = artifact.stat().st_size
            total_size += size

            # Calculate SHA256 for verification
            sha256_hash = hashlib.sha256()
            with artifact.open("rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            size_str = format_size(size)
            print(f"   {artifact.name}")
            print(f"   Size: {size_str}")
            print(f"   SHA256: {sha256_hash.hexdigest()}")
            print()

    print(f"Total: {len(artifacts)} artifacts, {format_size(total_size)}")
    print("All artifacts listed successfully")
    return True


def format_size(size_bytes: int) -> str:
    """Format size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024**3:
        return f"{size_bytes / 1024**2:.1f} MB"
    return f"{size_bytes / 1024**3:.1f} GB"


if __name__ == "__main__":
    import sys

    success = list_artifacts()
    if not success:
        sys.exit(1)
