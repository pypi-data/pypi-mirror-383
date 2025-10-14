"""
Example: Download repository with pattern filters
"""

from xiaoshiai_hub import snapshot_download

# Configuration
REPO_ID = "demo/demo"
REPO_TYPE = "models"  # or "datasets"
USERNAME = ""
PASSWORD = ""

# Download only YAML files, ignoring .git files
print(f"Downloading repository: {REPO_ID}")
print("Filters:")
print("  - Allow: *.yml, *.yaml")
print("  - Ignore: .git*")
print()

repo_path = snapshot_download(
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,
    allow_patterns=["*.yml", "*.yaml"],
    ignore_patterns=[".git*"],
    username=USERNAME,
    password=PASSWORD,
    verbose=True,
)

print(f"\n✓ Repository downloaded to: {repo_path}")

