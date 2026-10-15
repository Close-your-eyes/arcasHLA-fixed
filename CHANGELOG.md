# Changes

## 15 October 2026 — local compatibility release

Based on arcasHLA v0.5.0, upstream revision `157fabbc4bdb6a72cef1e608b9875ba06d8b4af5`.

- Fix reference-building errors caused by modern SciPy returning scalar mode values.
- Support both historical Git LFS sequence data and current `hla.dat.zip` releases.
- Check for missing or empty typing indexes and metadata, and rebuild incomplete references.
- Fetch the requested IMGT/HLA revision before checkout; handle generated sequence files when switching versions.
- Limit new database checkouts to typing support files with sparse checkout.
- Report external command failures instead of continuing after a failed dependency command.
- Remove the unused `Bio.Alphabet` import that fails with modern Biopython.
- Replace installation-specific Python paths with a portable environment-based launcher.
- Prefer private Kallisto and give a clear error for incompatible versions.
- Add optional native Kallisto build instructions and a checksum-verified runtime support downloader.
- Preserve upstream licensing and documentation, and add tests and upload checks.
- Exclude downloaded datasets, generated reference files, binaries, personal paths, and local backups from the source repository.

The inherited scientific genotyping algorithm and its defaults have not been deliberately changed. Reference catalog updates can change reported alleles. Full quantification and customization workflows have not been validated for this release.
