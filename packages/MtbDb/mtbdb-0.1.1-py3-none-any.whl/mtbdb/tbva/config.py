import json
import os
from pathlib import Path
from mtbdb import DATA_DIR


def load_genes():
    genes_file = DATA_DIR / 'genes.json'
    with genes_file.open('r') as f:
        return json.load(f)


def load_lineage_info():
    lineage_info_file = DATA_DIR / 'lineage_info.json'
    with lineage_info_file.open('r') as f:
        return json.load(f)


def load_domains():
    domains_file = DATA_DIR / 'domains.json'
    with domains_file.open('r') as f:
        return json.load(f)


def load_epitopes():
    epitopes_file = DATA_DIR / 'epitopes.json'
    with epitopes_file.open('r') as f:
        return json.load(f)


# 加载数据文件
genes = load_genes()
lineage_info = load_lineage_info()
domains = load_domains()
epitopes = load_epitopes()


# ===== 参考基因组配置 =====
# H37Rv参考基因组相关配置
DEFAULT_REFERENCE_FASTA = None  # 用户需要自行配置
DEFAULT_CHROM_ID = "NC_000962.3"  # H37Rv染色体ID


def set_reference_fasta(fasta_path):
    """
    设置默认参考基因组路径

    Args:
        fasta_path: 参考基因组FASTA文件路径
    """
    global DEFAULT_REFERENCE_FASTA
    DEFAULT_REFERENCE_FASTA = Path(fasta_path)


def get_reference_fasta():
    """
    获取默认参考基因组路径

    Returns:
        Path or None: 参考基因组路径
    """
    if DEFAULT_REFERENCE_FASTA:
        return DEFAULT_REFERENCE_FASTA

    # 尝试从环境变量读取
    env_ref = os.environ.get('MTBDB_REFERENCE_FASTA')
    if env_ref:
        return Path(env_ref)

    return None


def get_default_reference_fasta():
    """
    获取包内置的默认H37Rv参考基因组路径

    该函数会自动定位包内附带的H37Rv参考基因组文件。
    如果找不到，返回None。

    Returns:
        str or None: 参考基因组的绝对路径字符串，如果未找到则返回None

    Example:
        >>> from mtbdb.tbva import get_default_reference_fasta
        >>> ref = get_default_reference_fasta()
        >>> print(f"默认参考基因组: {ref}")
    """
    # 包内参考基因组位置：src/mtbdb/data/reference/
    package_ref = Path(__file__).parent.parent / "data" / "reference" / "H37Rv_complete_genome.fa"

    if package_ref.exists():
        return str(package_ref.resolve())

    # 如果包内未找到，尝试项目根目录（开发模式/向后兼容）
    project_ref = Path(__file__).parent.parent.parent.parent / "data" / "reference" / "H37Rv_complete_genome.fa"
    if project_ref.exists():
        return str(project_ref.resolve())

    return None


# ===== 外部工具路径配置 =====
# 用户可以通过环境变量或直接设置来配置工具路径
# 如果不设置，将使用系统PATH中的工具

TOOL_PATHS = {
    # MUMmer工具链
    'nucmer': os.environ.get('MTBDB_NUCMER_PATH', 'nucmer'),
    'delta_filter': os.environ.get('MTBDB_DELTA_FILTER_PATH', 'delta-filter'),
    'show_snps': os.environ.get('MTBDB_SHOW_SNPS_PATH', 'show-snps'),

    # NGS分析工具链
    'fastq_dump': os.environ.get('MTBDB_FASTQ_DUMP_PATH', 'fastq-dump'),
    'fastp': os.environ.get('MTBDB_FASTP_PATH', 'fastp'),
    'bwa': os.environ.get('MTBDB_BWA_PATH', 'bwa'),
    'samtools': os.environ.get('MTBDB_SAMTOOLS_PATH', 'samtools'),
    'varscan': os.environ.get('MTBDB_VARSCAN_PATH', 'varscan'),
}


def set_tool_path(tool_name, path):
    """
    设置外部工具的路径

    Args:
        tool_name: 工具名称（如'nucmer', 'bwa'等）
        path: 工具的可执行文件路径
    """
    if tool_name in TOOL_PATHS:
        TOOL_PATHS[tool_name] = path
    else:
        raise ValueError(f"未知的工具名称: {tool_name}")


def get_tool_path(tool_name):
    """
    获取外部工具的路径

    Args:
        tool_name: 工具名称

    Returns:
        str: 工具路径
    """
    return TOOL_PATHS.get(tool_name, tool_name)
