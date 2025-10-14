"""
Example: Download with progress bars (like Hugging Face Hub)
"""

from xiaoshiai_hub import hf_hub_download, snapshot_download

# Configuration
REPO_ID = "demo/demo"
REPO_TYPE = "models"  # or "datasets"
USERNAME = ""
PASSWORD = ""

print("=" * 80)
print("Example 1: Download single file with progress bar")
print("=" * 80)
print()

# Download a single file with progress bar
file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename="Dockerfile",
    repo_type=REPO_TYPE,
    username=USERNAME,
    password=PASSWORD,
    show_progress=True,  # Show progress bar (default)
)

print(f"\n✓ File downloaded to: {file_path}")
print()

print("=" * 80)
print("Example 2: Download repository with overall progress")
print("=" * 80)
print()

# Download entire repository with overall progress bar
repo_path = snapshot_download(
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,
    username=USERNAME,
    password=PASSWORD,
    show_progress=True,  # Show overall progress bar
    verbose=True,
)

print(f"\n✓ Repository downloaded to: {repo_path}")
print()

print("=" * 80)
print("Example 3: Download with filters and progress")
print("=" * 80)
print()

# Download only YAML files with progress
repo_path = snapshot_download(
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,
    allow_patterns=["*.yml", "*.yaml"],
    ignore_patterns=[".git*"],
    username=USERNAME,
    password=PASSWORD,
    show_progress=True,
    verbose=True,
)

print(f"\n✓ Filtered repository downloaded to: {repo_path}")

