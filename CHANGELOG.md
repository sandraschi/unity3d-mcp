# Changelog

All notable changes to Unity3D-MCP will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **BREAKING**: Removed `OSCManager` - use `oscmcp` for OSC functionality
- OSC operations now require FastMCP server composition with `oscmcp`
- See module docstring in `vrchat/__init__.py` for composition example

### Added

#### World Labs Integration (Marble/Chisel)
- `import_marble_world`: Import 3D worlds from World Labs Marble/Chisel
- `check_gaussian_splatting`: Check if Gaussian Splatting renderer installed
- `install_gaussian_splatting`: Install aras-p/UnityGaussianSplatting package
- `optimize_worldlabs_for_vrchat`: VRChat optimization recommendations
- Support for mesh formats: `.obj`, `.fbx`, `.glb`, `.gltf`
- Support for Gaussian Splats: `.ply`, `.splat`
- Automatic asset organization (Visuals/, Colliders/, Splats/)

#### UniVRM Package Management
- `check_univrm_installed`: Check UniVRM installation status
- `install_univrm`: Install UniVRM 0.x or 1.0 via Package Manager
- `create_unity_project_with_univrm`: Create project with UniVRM pre-installed
- Git-based package installation via manifest.json

#### Multi-Platform Social VR Support
- `list_vr_platforms`: List all supported social VR platforms
- `check_platform_sdk`: Check SDK installation for any platform
- **ChilloutVR (CCK)**
  - `check_cck_installed`: Check CCK installation
  - `setup_cvr_avatar`: Configure CVRAvatar component
  - `validate_for_chilloutvr`: Validate avatar for CVR
- **Resonite** (no Unity SDK needed - direct import!)
  - `prepare_for_resonite`: Prepare VRM/GLB for direct import
  - `check_resonite_compatibility`: Check model compatibility
- **Cluster** (Japanese social VR)
  - `check_cluster_kit`: Check Creator Kit installation
  - `prepare_for_cluster`: Prepare avatar for Cluster upload

#### VRChat Authentication
- `vrchat_check_auth`: Check VRChat authentication status
- `vrchat_authenticate`: Authenticate with VRChat API (supports 2FA/TOTP)
- `vrchat_check_sdk`: Verify VRChat SDK installation
- `vrchat_validate_avatar`: Validate avatar before upload

#### Testing Infrastructure
- Comprehensive test suite (119+ tests)
- Organized test structure: `unit/`, `integration/`, `e2e/`, `fixtures/`
- Fixture factories for mock Unity projects
- VRM test file support with skip markers
- E2E tests for real Unity integration (--run-e2e flag)
- PowerShell test runner script

### Improved
- MCPB packaging with extensive prompt templates
- CI/CD workflows (GitHub Actions)
- .cursorrules with Rule #1
- .agravrules rulebook
- CONTRIBUTING.md and CHANGELOG.md
- Repository structure and organization
- Documentation quality
- Code quality (ruff configuration)
- Professional standards compliance

## [1.0.0] - 2025-10-26

### Added

#### Core Features
- Unity Editor automation and control
- Project and scene management
- Multi-platform build pipeline
- Asset package management

#### VRM Avatar Pipeline
- VRM import and validation
- Avatar optimization for VRChat
- Animation system setup
- Performance profiling
- Blend shape configuration

#### VRChat Integration
- VRChat SDK automation
- Avatar upload to VRChat platform
- Expression parameter setup
- Expression menu creation
- OSC real-time control
- Performance validation (Poor to Excellent ranks)

#### Additional Features
- Dual interface (stdio + HTTP)
- Comprehensive logging
- Platform management (Windows, macOS, Linux, Android, iOS)
- Intelligent Unity installation detection

### Documentation
- Complete README with feature overview
- Setup and installation guide
- Usage examples
- API reference

### Technical
- FastMCP 2.10+ framework
- Async/await architecture
- Type hints throughout
- Error handling and logging

### Standards
- FastMCP 2.12+ compliant
- MCPB packaging
- Professional folder structure
- Modern Python tooling

---

## Version History

| Version | Date | Type | Description |
|---------|------|------|-------------|
| 1.2.0 | 2025-11-27 | Minor | Multi-Platform Social VR (ChilloutVR, Resonite, Cluster) |
| 1.1.0 | 2025-11-26 | Minor | World Labs + UniVRM + Auth + Testing |
| 1.0.0 | 2025-10-26 | Major | Initial release - Unity automation + VRM + VRChat |

---

**Generated:** 2025-11-26  
**Maintained by:** Sandra  
**Project:** Unity3D-MCP - Professional Unity automation with Austrian precision! 🇦🇹🎮


