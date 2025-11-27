# Test Fixtures

This directory contains test fixture files for local testing.

## Required Files (not in git)

Large binary files are excluded from git. For full local testing, add:

| File | Purpose | Source |
|------|---------|--------|
| `Nekomimi-chan.vrm` | VRM avatar load testing | [VRoid Hub](https://hub.vroid.com/) or your own VRM |

## Included Files

- `unity_project/` - Mock Unity project structures (generated)
- `vrchat/` - VRChat-specific test data (generated)
- `factories.py` - Fixture factory functions

## Setup for Local Testing

1. Download or create a VRM file
2. Place it in this directory as `Nekomimi-chan.vrm`
3. Run tests: `python -m pytest tests/ -v`

Tests will skip VRM-specific tests if the file is missing.

