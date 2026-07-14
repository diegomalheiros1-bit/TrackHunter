# TrackHunter technical baseline

Baseline originally captured on 2026-07-13 during the reliability and maintainability pass.

## Version

- Current release version: `v2.1`
- Current GUI window title: `TrackHunter v2.1`
- Current definitive branch: `main`
- Latest validated state is tracked on `main`; use `git log -1` for the current commit.

## Current structure

- `trackhunter/app.py`: PySide6 desktop application and GUI worker code.
- `trackhunter/cli.py`: CLI entry point for automation.
- `trackhunter/search.py`: candidate scoring and Playwright search helpers.
- `trackhunter/download.py`: download orchestration.
- `trackhunter/history.py`: local history persistence.
- `trackhunter/report.py`: text report/log file generation.
- `trackhunter/utils.py`: normalization, track parsing and tracklist loading.
- `scripts/create_release.ps1`: copies `dist/TrackHunter` into `release/TrackHunter-v2.1` and creates the ZIP.
- `scripts/create_installer.ps1`: creates a Windows setup executable with terms acceptance, destination selection, shortcuts, registry entry and uninstaller.
- `TrackHunterApp.spec`: PyInstaller folder-based build recipe.

## Baseline commands executed

```powershell
Get-Content -Raw RELEASE_VERSION.txt
python -m trackhunter.cli --help
$p = Start-Process -FilePath python -ArgumentList '-m','trackhunter.app' -PassThru -WindowStyle Hidden; Start-Sleep -Seconds 5; if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force }
python -m PyInstaller --noconfirm --clean TrackHunterApp.spec
powershell -ExecutionPolicy Bypass -File scripts\create_installer.ps1
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

## Build commands

Folder-based executable:

```powershell
python -m PyInstaller --noconfirm --clean TrackHunterApp.spec
```

Installer:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_installer.ps1
```

Release ZIP:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

## Generated artifacts

- `dist/TrackHunter/TrackHunter.exe`
  - Size observed on 2026-07-14: 3,483,388 bytes.
- `release/TrackHunter-v2.1.zip`
  - Size observed on 2026-07-14: 384,638,700 bytes.
- `release/TrackHunter-v2.1-Setup.exe`
  - Size observed on 2026-07-14: 380,882,944 bytes.
- `dist-onefile/TrackHunter.exe`
  - Size observed on 2026-07-14: 382,205,470 bytes.

The generated `release/` and `dist*/` artifacts are ignored by Git and are not suitable for normal GitHub commits because the setup executable is larger than GitHub's 100 MB file limit.

## Installer behavior

The current installer:

- opens a GUI setup window;
- shows `TrackHunter v2.1`;
- requires accepting the TrackHunter terms of use before continuing;
- lets the user select an installation directory;
- installs `TrackHunter.exe`;
- creates `downloads`, `logs` and `state` folders under the chosen installation directory;
- preserves an existing `state/tracklist.txt` when reinstalling over an existing installation;
- creates Desktop and Start Menu shortcuts;
- registers `TrackHunter` under the current user's Windows uninstall registry key;
- copies an `uninstall.ps1` script;
- uninstalls by removing the installation folder, shortcuts and uninstall registry key.

## Manual baseline validation

- CLI help opens successfully with `python -m trackhunter.cli --help`.
- GUI smoke test launched `python -m trackhunter.app` and was stopped after 5 seconds.
- PyInstaller folder build completed successfully.
- Installer generation completed successfully.
- Release ZIP generation completed successfully.

No real Muzpa login, browser automation against Muzpa, search or download was performed during this baseline to avoid external calls and credential use.

## Warnings observed

PyInstaller generated `build/TrackHunterApp/warn-TrackHunterApp.txt`.

Observed warnings are mostly optional or platform-specific imports, including:

- POSIX-only modules such as `pwd`, `grp`, `fcntl`, `posix`, `_posixsubprocess` and `_posixshmem` on Windows.
- Optional platform modules such as `_scproxy`, `vms_lib`, `java` and `java.lang`.
- PyInstaller runtime helper `pyimod02_importers`.
- Conditional Playwright import `playwright._impl._worker`.

These warnings did not prevent the executable from being generated.

## Known risks

- `trackhunter/app.py` is a large monolithic file and mixes UI, workers, dialogs, styles and path logic.
- `scripts/create_installer.ps1` currently embeds installer UI, install script, uninstall script and terms text in one large generator script.
- Runtime data is still written relative to the executable/base directory, which complicates updates and uninstalls.
- History persistence now has corrupted JSON backup and atomic replace behavior covered by tests.
- Logging now has a shared runtime file setup, but some user-facing progress still uses text output for CLI/UI compatibility.
- Automated tests now cover helpers, matching, history, reports, config and logging.
- Dependencies are not pinned exactly.
- No CI workflow is present yet.

## Known limitations

- The installer is generated with Windows IExpress and takes several minutes because it packages a roughly 380 MB one-file executable.
- The generated setup executable is too large for a normal GitHub commit.
- The baseline did not validate real login, MP3 download, AIFF download or Muzpa selector behavior.
- Current uninstall behavior removes the selected installation folder; safer data preservation modes are planned for the modular installer step.

## Current acceptance status

- Definitive branch updated: `main`.
- CLI help smoke test: passed.
- GUI launch smoke test: passed.
- Executable generation: passed.
- Installer generation: passed.
- Release ZIP generation: passed.
- Automated unit tests: 49 tests passing.
- Ruff: not configured yet.
- GitHub Actions: not configured yet.
