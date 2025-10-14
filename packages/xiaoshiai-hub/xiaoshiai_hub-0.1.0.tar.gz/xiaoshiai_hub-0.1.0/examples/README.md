# Examples

This directory contains example scripts demonstrating how to use the XiaoShi AI Hub Python SDK.

## Prerequisites

Make sure you have installed the SDK:

```bash
cd python-sdk
pip install -e .
```

## Running Examples

### 1. Download a Single File

```bash
python examples/download_single_file.py
```

Downloads a single file from a repository.

### 2. Download Entire Repository

```bash
python examples/download_repository.py
```

Downloads all files from a repository.

### 3. Download with Filters

```bash
python examples/download_with_filters.py
```

Downloads only files matching specific patterns (e.g., only YAML files).

### 4. List Repository Content

```bash
python examples/list_repository_content.py
```

Lists repository information, branches, and file tree.

## Configuration

Before running the examples, update the following variables in each script:

- `REPO_ID` or `ORGANIZATION`/`REPO_NAME`: Your repository identifier
- `REPO_TYPE`: Either "models" or "datasets"
- `USERNAME`: Your username
- `PASSWORD`: Your password

Or use environment variables:

```bash
export XIAOSHIAI_USERNAME="your-username"
export XIAOSHIAI_PASSWORD="your-password"
```

Then modify the scripts to read from environment variables:

```python
import os

USERNAME = os.getenv("XIAOSHIAI_USERNAME")
PASSWORD = os.getenv("XIAOSHIAI_PASSWORD")
```

