# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.13.0] - 2025-10-07

### Added

- **BOD Parser Module** : Complete module for parsing Infor M3 BOD XML documents to CSV
  - `BODParser` : Main parser class with support for Header + Lines structures
  - `BODConfig` : Configuration dataclass for mapping definitions
  - `BODConfigLoader` : Load configurations from YAML, JSON, or S3
  - `BODTransformers` : Pre-built transformation functions (date, text, numbers, booleans)
  - Support for custom transformers via `register_transformer()`
  - Multiple flatten modes: `duplicate_header`, `header_only`, `lines_only`
  - XPath-based field extraction with namespace support
- **Documentation System** : Complete auto-generated documentation
  - MkDocs with Material theme integration
  - Auto-generation from Python docstrings (Google-style)
  - Complete navigation with tabs, sections, breadcrumbs
  - Search functionality with suggestions and highlighting
  - Light/Dark mode support
  - Deployment script for AWS S3 hosting
  - Documentation URL: http://cmp-docs-internal.s3-website.eu-west-3.amazonaws.com
- **New Dependencies** : Added `pyyaml` and `lxml` for XML and YAML processing
- **Development Tools** : Added MkDocs and related packages in dev dependencies

### Changed

- Updated `setup.py` with new dependencies
- Updated `__init__.py` to export new BOD Parser modules
- Enhanced README.md with comprehensive documentation section
- Python minimum version changed from 3.6 to 3.7 (for dataclasses support)

### Fixed

- QuableAPI lazy loading to avoid Parameter Store errors when not using the class
- Import issues in `__init__.py` for better module organization

## [1.12.7] - 2025-06-25

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Install specific version of pymssql

## [1.12.6] - 2025-06-23

### Added

- Nothing

### Changed

- Nothing

### Fixed

- send_email_to_support signature in S3 and FTP classes

## [1.12.5] - 2025-05-07

### Added

- Nothing

### Changed

- S3 : archive location

### Fixed

- Nothing

## [1.12.4] - 2025-04-25

### Added

- S3 : Function to archive files

### Changed

- Nothing

### Fixed

- Nothing

## [1.11.4] - 2025-03-07

### Added

- Nothing

### Changed

- Parameters : Allow to extract parameter value from parameters list

### Fixed

- Nothing

## [1.10.4] - 2025-03-06

### Added

- Nothing

### Changed

- Sharepoint : Allow to get context

### Fixed

- Nothing

## [1.9.4] - 2025-02-10

### Added

- Nothing

### Changed

- Allow to get all parameters by path

### Fixed

- Nothing

## [1.8.4] - 2025-02-04

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Import of the ses utils

## [1.8.3] - 2025-02-03

### Added

- Functions to better handle exceptions (display details)

### Changed

- Nothing

### Fixed

- Nothing

## [1.7.3] - 2025-01-30

### Added

- Nothing

### Changed

- Additional condition for decrypting parameter in get_parameter function

### Fixed

- Nothing

## [1.6.3] - 2024-12-11

### Added

- Nothing

### Changed

- Allow to get parameter by passing only one parameter to the function

### Fixed

- Nothing

## [1.5.3] - 2024-12-10

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Import only the SQL connector given in parameter

## [1.5.2] - 2024-12-09

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Fix pattern syntax in check_email function

## [1.5.1] - 2024-12-03

### Added

- Add upload function to FTP class

### Changed

- Nothing

### Fixed

- Nothing

## [1.4.1] - 2024-11-07

### Added

- Add class to interact with Sharepoint

### Changed

- Nothing

### Fixed

- Nothing

## [1.3.1] - 2024-10-10

### Added

- Add mssql class to connect to Microsoft SQL Servers databases

### Changed

- Nothing

### Fixed

- Nothing

## [1.2.1] - 2024-10-04

### Added

- Nothing

### Changed

- Add missing disconnect function to odbc

### Fixed

- Removed `from_email` and `to_email` parameters from the function signature
- Now uses a generic error email address for `from_email`, retrieved from the parameter store
- Support email address (`to_email`) is now passed directly to the function, retrieved from the parameter store

## [1.1.0] - 2024-09-27

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Fixed get_parameter function: Added verification condition to decrypt the password

## [1.2.0] - 2024-09-30

### Added

- Added SqlFactory and Odbc classes: Allows connection to Microsoft Server databases

### Changed

- Nothing

### Fixed

- Nothing

## [1.1.0] - 2024-09-27

### Added

- Nothing

### Changed

- Nothing

### Fixed

- Fixed get_parameter function: Added verification condition to decrypt the password

## [1.0.0] - 2024-09-23

### Added

- Added FTP functions
- Added S3 functions
- Added MongoDB functions
- Added SES functions
- Added utils functions

### Changed

- Nothing

### Fixed

- Nothing

## [0.1.1] - 2024-09-02

### Added

- Added and tested initial functions to get started with PyPI

### Changed

- Nothing

### Fixed

- Nothing

## [0.0.1] - 2024-09-02

### Added

- Initial project setup
