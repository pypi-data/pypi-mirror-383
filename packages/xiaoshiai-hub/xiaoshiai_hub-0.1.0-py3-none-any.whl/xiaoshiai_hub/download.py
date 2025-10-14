"""
Download utilities for XiaoShi AI Hub SDK
"""

import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Union

try:
    from tqdm.auto import tqdm
except ImportError:
    tqdm = None

from .client import HubClient, DEFAULT_BASE_URL
from .types import GitContent


def _match_pattern(name: str, pattern: str) -> bool:
    """
    Match a filename against a pattern.
    
    Supports wildcards:
    - * matches any characters
    - *.ext matches files with extension
    - prefix* matches files starting with prefix
    
    Args:
        name: Filename to match
        pattern: Pattern to match against
        
    Returns:
        True if the name matches the pattern
    """
    return fnmatch.fnmatch(name, pattern)


def _should_download_file(
    file_path: str,
    allow_patterns: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
) -> bool:
    """
    Determine if a file should be downloaded based on patterns.
    
    Args:
        file_path: Path of the file
        allow_patterns: List of patterns to allow (if None, allow all)
        ignore_patterns: List of patterns to ignore
        
    Returns:
        True if the file should be downloaded
    """
    filename = os.path.basename(file_path)
    
    # Check ignore patterns first
    if ignore_patterns:
        for pattern in ignore_patterns:
            if _match_pattern(filename, pattern) or _match_pattern(file_path, pattern):
                return False
    
    # If no allow patterns, allow all (except ignored)
    if not allow_patterns:
        return True
    
    # Check allow patterns
    for pattern in allow_patterns:
        if _match_pattern(filename, pattern) or _match_pattern(file_path, pattern):
            return True
    
    return False


def _count_files_to_download(
    client: HubClient,
    organization: str,
    repo_type: str,
    repo_name: str,
    branch: str,
    path: str,
    allow_patterns: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
) -> int:
    """
    Count total number of files to download.

    Args:
        client: Hub client instance
        organization: Organization name
        repo_type: Repository type
        repo_name: Repository name
        branch: Branch name
        path: Current path in the repository
        allow_patterns: Patterns to allow
        ignore_patterns: Patterns to ignore

    Returns:
        Total number of files to download
    """
    content = client.get_repository_content(
        organization=organization,
        repo_type=repo_type,
        repo_name=repo_name,
        branch=branch,
        path=path,
    )

    count = 0
    if content.entries:
        for entry in content.entries:
            if entry.type == "file":
                if _should_download_file(entry.path, allow_patterns, ignore_patterns):
                    count += 1
            elif entry.type == "dir":
                count += _count_files_to_download(
                    client=client,
                    organization=organization,
                    repo_type=repo_type,
                    repo_name=repo_name,
                    branch=branch,
                    path=entry.path,
                    allow_patterns=allow_patterns,
                    ignore_patterns=ignore_patterns,
                )

    return count


def _download_repository_recursively(
    client: HubClient,
    organization: str,
    repo_type: str,
    repo_name: str,
    branch: str,
    path: str,
    local_dir: str,
    allow_patterns: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    verbose: bool = True,
    progress_bar = None,
) -> None:
    """
    Recursively download repository contents.

    Args:
        client: Hub client instance
        organization: Organization name
        repo_type: Repository type
        repo_name: Repository name
        branch: Branch name
        path: Current path in the repository
        local_dir: Local directory to save files
        allow_patterns: Patterns to allow
        ignore_patterns: Patterns to ignore
        verbose: Print progress messages
        progress_bar: Optional tqdm progress bar for overall progress
    """
    # Get content at current path
    content = client.get_repository_content(
        organization=organization,
        repo_type=repo_type,
        repo_name=repo_name,
        branch=branch,
        path=path,
    )

    # Process entries
    if content.entries:
        for entry in content.entries:
            if entry.type == "file":
                # Check if file should be downloaded
                if _should_download_file(entry.path, allow_patterns, ignore_patterns):
                    if verbose and progress_bar is None:
                        print(f"Downloading file: {entry.path}")

                    local_path = os.path.join(local_dir, entry.path)

                    # Update progress bar description if available
                    if progress_bar is not None:
                        progress_bar.set_description(f"Downloading {entry.path}")

                    client.download_file(
                        organization=organization,
                        repo_type=repo_type,
                        repo_name=repo_name,
                        branch=branch,
                        file_path=entry.path,
                        local_path=local_path,
                        show_progress=progress_bar is None,  # Show individual progress only if no overall progress
                    )

                    # Update overall progress
                    if progress_bar is not None:
                        progress_bar.update(1)
                else:
                    if verbose and progress_bar is None:
                        print(f"Skipping file: {entry.path}")

            elif entry.type == "dir":
                if verbose and progress_bar is None:
                    print(f"Entering directory: {entry.path}")

                # Recursively download directory contents
                _download_repository_recursively(
                    client=client,
                    organization=organization,
                    repo_type=repo_type,
                    repo_name=repo_name,
                    branch=branch,
                    path=entry.path,
                    local_dir=local_dir,
                    allow_patterns=allow_patterns,
                    ignore_patterns=ignore_patterns,
                    verbose=verbose,
                    progress_bar=progress_bar,
                )

            else:
                if verbose and progress_bar is None:
                    print(f"Skipping {entry.type}: {entry.path}")


