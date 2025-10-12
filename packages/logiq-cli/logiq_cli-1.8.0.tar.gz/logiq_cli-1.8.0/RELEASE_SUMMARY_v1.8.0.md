# LogIQ CLI Tool v1.8.0 - Release Summary

## 📦 Package Information

- Version: 1.8.0
- Release Date: October 12, 2025
- Package: logiq-cli

## 🎯 Release Focus

Quieter default logs, minor stability/polish in initialization paths, no breaking changes.

## 🔑 Key Changes

### Logging & Noise Reduction

- Suppressed ML fallback warnings by default (now visible in DEBUG only)

### Stability & Polish

- Small improvements in model initialization and error paths

## 🗂️ Files Modified

- setup.py – version bumped to 1.8.0
- __init__.py – version bumped to 1.8.0
- Scripts/prerag_classifier.py – downgraded noisy prints to debug
- CHANGELOG.md – added 1.8.0 section
- README.md – updated to v1.8.0

## 🧪 Testing Status

- Smoke tested init/login/monitor flows
- Verified noisy fallback messages no longer appear by default

## ✅ Pre-Release Checklist

- [x] Versions updated across files
- [x] Changelog and release notes added
- [x] README updated for 1.8.0
- [x] Package builds locally (expected, same structure as 1.7.x)

## 🚀 Next Steps

1. Build: `python -m build`
2. Upload to TestPyPI and verify install
3. Upload to PyPI
4. Tag and publish GitHub release

—

Thanks for continuing to improve LogIQ CLI!
