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