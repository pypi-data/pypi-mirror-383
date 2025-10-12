# LogIQ CLI Tool v1.8.0 Release Notes

## 📅 Release Date: October 12, 2025

## 🎯 Focus: Quieter logs, polish, and minor fixes

This release reduces noisy startup warnings, polishes messages, and includes small quality fixes. Functionality remains compatible with 1.7.x.

## ✨ Highlights

### Logging & Noise Reduction

- Suppressed internal startup warnings related to ML fallback checks (now debug-only)
- Cleaner standard output by default; enable DEBUG to see diagnostics

### Stability & Polish

- Minor resilience improvements in model initialization paths
- Kept informative OK/threshold messages; configurable in future if desired

## 🧩 Technical Notes

- No API changes
- Same Python compatibility (3.8–3.12)
- Packaging unchanged aside from version bump

## 📦 Installation

```bash
pip install logiq-cli==1.8.0
```

## 🔄 Upgrade Notes

- No breaking changes
- Recommended for a quieter default CLI experience

## ✅ Verification

- Smoke tests on init, login, and monitor flows
- Verified absence of previously noisy fallback messages in normal runs

## 📌 Files Updated in 1.8.0

- `setup.py`, `__init__.py` – version bump to 1.8.0
- `Scripts/prerag_classifier.py` – downgrade specific prints to debug
- `CHANGELOG.md` – added 1.8.0 section

---

Thanks for using LogIQ CLI. Feedback helps us keep smoothing the edges!
