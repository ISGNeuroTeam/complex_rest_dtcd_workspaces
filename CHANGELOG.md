# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.6] - 2022-08-19
### Added:
- Default permissions to `-rwxr-xr-x` (`755`) on initialization scripts.
- Nice messages in `create_root_records` command.

### Fixed:
- Bug in `database_init.sh`: project's `venv` was not activated due to a missing symbol before variable name.

## [0.2.5] - 2022-08-18
### Added:
- Database initialization script `database_init.sh`.

## [0.2.4] - 2022-08-10
### Fixed:
- You can now get root dir info.
- Listed directory info added to listing.

## [0.2.3] - 2022-07-18

### Fixed:
- .DIR_INFO meta file absence in root workspaces directories fixed.

### Added:
- Necessary records in rest auth db now can be added via create_root_records Django management command.

## [0.2.2] - 2022-07-01

### Added:
- Necessary records in rest auth db now can be added via create_root_records Django management command.

## [0.2.1] - 2022-06-30

### Fixed:
- Guidelines following.

## [0.2.0] - 2022-06-30

### Added
- Meta support added.
- Workspaces can now be organized in directories. .
- Workspaces can now work with role model if Complex Rest supports role model.
- Creation and modification time are added to workspaces and directories for sorting reasons.

### Changed
- Workspaces are now separate from dtcd_server plugin. dtcd_server is now called dtcd_utils.

### Fixed
- .gitkeep absence now doesn't error out when listing plugins and workspaces.