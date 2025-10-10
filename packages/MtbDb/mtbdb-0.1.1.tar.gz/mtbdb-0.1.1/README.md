# MtbDb: Genomics Database Toolkit for Mycobacterium Tuberculosis

> 🇬🇧 English | 🇨🇳 [简体中文](./README_zh.md)

MtbDb is a Python toolkit specifically designed for Mycobacterium tuberculosis genomics analysis, providing efficient database querying and analysis capabilities for TB genomic data.

## Features

- 🧬 TB genomic database queries
- 📊 Gene Variant Analysis (TBVA)
- 🔍 Gene Expression Analysis (TBGEA)
- 📈 Statistical analysis and visualization
- 🔗 Support for multiple data formats
- 🧪 FASTA/FASTQ/SNP to VCF conversion
- 📦 Built-in H37Rv reference genome (ready to use)

## Installation

### Quick Start: Using Conda (Highly Recommended)

If you need FASTA/FASTQ to VCF conversion features, we recommend using Conda, which automatically configures all Python packages and bioinformatics tools:

```bash
# Clone the repository
git clone https://github.com/16627517673/mtbdb.git
cd mtbdb

# Create and activate conda environment
conda env create -f environment.yml
conda activate mtbdb

# Verify installation
python -c "from mtbdb.tbva import check_all_dependencies; check_all_dependencies()"
```

### Python Package Only (Without External Tools)

If you only need VCF parsing and annotation features, you can install via pip alone:

#### Install from PyPI
```bash
pip install MtbDb
```

#### Install from TestPyPI
```bash
pip install -i https://test.pypi.org/simple/ MtbDb
```

#### Install from Source
```bash
git clone https://github.com/16627517673/mtbdb.git
cd mtbdb
pip install -e .
```

## Environment Configuration and Dependencies

### Python Dependencies
- Python >= 3.8
- intervaltree >= 3.0.2
- numpy >= 1.20.0
- pandas >= 1.2.0
- scipy >= 1.6.0
- statsmodels >= 0.12.0

### External Bioinformatics Tools (Required for FASTA/FASTQ to VCF)

⚠️ **Important**: The following tools are system binaries and **cannot be installed via pip**

#### Tools Required for FASTA to VCF
- **MUMmer Suite** (nucmer, delta-filter, show-snps)
  - For whole genome alignment and SNP extraction

#### Tools Required for FASTQ to VCF
- **bwa**: Short reads alignment
- **samtools**: SAM/BAM file processing
- **varscan**: Variant calling
- **fastp**: Quality control
- **fastq-dump** (optional): SRA file extraction

#### Installation Methods

**Option 1: Using Conda (Recommended)**
```bash
# Method A: Using provided environment configuration
conda env create -f environment.yml
conda activate mtbdb

# Method B: Manual installation
conda install -c bioconda mummer bwa samtools varscan fastp sra-tools
```

**Option 2: Using Homebrew (macOS)**
```bash
brew install brewsci/bio/mummer bwa samtools fastp
# varscan needs separate JAR file download
```

**Option 3: Build from Source**
- Refer to each tool's official documentation

#### Verify Tool Installation

```python
from mtbdb.tbva import check_all_dependencies
check_all_dependencies()
```

Example output:
```
Checking MtbDb external tool dependencies...

【FASTA to VCF Tools】
  nucmer: ✓ Installed 4.0.0beta2
  delta-filter: ✓ Installed
  show-snps: ✓ Installed

【FASTQ to VCF Tools】
  bwa: ✓ Installed 0.7.17
  samtools: ✓ Installed 1.15
  varscan: ✓ Installed 2.4.4
  fastp: ✓ Installed 0.23.2
  fastq-dump: ✓ Installed (optional)

Summary: 8/8 tools available
✓ All required tools are properly installed!
```

## Quick Start

### Built-in Reference Genome

MtbDb includes the standard H37Rv reference genome (NC_000962.3, 4.4MB) with all necessary index files:
- H37Rv complete genome sequence (.fa)
- BWA index files (.bwt, .pac, .sa, .amb, .ann)
- samtools index (.fai)

**Advantages:**
- ✅ No manual download or configuration needed
- ✅ Ready to use with one line of code
- ✅ Custom reference genomes also supported

```python
from mtbdb.tbva import get_default_reference_fasta

# View built-in reference genome path
ref_path = get_default_reference_fasta()
print(f"Built-in reference genome: {ref_path}")
# Output: /path/to/mtbdb/data/reference/H37Rv_complete_genome.fa
```

### Basic VCF Parsing and Annotation

