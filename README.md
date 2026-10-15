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
