# Work Log

## 2026-05-29

### Goal

Synchronize this computer's Codex configuration and upload the previous FDTD project handoff to GitHub repository `tya34/FDTD`.

### Completed locally

- Restored Codex global `developer_instructions` for output cleanup and work-upload behavior.
- Added local memory files:
  - `C:\Users\tya\.codex\memories\download-cleanup.md`
  - `C:\Users\tya\.codex\memories\work-upload-command.md`
- Corrected trusted project paths in `C:\Users\tya\.codex\config.toml` for:
  - `C:\博士\课题1\模拟`
  - `C:\博士\课题1\FDTD`
  - `C:\博士\cedex`

### FDTD upload policy

The local FDTD folder includes text scripts plus roughly 1.0 GB of binary artifacts. This first GitHub upload keeps the maintainable source/handoff material and excludes sensitive, temporary, cache, log, backup, and large binary files.

### Local project inventory

- Text/script files found in `C:\博士\课题1\FDTD`: 15 files, about 0.11 MB excluding sensitive password file.
- Binary/model/render files found in `C:\博士\课题1\FDTD`: 45 files, about 1008.98 MB.
- Explicitly excluded sensitive file: `远程桌面密码.txt`.
