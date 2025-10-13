# Migrating a Service to `spaps-server-quickstart`

This playbook describes the concrete steps for services like `htma_server` and
`ingredient_server` to replace local scaffolding with the shared package. Expect a
single PR per service.

## 1. Prepare the Service

1. **Pin the dependency**
   - Add `spaps-server-quickstart = "^0.x"` to the service `pyproject.toml`.
   - `poetry update spaps-server-quickstart` (or pip equivalent) and commit the lockfile.
2. **Install tooling**
   - Ensure the editable install exists locally: `python3 -m pip install -e 'packages/python-server-quickstart[dev]'`.
   - Run the shared package tests once: `npm run test:python-server-quickstart`.

## 2. Settings & Configuration

1. Replace the local `Settings` class with a subclass of `spaps_server_quickstart.settings.BaseServiceSettings`.
   ```python
   from spaps_server_quickstart.settings import BaseServiceSettings, create_settings_loader

   class Settings(BaseServiceSettings):
       app_name: str = "HTMA Server"
       service_slug: str = "htma-server"
       database_url: str = "postgresql+asyncpg://.../htma"
       # include service-specific fields (e.g., practitioners, ingredient keys)

   get_settings = create_settings_loader(Settings)
   ```
2. Update imports wherever `Settings` or `get_settings` were used (app factory, dependencies, tasks).

## 3. FastAPI Application & Routers

1. Remove the local `create_app` factory and import the shared one:
   ```python
   from spaps_server_quickstart.app_factory import create_app
   from spaps_server_quickstart.api.router import build_base_router
   from spaps_server_quickstart.api.health import HealthRouterFactory
   ```
2. Compose routers:
   ```python
   settings_loader = get_settings
   health_router = HealthRouterFactory(
       settings_loader=settings_loader,
       session_dependency=db_resources.session_dependency,
       extra_metrics_provider=custom_metrics,
   ).create_router()

   api_router = build_base_router(
       health_router,
       (practitioner_router, {"prefix": "/v1", "tags": ["practitioner"]}),
   )

   app = create_app(
       settings_loader=settings_loader,
       api_router=api_router,
       enable_spaps_auth=True,
       auth_exempt_paths={"/open-metrics"},
   )
   ```
3. Delete redundant local modules (auth, middleware, logging) once replaced.

## 4. Database Integration

1. Instantiate shared DB resources in a new `core/db.py` or similar:
   ```python
   from spaps_server_quickstart.db import DatabaseResources

   db_resources = DatabaseResources(get_settings())
   get_db_session = db_resources.session_dependency
   ```
2. Update dependencies in API modules (`Depends(get_db_session)`).
3. Ensure Alembic scripts reuse the shared naming validators if applicable.

## 5. Celery & Tasks

1. Replace the local `Celery` bootstrap with:
   ```python
   from spaps_server_quickstart.tasks import create_celery_app

   celery_app = create_celery_app(get_settings(), task_modules=["htma_server.tasks"])
   ```
2. Update shared tasks (`build_ping_task`, `build_notification_task`) or keep service-specific overrides as needed.

## 6. Test & Validate

1. Run unit/integration tests: `poetry run pytest`, `poetry run ruff`, `poetry run mypy`.
2. Run the root `npm run prepush` to cover shared checks.
3. Smoke test FastAPI and Celery locally if the service has start scripts.

## 7. Cleanup & Review

1. Remove unused files (duplicate middleware/auth/logging) and update service README docs to reference the shared package.
2. Ensure CI passes and request review. Highlight the dependency bump and key refactors in the PR summary.

## Appendix: Checklist

- [ ] `pyproject.toml` dependency updated and installed.
- [ ] Settings subclass uses `create_settings_loader`.
- [ ] FastAPI app uses shared `create_app` and router helpers.
- [ ] Database dependencies go through `DatabaseResources`.
- [ ] Celery uses `create_celery_app` with correct task module.
- [ ] Tests + prepush suite green.
- [ ] Redundant local scaffolding removed.
