# TrackHunter architecture

## Overview

TrackHunter is a Python desktop application for automating search and download workflows on Muzpa. The current app keeps the original technology stack:

- Python
- PySide6 for the desktop UI
- Playwright for browser automation
- PyInstaller for Windows executable generation
- IExpress-based Windows setup generation

## Runtime modules

- `trackhunter/app.py`: current PySide6 desktop UI, dialogs, workers, styling and GUI orchestration.
- `trackhunter/cli.py`: command-line orchestration and argument parsing.
- `trackhunter/auth.py`: login flow.
- `trackhunter/search.py`: search field discovery and candidate scoring.
- `trackhunter/download.py`: per-track automation and download flow.
- `trackhunter/history.py`: local history state, duplicate detection and safe persistence.
- `trackhunter/report.py`: final text report generation.
- `trackhunter/utils.py`: text normalization, track parsing, tracklist loading and stop helpers.
- `trackhunter/models.py`: shared dataclasses.

## Current data flow

1. The UI or CLI collects credentials, tracklist, output paths and execution options.
2. `trackhunter.cli.run()` loads the tracklist and history.
3. Playwright opens Muzpa and authenticates.
4. `process_tracks()` searches and handles one track at a time.
5. History is updated when a track is downloaded, resolved or marked missing.
6. The CLI now passes `on_history_changed` so history is persisted after each successful state change.
7. `write_results()` writes the final execution log and missing-track file.

## History persistence

`trackhunter/history.py` now writes history atomically:

1. Create a temporary `*.tmp` file.
2. Write JSON.
3. Flush and `fsync`.
4. Replace the target file.

If the history JSON is corrupted, the file is copied to a backup named:

```text
track_history.corrupted_YYYYMMDD_HHMMSS.json
```

Then TrackHunter starts with an empty history instead of failing during startup.

## Testing boundary

Unit tests are intentionally limited to pure logic:

- no Chromium launch;
- no Muzpa access;
- no real downloads;
- no dependency on user files.

Current coverage lives in `tests/` and covers helpers, matching, history and report generation.

## Known technical debt

- `trackhunter/app.py` is still monolithic and should be split gradually.
- Logging still relies heavily on printed text and UI redirection.
- Installer logic is still concentrated in `scripts/create_installer.ps1`.
- Mutable data is still primarily under the executable/base directory.
- Dependencies are not yet pinned for runtime releases.
