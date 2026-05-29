# Next Steps

1. Decide how to store large `.fsp`, `.blend`, and `.png` artifacts.
2. If GitHub should hold large files, enable Git LFS before uploading them.
3. Otherwise, keep binaries in local/cloud storage and record stable download links in this repository.
4. Open the uploaded FDTD scripts in Lumerical and verify material names such as `VO2 20` and `SiO2 (Glass) - Palik` exist in the target installation.
5. Re-run one representative Taper case before batch simulation to confirm monitor/export settings.
6. Add a project-level figure index after choosing which render images are final outputs.

## Current upload exclusions

- Password/secret files.
- Logs and cache files.
- Blender `.blend1` backups.
- Large `.fsp`, `.blend`, and `.png` files until storage policy is chosen.