def hf_hub_download(
    repo_id: str,
    filename: str,
    *,
    repo_type: str = "models",
    revision: Optional[str] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    local_dir: Optional[Union[str, Path]] = None,
    base_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    show_progress: bool = True,
) -> str:
    """
    Download a single file from a repository.

    Similar to huggingface_hub.hf_hub_download().

    Args:
        repo_id: Repository ID in the format "organization/repo_name"
        filename: Path to the file in the repository
        repo_type: Type of repository ("models" or "datasets")
        revision: Branch/tag/commit to download from (default: main branch)
        cache_dir: Directory to cache downloaded files
        local_dir: Directory to save the file (if not using cache)
        base_url: Base URL of the Hub API (default: from MOHA_ENDPOINT env var)
        username: Username for authentication
        password: Password for authentication
        token: Token for authentication
        show_progress: Whether to show download progress bar

    Returns:
        Path to the downloaded file

    Example:
        >>> file_path = hf_hub_download(
        ...     repo_id="demo/demo",
        ...     filename="config.yaml",
        ...     username="your-username",
        ...     password="your-password",
        ... )
    """
    # Parse repo_id
    parts = repo_id.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid repo_id format: {repo_id}. Expected 'organization/repo_name'")

    organization, repo_name = parts

    # Create client
    client = HubClient(
        base_url=base_url,
        username=username,
        password=password,
        token=token,
    )

    # Get repository info to determine branch
    if revision is None:
        repo_info = client.get_repository_info(organization, repo_type, repo_name)
        revision = repo_info.default_branch or "main"

    # Determine local path
    if local_dir:
        local_path = os.path.join(local_dir, filename)
    elif cache_dir:
        # Create cache structure similar to huggingface_hub
        cache_path = os.path.join(
            cache_dir,
            f"{repo_type}--{organization}--{repo_name}",
            "snapshots",
            revision,
            filename,
        )
        local_path = cache_path
    else:
        # Default to current directory
        local_path = filename

    # Download file
    client.download_file(
        organization=organization,
        repo_type=repo_type,
        repo_name=repo_name,
        branch=revision,
        file_path=filename,
        local_path=local_path,
        show_progress=show_progress,
    )

    return local_path


def snapshot_download(
    repo_id: str,
    *,
    repo_type: str = "models",
    revision: Optional[str] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    local_dir: Optional[Union[str, Path]] = None,
    allow_patterns: Optional[Union[List[str], str]] = None,
    ignore_patterns: Optional[Union[List[str], str]] = None,
    base_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None,
    verbose: bool = True,
    show_progress: bool = True,
) -> str:
    """
    Download an entire repository snapshot.

    Similar to huggingface_hub.snapshot_download().

    Args:
        repo_id: Repository ID in the format "organization/repo_name"
        repo_type: Type of repository ("models" or "datasets")
        revision: Branch/tag/commit to download from (default: main branch)
        cache_dir: Directory to cache downloaded files
        local_dir: Directory to save files (if not using cache)
        allow_patterns: Pattern or list of patterns to allow (e.g., "*.yaml", "*.yml")
        ignore_patterns: Pattern or list of patterns to ignore (e.g., ".git*")
        base_url: Base URL of the Hub API (default: from MOHA_ENDPOINT env var)
        username: Username for authentication
        password: Password for authentication
        token: Token for authentication
        verbose: Print progress messages
        show_progress: Whether to show overall progress bar

    Returns:
        Path to the downloaded repository

    Example:
        >>> repo_path = snapshot_download(
        ...     repo_id="demo/demo",
        ...     repo_type="models",
        ...     allow_patterns=["*.yaml", "*.yml"],
        ...     ignore_patterns=[".git*"],
        ...     username="your-username",
        ...     password="your-password",
        ... )
    """
    # Parse repo_id
    parts = repo_id.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid repo_id format: {repo_id}. Expected 'organization/repo_name'")

    organization, repo_name = parts

    # Normalize patterns to lists
    if isinstance(allow_patterns, str):
        allow_patterns = [allow_patterns]
    if isinstance(ignore_patterns, str):
        ignore_patterns = [ignore_patterns]

    # Create client
    client = HubClient(
        base_url=base_url,
        username=username,
        password=password,
        token=token,
    )

    # Get repository info
    repo_info = client.get_repository_info(organization, repo_type, repo_name)

    # Determine revision
    if revision is None:
        revision = repo_info.default_branch or "main"

    # Determine local directory
    if local_dir:
        download_dir = str(local_dir)
    elif cache_dir:
        # Create cache structure
        download_dir = os.path.join(
            cache_dir,
            f"{repo_type}--{organization}--{repo_name}",
            "snapshots",
            revision,
        )
    else:
        # Default to downloads directory
        download_dir = f"./downloads/{organization}_{repo_type}_{repo_name}"

    if verbose and not show_progress:
        print(f"Downloading repository: {repo_id}")
        print(f"Repository type: {repo_type}")
        print(f"Revision: {revision}")
        print(f"Destination: {download_dir}")

    # Create progress bar if requested
    progress_bar = None
    if show_progress and tqdm is not None:
        # Count total files to download
        if verbose:
            print(f"Fetching repository info...")

        total_files = _count_files_to_download(
            client=client,
            organization=organization,
            repo_type=repo_type,
            repo_name=repo_name,
            branch=revision,
            path="",
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
        )

        if total_files > 0:
            progress_bar = tqdm(
                total=total_files,
                unit='file',
                desc=f"Downloading {repo_id}",
                leave=True,
            )

    # Download recursively
    try:
        _download_repository_recursively(
            client=client,
            organization=organization,
            repo_type=repo_type,
            repo_name=repo_name,
            branch=revision,
            path="",
            local_dir=download_dir,
            allow_patterns=allow_patterns,
            ignore_patterns=ignore_patterns,
            verbose=verbose,
            progress_bar=progress_bar,
        )
    finally:
        if progress_bar is not None:
            progress_bar.close()

    if verbose and not show_progress:
        print(f"Download completed to: {download_dir}")

    return download_dir

