"""
Example: Download entire repository
"""

from xiaoshiai_hub import snapshot_download

# Configuration
REPO_ID = "demo/demo"
REPO_TYPE = "models"  # or "datasets"
USERNAME = ""
PASSWORD = ""

# Download entire repository
print(f"Downloading repository: {REPO_ID}")

repo_path = snapshot_download(
    repo_id=REPO_ID,
    repo_type=REPO_TYPE,
    username=USERNAME,
    password=PASSWORD,
    verbose=True,
)

print(f"\n✓ Repository downloaded to: {repo_path}")

