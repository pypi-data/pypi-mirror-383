# SPAPS Server Quickstart

Reusable scaffolding for Sweet Potato service backends. This package gathers the FastAPI
application factory, Celery bootstrap, Pydantic settings base classes, and other utilities
that HTMA, Ingredient, and future services can share.

## Installation

Use either Poetry (preferred inside this repo) or pip editable installs:

```bash
# with poetry
poetry install -C packages/python-server-quickstart

# or with pip (installs package + dev extras)
python3 -m pip install -e 'packages/python-server-quickstart[dev]'
```

The editable install ensures FastAPI, SQLAlchemy, Celery, and other dependencies are
available when the pre-push scripts execute.

## Local Development

```bash
poetry run -C packages/python-server-quickstart pytest
```

The shared modules are designed to be imported by individual service packages. Tests live
alongside the shared code to guard the common behaviour.

## Lifecycle Hooks

`create_app` now uses FastAPI's lifespan context to close shared resources (e.g., SPAPS auth
clients). When you need additional startup/shutdown logic, extend the lifespan in your service
by wrapping the provided app with your own context manager or closing resources within your
domain packages. Running tests with `TestClient(app)` will automatically exercise the shutdown
path and catch missing `aclose()` implementations.

## Upgrading Downstream Services

Guidance for publishing new versions and upgrading consumer services lives in
[`docs/UPGRADING.md`](docs/UPGRADING.md). Review those steps before bumping the package or
pulling a newer release into `htma_server`, `ingredient_server`, or other SPAPS services.

## Migrating an Existing Service

See [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md) for a step-by-step walkthrough of
adopting the shared package inside an existing FastAPI/Celery service. It covers settings
integration, router wiring, database session management, Celery bootstraps, and the final
cleanup checklist.

## Release Workflow

- Use the GitHub Action **Publish Python Server Quickstart** (`.github/workflows/python-server-quickstart-release.yml`) to cut releases. It reuses the generic `python-package-release` workflow alongside `scripts/manage_python_package_version.py`.
- Ensure the repository secret `PYPI_SERVER_QUICKSTART_TOKEN` holds the PyPI API token for this package.
- For manual bumps, dispatch the workflow and choose the bump type (major/minor/patch). For automated publishes, pushing a commit that updates `packages/python-server-quickstart/pyproject.toml` will trigger the workflow.

## Status

- [x] Initial package scaffold
- [x] Shared application factories
- [x] Shared Celery bootstrap
- [x] Shared middleware, logging, and settings base classes
- [x] Health endpoint helpers
- [ ] Documentation and usage examples

## Repository Integration

The root `package.json` includes `lint:python-server-quickstart`, `typecheck:python-server-quickstart`,
and `test:python-server-quickstart` commands. These run automatically via `npm run prepush`, so make sure
the editable install step above has been executed before pushing commits.
