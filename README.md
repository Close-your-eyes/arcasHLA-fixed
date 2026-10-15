# arcasHLA compatibility fixes

Source distribution based on [RabadanLab/arcasHLA v0.5.0](https://github.com/RabadanLab/arcasHLA/tree/v0.5.0), modified on 15 October 2026. Original authors: Rose Orenbuch, Ioan Filip, and Itsik Pe'er. This is an independently maintained compatibility version. The original documentation is preserved in [README.UPSTREAM.md](README.UPSTREAM.md).

The changes repair modern SciPy reference building, support current zipped IMGT/HLA releases, regenerate missing typing references, report failed external commands, and remove an obsolete Biopython import. The launcher selects a private compatible Kallisto when available and otherwise checks the version on PATH. It uses the active environment's Python, with an optional `ARCASHLA_PYTHON` override.

## Install

Run these commands inside this repository after installing Conda and your platform's C/C++ compiler. On macOS, install the Xcode Command Line Tools first. Linux also needs the usual compiler toolchain.

```bash
conda env create -f environment.yml
conda activate arcashla-fixed
python scripts/setup_runtime.py --data --build-kallisto --jobs 4
./arcasHLA reference --update -v
```

The build script compiles native Kallisto 0.48.0 into `bin/kallisto`; it does not replace other installations. An existing compatible Kallisto 0.44.x or 0.48.x can be used instead, by omitting `--build-kallisto`. Recent Kallisto releases that removed the required `pseudo` command are rejected with setup instructions.

Runtime support files come from a pinned upstream source revision and are checked against SHA256 digests. IMGT/HLA is downloaded separately from its official repository. `reference --update` selects whatever release is current when the command runs. For reproducible analyses, record the reference commit printed in the log and use `reference --commit COMMIT` to select it later.

Legacy upstream shell routines expect repository, input, and output paths without spaces or shell metacharacters. Invoke `./arcasHLA` directly from this checkout rather than symlinking the launcher. Python 3.12 or newer is required by the setup script. Typing remains the validated workflow; optional quantification commands retain upstream behavior and need `python scripts/setup_runtime.py --quant-data` for their separate support datasets.

## Genotype paired-end RNA-seq

For a coordinate-sorted BAM, replace the input path and sample basename:

```bash
mkdir -p hla_results
./arcasHLA extract /path/to/sample.bam -o hla_results -t 8 -v
./arcasHLA genotype \
  hla_results/sample.extracted.1.fq.gz \
  hla_results/sample.extracted.2.fq.gz \
  -g A,B,C,DPB1,DQB1,DQA1,DRB1 -o hla_results -t 8 -v
```

Results are written to `hla_results/sample.genotype.json`. For single-end inputs, use `--single` in both commands and supply the single extracted FASTQ. Choose threads according to your own hardware; eight is a starting point on a 14-core machine. Later genotyping stages may use fewer cores.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/check_upload.py
```

The compatibility repair was validated on macOS arm64: extraction succeeded, genotype and partial genotype calls matched all seven genes in the upstream 3.24.0 test fixtures, and genotyping also ran with IMGT/HLA 3.66.0, commit `d972ae287948dc2e5468a40ff3b3d27227541189`. Validation of this portable export is recorded in [VALIDATION.md](VALIDATION.md). Other operating systems and a fresh Conda solve have not yet been validated.

Test fixtures can be downloaded separately:

```bash
python scripts/setup_runtime.py --test-data
```

Follow the upstream test commands using `test/fixtures/test.bam` as input and `test/fixtures/expected_output` for comparisons. Those expected calls require reference 3.24.0. Changing the reference changes the allele catalog and can change calls. Restore your analysis reference afterwards.

## License and data

The modified arcasHLA source is distributed under GNU GPL version 3 or later. Keep [LICENSE](LICENSE), the original notices, and the dated change notices when redistributing it. See [NOTICE.md](NOTICE.md) and [CHANGELOG.md](CHANGELOG.md).

This source repository excludes downloaded databases, generated reference sequences and indexes, external binaries, and sample datasets. IMGT/HLA has separate Attribution-NoDerivs terms and requests links instead of mirrors; obtain permission before distributing modified database data. Its [license](https://github.com/ANHIG/IMGTHLA/blob/Latest/LICENCE.md) applies independently of arcasHLA's code license. Downloaded support datasets retain their upstream terms.

## Publish this local repository

The repository is prepared locally with files staged for review and no configured upload destination. Review and commit the files, create an empty repository under your GitHub account, then replace `YOUR_USERNAME` and `YOUR_REPOSITORY` below:

```bash
git diff --cached --stat
python scripts/check_upload.py
git commit -m "Prepare arcasHLA compatibility source release"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If Git asks for author identity, configure your own name and email before committing. An `upstream` remote points to the original project for reference. This clean export starts new history; it is not a GitHub-linked fork with upstream history. Do not upload your Conda installation directory or ignored runtime data.
