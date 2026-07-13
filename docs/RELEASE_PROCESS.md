# Release process

## Version source

The release version is stored in:

```text
RELEASE_VERSION.txt
```

Current version:

```text
v2.1
```

## Local validation

Run tests before building distributable artifacts:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pytest -v
python -m trackhunter.cli --help
```

## Folder executable

Generate the folder-based executable:

```powershell
python -m PyInstaller --noconfirm --clean TrackHunterApp.spec
```

Output:

```text
dist/TrackHunter/TrackHunter.exe
```

## ZIP package

Generate the ZIP package:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_release.ps1
```

Outputs:

```text
release/TrackHunter-v2.1/
release/TrackHunter-v2.1.zip
```

## One-file executable

Generate the one-file executable used by the installer:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH='0'
python -m PyInstaller --noconfirm --clean --onefile --windowed --name TrackHunter --icon assets\app_icon.ico --add-data "assets\logo.png;assets" --add-data "assets\app_icon.png;assets" --distpath dist-onefile --workpath build-onefile scripts\trackhunter_gui.py
```

Output:

```text
dist-onefile/TrackHunter.exe
```

## Installer

Generate the Windows setup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\create_installer.ps1
```

Output:

```text
release/TrackHunter-v2.1-Setup.exe
```

## GitHub note

The generated setup is too large for a normal Git commit. Publish the generator scripts and source changes in Git. Distribute the generated setup through a release asset or another file distribution channel.

## Current validated state

The branch `refactor/reliability-and-maintainability` currently has:

- technical baseline captured;
- unit tests for core helpers;
- safer history persistence;
- updated executable and installer generated locally;
- `python -m pytest -v` passing with 42 tests.
