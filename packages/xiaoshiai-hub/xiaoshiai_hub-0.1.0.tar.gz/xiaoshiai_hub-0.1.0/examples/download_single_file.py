"""
Example: Download a single file from a repository
"""

from xiaoshiai_hub import hf_hub_download

# Configuration
REPO_ID = "demo/demo"
FILENAME = "config.yaml"
REPO_TYPE = "models"  # or "datasets"
USERNAME = ""
PASSWORD = ""

# Download a single file
print(f"Downloading {FILENAME} from {REPO_ID}...")

file_path = hf_hub_download(
    repo_id=REPO_ID,
    filename=FILENAME,
    repo_type=REPO_TYPE,
    username=USERNAME,
    password=PASSWORD,
)

print(f"✓ File downloaded to: {file_path}")

