# Local validation

Validated on 15 October 2026 on macOS arm64, with Python 3.14.7, NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, and Biopython 1.88.

## Prepared source distribution

- Ten regression tests passed, covering SciPy mode behavior, zipped database extraction, invalid archives, missing indexes, reference revision mismatches, failed-checkout recovery, external command failures, download checksum failures, launcher argument handling, and incompatible Kallisto rejection.
- The runtime helper downloaded the typing frequency table and all listed upstream test fixtures; their SHA256 checks passed.
- Checksums for the four optional quantification JSON support files were verified against the pinned upstream revision. The large optional FASTA downloads and full quantification workflow were not tested.
- The included build helper compiled native arm64 Kallisto 0.48.0 successfully, including its bundled HTSlib and HDF5 support.
- All eight command help screens ran successfully.
- Extraction and full FASTQ-to-genotype processing from this source checkout succeeded for HLA-C on the upstream sample, using IMGT/HLA 3.66.0, commit `d972ae287948dc2e5468a40ff3b3d27227541189`. The calls matched the repaired installation: `C*01:02:62` and `C*08:01:01`.
- The export smoke test reused the working installation's reference via temporary links. These links and all generated or downloaded runtime files were removed before source packaging. The new export did not independently download and build a fresh current reference.
- The local Git index passed the upload check for personal absolute paths, unexpected binaries, downloaded datasets, generated references, and oversized files.

## Earlier repair validation

Before export, the repaired installation rebuilt the documented IMGT/HLA 3.24.0 reference. Its genotype and partial genotype calls matched all seven genes in the upstream expected fixtures. Current IMGT/HLA 3.66.0 references were then built successfully, and seven-gene genotyping completed. Switching between the historical and current database revisions was also checked.

## Remaining platform coverage

The supplied Python 3.12 Conda environment recipe has not been solved in a fresh environment. Linux, Windows, and macOS Intel have not been tested. The GitHub Actions workflow is included but has not run remotely. The inherited customization and quantification workflows have not been validated end to end. Runtime downloads and compiled tools are intentionally absent from the upload payload.