```python
from mtbdb.tbva import VCFParser, VariantAnnotator

# Parse VCF file
parser = VCFParser('sample.vcf', filter_pass=True)
snps = parser.get_snps()
indels = parser.get_indels()

# Variant annotation
annotator = VariantAnnotator('sample.vcf')
annotated_variants = annotator.annotate()
```

### FASTA to VCF (Comparative Genomics)

Compare two genomes and generate VCF file using MUMmer toolkit:

```python
from mtbdb.tbva import fasta_to_vcf

# Method 1: Using built-in H37Rv reference (simplest)
vcf_file = fasta_to_vcf(
    query_fasta='sample_genome.fasta',
    output_vcf='output/sample.vcf'
)

# Method 2: Using custom reference genome
vcf_file = fasta_to_vcf(
    query_fasta='sample_genome.fasta',
    output_vcf='output/sample.vcf',
    reference_fasta='custom_reference.fasta',
    chrom_id='custom_chrom_id'
)

print(f"VCF file generated: {vcf_file}")
```

**Prerequisites:** MUMmer toolkit (see [Environment Configuration](#environment-configuration-and-dependencies) section)

### FASTQ to VCF (Re-sequencing Analysis)

Detect variants from FASTQ sequencing data and generate VCF file:

```python
from mtbdb.tbva import fastq_to_vcf

# Method 1: Using built-in H37Rv reference (simplest)
vcf_file = fastq_to_vcf(
    output_dir='output',
    sample_name='ERR181314',
    fastq1='ERR181314_1.fastq.gz',
    fastq2='ERR181314_2.fastq.gz',
    threads=8
)

# Method 2: Using custom reference genome
vcf_file = fastq_to_vcf(
    output_dir='output',
    sample_name='sample001',
    fastq1='sample_R1.fastq',
    fastq2='sample_R2.fastq',
    reference_fasta='custom_reference.fa',
    threads=16
)

print(f"VCF file generated: {vcf_file}")
```

**Prerequisites:** bwa, samtools, fastp, varscan, etc. (see [Environment Configuration](#environment-configuration-and-dependencies) section)

### SNP to VCF (Existing show-snps Output)

If you already have SNP file generated by MUMmer show-snps, convert directly to VCF format:

```python
from mtbdb.tbva import snp_to_vcf

# Basic usage: Simplest conversion (using H37Rv defaults)
vcf_file = snp_to_vcf(
    snp_file='sample.snps',
    output_vcf='sample.vcf'
)

# Full usage: Custom chromosome ID and reference info
vcf_file = snp_to_vcf(
    snp_file='sample.snps',
    output_vcf='sample.vcf',
    chrom_id='NC_000962.3',
    reference_name='H37Rv_genome.fasta',
    filter_indels=True  # Filter indels, keep only SNPs
)

print(f"VCF file generated: {vcf_file}")
```

**Advantages:**
- ✅ No external tool dependencies (pure Python)
- ✅ Fast conversion (seconds)
- ✅ Suitable for existing show-snps output
- ✅ Configurable chromosome ID and reference info

**Use Cases:**
- Already ran MUMmer alignment via other methods
- Need to convert SNP data to standard VCF format
- Integration with other VCF analysis tools

### Complete Analysis Pipeline Example

Complete workflow from FASTQ raw data to variant annotation:

```python
from mtbdb.tbva import fastq_to_vcf, VCFParser, VariantAnnotator

# Step 1: Generate VCF (using built-in H37Rv reference)
vcf_file = fastq_to_vcf(
    output_dir='analysis',
    sample_name='sample001',
    fastq1='sample001_R1.fastq',
    fastq2='sample001_R2.fastq',
    threads=16
)

# Step 2: Parse VCF
parser = VCFParser(vcf_file)
snps = parser.get_snps()
print(f"Detected {len(snps)} SNP variants")

# Step 3: Variant annotation
annotator = VariantAnnotator(vcf_file)
results = annotator.annotate()
```

### Configure Reference Genome and Tool Paths

```python
from mtbdb.tbva import set_reference_fasta, set_tool_path

# Set default reference genome
set_reference_fasta('/path/to/H37Rv_complete_genome.fa')

# Set external tool paths (if not in system PATH)
set_tool_path('bwa', '/usr/local/bin/bwa')
set_tool_path('samtools', '/usr/local/bin/samtools')
set_tool_path('nucmer', '/opt/mummer/bin/nucmer')
```

Or configure via environment variables:

```bash
export MTBDB_REFERENCE_FASTA=/path/to/H37Rv.fa
export MTBDB_BWA_PATH=/usr/local/bin/bwa
export MTBDB_SAMTOOLS_PATH=/usr/local/bin/samtools
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) file for details.

## Author

HengyuZhou (zhouhengyu23@mails.ucas.ac.cn)

## Homepage

https://github.com/16627517673/mtbdb
