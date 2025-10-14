# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-10-07

### 🚀 Added
- **Modern Python Support**: Full type hints throughout the codebase
- **Async/Await Support**: Complete async implementation with `AsyncSlackApp`
- **Official Slack SDK Integration**: Replaced custom HTTP client with official Slack SDK
- **Enhanced BlockBuilder**: Improved API with better type safety and validation
- **Comprehensive Test Suite**: 95%+ test coverage with pytest
- **GitHub Actions CI/CD**: Automated testing, linting, and deployment
- **Pre-commit Hooks**: Code quality enforcement with ruff, mypy, and more
- **Modern Dependencies**: Updated to latest Python packaging standards

### 🔄 Changed
- **BREAKING**: Removed singleton pattern from `SlackApp` - use regular instantiation
- **BREAKING**: Updated method signatures with type hints
- **BREAKING**: Replaced custom exception handling with official SDK patterns
- **BREAKING**: Updated OAuth flow to use official SDK methods
- Modernized project structure with `pyproject.toml`
- Enhanced error handling and logging
- Improved documentation with examples

### 🛠 Fixed
- Fixed exception `__init__` method signatures (missing `__` in method names)
- Fixed method name typo in `_check_request_time_stamp`
- Added missing `@staticmethod` decorators in `BlockBuilder`
- Fixed import issues and circular dependencies

### 📚 Documentation
- Complete rewrite of README with modern examples
- Added comprehensive usage examples
- Created migration guide from v0.1.x
- Added API documentation with type hints

### 🏗 Infrastructure
- Added GitHub Actions for CI/CD
- Added pre-commit configuration
- Added security scanning with bandit
- Added coverage reporting
- Modern Python packaging with hatchling

## [0.1.x] - Previous Versions

### Legacy Features
- Basic Slack app functionality
- Router pattern for interactions
- Block builder for UI components
- OAuth flow support
- Custom HTTP client implementation

---

## Migration from v0.1.x to v0.2.0

See [MIGRATION.md](MIGRATION.md) for detailed migration instructions.