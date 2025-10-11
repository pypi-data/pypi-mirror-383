# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-27

### Added
- **Unified Package Structure**: Created comprehensive Python package with both V1 and V2 functionality
- **Enhanced CLI**: Unified command-line interface with version selection (`spymot v1` vs `spymot v2`)
- **Package Installation**: Full pip installation support with `pip install spymot`
- **Comprehensive Documentation**: Complete README with installation and usage instructions
- **Version Management**: Automatic versioning with setuptools_scm
- **Development Tools**: Black, Ruff, MyPy, and Pytest configuration
- **Package Metadata**: Complete pyproject.toml with dependencies and classifiers

### Changed
- **Project Structure**: Reorganized into proper Python package layout (`src/spymot/`)
- **Import System**: Unified imports for both V1 and V2 functionality
- **CLI Interface**: Enhanced command structure with subcommands
- **Documentation**: Comprehensive README covering both versions

### Fixed
- **Import Issues**: Resolved circular imports and path issues
- **CLI Compatibility**: Fixed command-line interface for both versions
- **Package Structure**: Proper Python package layout for distribution

## [1.0.0] - 2024-12-01

### Added
- **V1 Original System**: Basic protein motif detection functionality
- **AlphaFold Integration**: Basic structure confidence scoring
- **Core Motif Database**: Essential motif patterns
- **Simple CLI**: Basic command-line interface

## [0.1.0] - 2024-11-01

### Added
- **Initial Development**: Project foundation
- **Basic Motif Detection**: Core functionality
- **Sequence Analysis**: Fundamental protein analysis
