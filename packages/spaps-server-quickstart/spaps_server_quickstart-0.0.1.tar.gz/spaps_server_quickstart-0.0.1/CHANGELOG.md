# Changelog

All notable changes to this project will be documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Added FastAPI lifespan handling for SPAPS auth cleanup.
- Introduced migration guide and upgrading instructions for downstream services.
- Established comprehensive unit tests across settings, middleware, DB, Celery, and auth helpers.

## [0.0.1] - 2025-10-14

- Initial scaffold of `spaps-server-quickstart` with shared FastAPI/Celery/DB utilities.
