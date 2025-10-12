# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-11

### Added
- Initial production release
- Seamless Databricks OAuth integration with Claude CLI
- Automatic token refresh and management
- Cross-platform support (macOS, Linux, Windows)
- Comprehensive test suite with 95%+ coverage
- Production-ready error handling and logging
- CLI commands: `login`, `logout`, `status`
- Docker container support
- CI/CD pipeline with GitHub Actions
- Type hints and mypy compliance
- Security scanning with bandit and safety
- Pre-commit hooks for code quality
- Comprehensive documentation

### Security
- Secure token storage with restricted file permissions
- Automatic token refresh to minimize exposure
- Security scanning in CI/CD pipeline
- No secrets logged in debug output

## [0.1.0] - 2025-10-10

### Added
- Initial prototype implementation
- Basic authentication flow
- Core functionality proof of concept

