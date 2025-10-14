# KubeMind Common Library

Shared Python library for all KubeMind services.

## Overview

`kubemind-common` provides shared functionality across all KubeMind services:
- Configuration management
- Logging setup with correlation IDs
- Middleware (request ID, rate limiting, error handling)
- Contracts (Pydantic models for events, playbooks, triggers)
- HTTP client with retries
- Redis client and utilities
- Database utilities
- Security utilities (JWT, HMAC)
- Metrics instrumentation
- Kubernetes utilities

## Contributor Guide

See [Repository Guidelines](AGENTS.md) for structure, workflows, and review expectations.

## Installation

- From PyPI:

```bash
pip install kubemind-common
```

- With extras (examples):

```bash
pip install "kubemind-common[fastapi]"
pip install "kubemind-common[db]"
pip install "kubemind-common[auth]"
```

- In a monorepo (editable install):

```bash
pip install -e ../kubemind-common
```

## Development

```bash
pip install -e .[dev]
```

Running the test suite and building artefacts are managed through the bundled Makefile:

```bash
make test   # run pytest after a clean build directory
make build  # produce wheel and sdist under dist/
make check  # twine check on the build outputs
```

## Publishing

1. Export a `PYPI_TOKEN` with upload permissions (username is always `__token__`).
2. Run `make publish` which will rebuild, validate and upload using Twine.
3. Tag the release (`git tag vX.Y.Z && git push --tags`) so downstream services can pin versions.

## Usage

### Configuration

```python
from kubemind_common.config.base import BaseServiceSettings

settings = BaseServiceSettings()
```

### Logging

```python
from kubemind_common.logging.setup import setup_logging

setup_logging(level="INFO", format="json")
```

### HTTP Client

```python
from kubemind_common.http.client import create_http_client, http_request

async with create_http_client() as client:
    response = await http_request(client, "GET", "https://api.example.com")
```

### Kubernetes

```python
from kubemind_common.k8s.client import create_k8s_client

k8s = create_k8s_client(in_cluster=False)
pods = k8s.core_v1_api.list_pod_for_all_namespaces()
```

### Contracts

```python
from kubemind_common.contracts.events import Event
from kubemind_common.contracts.playbooks import PlaybookSpec

event = Event(
    id="evt-123",
    source="kubernetes",
    type="pod_crash",
    timestamp="2025-10-12T17:00:00Z"
)
```

## Project Structure

- `src/kubemind_common/` — library code
  - `config/`, `logging/`, `middleware/`, `contracts/`, `http/`, `redis/`, `db/`, `security/`, `metrics/`, `k8s/`, `utils/`, etc.
- `tests/` — unit and integration tests
- `docs/` — documentation (see `docs/index.md`)
- `examples/` — runnable usage examples
- `.github/workflows/` — CI/CD and publishing

## Development

```bash
# Create a virtual environment and install in editable mode
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Type checking (if configured)
mypy src/kubemind_common/

# Linting (if configured)
ruff check .
```

## Build & Publish

This project uses modern PEP 621 metadata with Hatchling.

- Local build:

```bash
python -m pip install --upgrade build
python -m build
```

- Trusted Publishing via GitHub Actions:
  - Configure the PyPI project to trust this repository (PyPI → Management → Publishing → Trusted Publishers).
  - Tag a release `vX.Y.Z` to publish to PyPI.
  - Tag a pre-release like `vX.Y.Z-rc1` to publish to TestPyPI.
  - Or run the `Publish` workflow manually and choose `pypi` or `testpypi`.

## Versioning

This library follows semantic versioning. Services should pin compatible versions:

```toml
kubemind-common = "^0.2.0"
```

## Documentation

See `docs/index.md` for module documentation and examples.
