# H37Rv参考基因组

本目录包含结核分枝杆菌（Mycobacterium tuberculosis）标准参考株H37Rv的完整基因组序列。

## 文件说明

- `H37Rv_complete_genome.fa` - 参考基因组FASTA文件（4.3MB）
- `H37Rv_complete_genome.fa.amb` - BWA索引文件（ambiguous bases）
- `H37Rv_complete_genome.fa.ann` - BWA索引文件（annotation）
- `H37Rv_complete_genome.fa.bwt` - BWA索引文件（Burrows-Wheeler Transform）
- `H37Rv_complete_genome.fa.fai` - samtools faidx索引文件
- `H37Rv_complete_genome.fa.pac` - BWA索引文件（packed sequences）
- `H37Rv_complete_genome.fa.sa` - BWA索引文件（suffix array）

## 基因组信息

- **菌株**: Mycobacterium tuberculosis H37Rv
- **GenBank ID**: NC_000962.3
- **基因组大小**: 4,411,532 bp
- **GC含量**: 65.6%
- **编码基因数**: ~4,000

## 自动安装

这些文件会随MtbDb包一起安装，用户无需手动下载。

## 使用方式

### 默认使用（推荐）

```python
from mtbdb.tbva import fasta_to_vcf, fastq_to_vcf

# ✅ 自动使用包内参考基因组
vcf1 = fasta_to_vcf(
    query_fasta='sample.fa',
    output_vcf='output.vcf'
)

vcf2 = fastq_to_vcf(
    output_dir='output',
    sample_name='sample001',
    fastq1='R1.fastq.gz',
    fastq2='R2.fastq.gz'
)
```

### 获取参考基因组路径

```python
from mtbdb.tbva import get_default_reference_fasta

ref_path = get_default_reference_fasta()
print(f"参考基因组路径: {ref_path}")
```

### 使用自定义参考基因组

```python
# ✅ 指定自定义参考基因组
vcf = fasta_to_vcf(
    reference_fasta='/path/to/custom_reference.fa',
    query_fasta='sample.fa',
    output_vcf='output.vcf'
)
```

## 索引文件重新生成

如果索引文件损坏或需要重新生成：

```bash
# 进入参考基因组目录
cd $(python -c "from mtbdb.tbva import get_default_reference_fasta; import os; print(os.path.dirname(get_default_reference_fasta()))")

# 生成BWA索引
bwa index H37Rv_complete_genome.fa

# 生成samtools索引
samtools faidx H37Rv_complete_genome.fa
```

## 数据来源

H37Rv参考基因组来自NCBI GenBank数据库：
- https://www.ncbi.nlm.nih.gov/nuccore/NC_000962.3

## 许可证

参考基因组数据来自公共数据库，遵循相应的数据使用协议。
