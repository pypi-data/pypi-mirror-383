"""
XiaoShi AI Hub Python SDK

A Python library for interacting with XiaoShi AI Hub repositories.
"""

from .client import HubClient, DEFAULT_BASE_URL
from .download import (
    hf_hub_download,
    snapshot_download,
)
from .exceptions import (
    HubException,
    RepositoryNotFoundError,
    FileNotFoundError,
    AuthenticationError,
)
from .types import (
    Repository,
    Ref,
    GitContent,
    Commit,
)

__version__ = "0.2.0"

__all__ = [
    "HubClient",
    "DEFAULT_BASE_URL",
    "hf_hub_download",
    "snapshot_download",
    "HubException",
    "RepositoryNotFoundError",
    "FileNotFoundError",
    "AuthenticationError",
    "Repository",
    "Ref",
    "GitContent",
    "Commit",
]

