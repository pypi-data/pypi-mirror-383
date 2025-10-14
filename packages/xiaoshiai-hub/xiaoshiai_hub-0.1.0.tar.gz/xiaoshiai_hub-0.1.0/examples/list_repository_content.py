"""
Example: List repository contents
"""

from xiaoshiai_hub import HubClient

# Configuration
ORGANIZATION = "demo"
REPO_NAME = "demo"
REPO_TYPE = "models"  # or "datasets"
USERNAME = ""
PASSWORD = ""

# Create client
client = HubClient(
    username=USERNAME,
    password=PASSWORD,
)

# Get repository information
print(f"Repository: {ORGANIZATION}/{REPO_NAME}")
print("=" * 60)

repo_info = client.get_repository_info(
    organization=ORGANIZATION,
    repo_type=REPO_TYPE,
    repo_name=REPO_NAME,
)

print(f"Name: {repo_info.name}")
print(f"Organization: {repo_info.organization}")
print(f"Type: {repo_info.type}")
print(f"Default Branch: {repo_info.default_branch}")
if repo_info.description:
    print(f"Description: {repo_info.description}")

# List branches and tags
print("\nBranches and Tags:")
print("-" * 60)

refs = client.get_repository_refs(
    organization=ORGANIZATION,
    repo_type=REPO_TYPE,
    repo_name=REPO_NAME,
)

for ref in refs:
    default_marker = " (default)" if ref.is_default else ""
    print(f"  {ref.type:8s} {ref.name:20s} {ref.hash[:8]}{default_marker}")

# Get repository content
print("\nRepository Contents:")
print("-" * 60)

branch = repo_info.default_branch or "main"
content = client.get_repository_content(
    organization=ORGANIZATION,
    repo_type=REPO_TYPE,
    repo_name=REPO_NAME,
    branch=branch,
    path="",
)

def print_tree(content, indent=0):
    """Recursively print directory tree."""
    if content.entries:
        for entry in content.entries:
            prefix = "  " * indent
            if entry.type == "dir":
                print(f"{prefix}📁 {entry.name}/")
                # Get subdirectory content
                try:
                    sub_content = client.get_repository_content(
                        organization=ORGANIZATION,
                        repo_type=REPO_TYPE,
                        repo_name=REPO_NAME,
                        branch=branch,
                        path=entry.path,
                    )
                    print_tree(sub_content, indent + 1)
                except Exception as e:
                    print(f"{prefix}  (error: {e})")
            elif entry.type == "file":
                size_kb = entry.size / 1024 if entry.size > 0 else 0
                print(f"{prefix}📄 {entry.name} ({size_kb:.1f} KB)")
            else:
                print(f"{prefix}❓ {entry.name} ({entry.type})")

print_tree(content)

