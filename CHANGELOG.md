# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added:
- Workspaces and Directories tests added (no Role Model tests though)
- Additional info about permissions on GET requests

## [0.2.2] - 2022-07-01

### Added:
- Necessary records in rest auth db now can be added via create_root_records Django management command

## [0.2.1] - 2022-06-30

### Fixed:
- Guidelines following

## [0.2.0] - 2022-06-30

### Added
- Meta support added
- Workspaces can now be organized in directories. 
- Workspaces can now work with role model if Complex Rest supports role model
- Creation and modification time are added to workspaces and directories for sorting reasons

### Changed
- Workspaces are now separate from dtcd_server plugin. dtcd_server is now called dtcd_utils.

### Fixed
- .gitkeep absence now doesn't error out when listing plugins and workspaces