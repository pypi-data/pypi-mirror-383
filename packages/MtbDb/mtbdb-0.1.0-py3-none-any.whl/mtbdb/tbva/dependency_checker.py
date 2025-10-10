"""
依赖检查模块
检查外部生物信息学工具是否已正确安装
"""
import shutil
import subprocess
from typing import List, Dict, Optional


class DependencyError(Exception):
    """依赖缺失错误"""
    pass


def check_tool_installed(tool_name: str) -> bool:
    """
    检查工具是否已安装并可用

    Args:
        tool_name: 工具名称

    Returns:
        bool: True表示工具可用，False表示不可用
    """
    return shutil.which(tool_name) is not None


def get_tool_version(tool_name: str) -> Optional[str]:
    """
    获取工具版本号

    Args:
        tool_name: 工具名称

    Returns:
        str or None: 版本号字符串，如果无法获取则返回None
    """
    try:
        # 尝试常见的版本查询命令
        for version_flag in ['--version', '-version', '-v', 'version']:
            try:
                result = subprocess.run(
                    [tool_name, version_flag],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # 返回第一行输出
                    return result.stdout.split('\n')[0].strip()
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
    except Exception:
        pass
    return None


def check_fasta_dependencies(raise_error: bool = True) -> Dict[str, bool]:
    """
    检查FASTA转VCF所需的外部工具

    Args:
        raise_error: 如果为True，发现缺失工具时抛出异常

    Returns:
        dict: 工具名称到可用性的映射 {'tool_name': True/False}

    Raises:
        DependencyError: 当raise_error=True且存在缺失工具时
    """
    required_tools = {
        'nucmer': 'MUMmer工具 - 全基因组比对',
        'delta-filter': 'MUMmer工具 - 过滤比对结果',
        'show-snps': 'MUMmer工具 - 提取SNP位点',
    }

    results = {}
    missing = []

    for tool, description in required_tools.items():
        is_installed = check_tool_installed(tool)
        results[tool] = is_installed
        if not is_installed:
            missing.append(f"  - {tool}: {description}")

    if missing and raise_error:
        error_msg = (
            "FASTA转VCF功能需要以下外部工具，但未检测到：\n"
            + "\n".join(missing) +
            "\n\n请使用以下方式安装：\n"
            "  Conda (推荐):\n"
            "    conda install -c bioconda mummer\n"
            "  或使用完整环境配置:\n"
            "    conda env create -f environment.yml\n"
            "    conda activate mtbdb\n"
            "\n  Homebrew (macOS):\n"
            "    brew install brewsci/bio/mummer\n"
            "\n  或参考MUMmer官方文档进行源码安装:\n"
            "    http://mummer.sourceforge.net/"
        )
        raise DependencyError(error_msg)

    return results


def check_fastq_dependencies(raise_error: bool = True) -> Dict[str, bool]:
    """
    检查FASTQ转VCF所需的外部工具

    Args:
        raise_error: 如果为True，发现缺失工具时抛出异常

    Returns:
        dict: 工具名称到可用性的映射 {'tool_name': True/False}

    Raises:
        DependencyError: 当raise_error=True且存在缺失工具时
    """
    required_tools = {
        'bwa': 'BWA - 短reads比对工具',
        'samtools': 'samtools - SAM/BAM文件处理',
        'varscan': 'VarScan - 变异检测工具',
        'fastp': 'fastp - 质量控制工具',
    }

    optional_tools = {
        'fastq-dump': 'SRA Toolkit - SRA文件解压 (可选)',
    }

    results = {}
    missing = []

    # 检查必需工具
    for tool, description in required_tools.items():
        is_installed = check_tool_installed(tool)
        results[tool] = is_installed
        if not is_installed:
            missing.append(f"  - {tool}: {description}")

    # 检查可选工具（不计入缺失）
    for tool, description in optional_tools.items():
        results[tool] = check_tool_installed(tool)

    if missing and raise_error:
        error_msg = (
            "FASTQ转VCF功能需要以下外部工具，但未检测到：\n"
            + "\n".join(missing) +
            "\n\n请使用以下方式安装：\n"
            "  Conda (推荐):\n"
            "    conda install -c bioconda bwa samtools varscan fastp\n"
            "  或使用完整环境配置:\n"
            "    conda env create -f environment.yml\n"
            "    conda activate mtbdb\n"
            "\n  Homebrew (macOS):\n"
            "    brew install bwa samtools fastp\n"
            "    # varscan需要单独下载JAR文件\n"
            "\n  或参考各工具的官方文档进行安装"
        )
        raise DependencyError(error_msg)

    return results


def check_all_dependencies(verbose: bool = True) -> Dict[str, Dict[str, bool]]:
    """
    检查所有外部工具依赖

    Args:
        verbose: 是否打印详细信息

    Returns:
        dict: 包含所有工具检查结果的字典
    """
    print("正在检查MtbDb外部工具依赖...\n")

    # 检查FASTA转换工具
    print("【FASTA转VCF工具】")
    fasta_tools = check_fasta_dependencies(raise_error=False)
    for tool, is_installed in fasta_tools.items():
        status = "✓ 已安装" if is_installed else "✗ 未安装"
        version = get_tool_version(tool) if is_installed else ""
        print(f"  {tool}: {status} {version}")

    print("\n【FASTQ转VCF工具】")
    fastq_tools = check_fastq_dependencies(raise_error=False)
    for tool, is_installed in fastq_tools.items():
        status = "✓ 已安装" if is_installed else "✗ 未安装"
        version = get_tool_version(tool) if is_installed else ""
        optional = " (可选)" if tool == "fastq-dump" else ""
        print(f"  {tool}: {status} {version}{optional}")

    # 统计结果
    all_tools = {**fasta_tools, **fastq_tools}
    installed_count = sum(all_tools.values())
    # fastq-dump是可选的，不计入总数
    total_count = len(all_tools) - 1

    print(f"\n总结: {installed_count}/{total_count+1} 工具可用")

    if installed_count < total_count:
        print("\n⚠️  存在缺失的必需工具，请使用以下命令安装：")
        print("  conda env create -f environment.yml")
        print("  conda activate mtbdb")
    else:
        print("\n✓ 所有必需工具均已正确安装！")

    return {
        'fasta_tools': fasta_tools,
        'fastq_tools': fastq_tools,
    }


def print_installation_guide():
    """打印详细的安装指南"""
    guide = """
================================================================================
MtbDb 外部工具安装指南
================================================================================

MtbDb的FASTA/FASTQ转VCF功能依赖以下生物信息学工具：

【方案1：使用Conda安装（强烈推荐）】
-----------------------------------------
Conda可以自动处理所有依赖关系，这是最简单的安装方式。

1. 使用环境配置文件（推荐）:
   conda env create -f environment.yml
   conda activate mtbdb

2. 或手动安装各工具:
   conda install -c bioconda mummer bwa samtools varscan fastp sra-tools

【方案2：使用Homebrew安装（macOS）】
-----------------------------------------
brew install brewsci/bio/mummer bwa samtools fastp

注意：varscan需要单独下载JAR文件
wget https://github.com/dkoboldt/varscan/raw/master/VarScan.v2.4.4.jar
# 然后配置CLASSPATH或创建wrapper脚本

【方案3：从源码编译】
-----------------------------------------
请参考各工具的官方文档：
- MUMmer: http://mummer.sourceforge.net/
- BWA: https://github.com/lh3/bwa
- samtools: http://www.htslib.org/
- fastp: https://github.com/OpenGene/fastp
- VarScan: http://varscan.sourceforge.net/

【验证安装】
-----------------------------------------
安装完成后，运行以下命令验证：
  python -c "from mtbdb.tbva import check_all_dependencies; check_all_dependencies()"

【常见问题】
-----------------------------------------
Q: 提示"command not found"怎么办？
A: 确保工具已添加到系统PATH，或使用set_tool_path()指定完整路径

Q: Conda安装很慢怎么办？
A: 可以使用mamba作为更快的替代品：
   conda install mamba -c conda-forge
   mamba env create -f environment.yml

================================================================================
"""
    print(guide)


if __name__ == '__main__':
    # 当直接运行此模块时，执行依赖检查
    check_all_dependencies()
    print("\n如需查看详细安装指南，请运行：")
    print("  python -c \"from mtbdb.tbva.dependency_checker import print_installation_guide; print_installation_guide()\"")
