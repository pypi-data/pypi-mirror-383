"""
FASTA to VCF Converter using MUMmer
基于MUMmer工具链将FASTA基因组序列比对并转换为VCF格式
"""
import subprocess
import os
from pathlib import Path
import logging
from .dependency_checker import check_fasta_dependencies
from .config import get_default_reference_fasta


class FastaToVcfConverter:
    """
    使用MUMmer工具链将FASTA基因组序列转换为VCF格式

    工作流程：
    1. nucmer: 全基因组比对
    2. delta-filter: 过滤比对结果
    3. show-snps: 提取SNP位点
    4. snp_to_vcf: 转换为VCF格式
    """

    def __init__(self,
                 reference_fasta,
                 query_fasta,
                 output_prefix,
                 chrom_id="NC_000962.3",
                 nucmer_path="nucmer",
                 delta_filter_path="delta-filter",
                 show_snps_path="show-snps",
                 cleanup_intermediate=True,
                 check_dependencies=True):
        """
        初始化FASTA到VCF转换器

        Args:
            reference_fasta: 参考基因组FASTA文件路径
            query_fasta: 查询基因组FASTA文件路径
            output_prefix: 输出文件前缀（包含路径）
            chrom_id: 染色体ID（默认为H37Rv的NC_000962.3）
            nucmer_path: nucmer可执行文件路径
            delta_filter_path: delta-filter可执行文件路径
            show_snps_path: show-snps可执行文件路径
            cleanup_intermediate: 是否清理中间文件
            check_dependencies: 是否在初始化时检查依赖工具（默认True）
        """
        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 检查依赖工具
        if check_dependencies:
            try:
                check_fasta_dependencies(raise_error=True)
                self.logger.info("依赖检查通过：所有必需工具均已安装")
            except Exception as e:
                self.logger.error(f"依赖检查失败: {e}")
                raise

        self.reference_fasta = Path(reference_fasta)
        self.query_fasta = Path(query_fasta)
        self.output_prefix = Path(output_prefix)
        self.chrom_id = chrom_id
        self.nucmer_path = nucmer_path
        self.delta_filter_path = delta_filter_path
        self.show_snps_path = show_snps_path
        self.cleanup_intermediate = cleanup_intermediate

        # 中间文件路径
        # 使用字符串拼接而不是with_suffix()，以正确处理多点文件名（如 GCF_020179105.1_genomic）
        self.delta_file = self.output_prefix.parent / (self.output_prefix.name + '.delta')
        self.filter_file = self.output_prefix.parent / (self.output_prefix.name + '.filter')
        self.snps_file = self.output_prefix.parent / (self.output_prefix.name + '.snps')
        self.vcf_file = self.output_prefix.parent / (self.output_prefix.name + '.vcf')

    def _run_command(self, cmd, description):
        """
        执行shell命令并处理错误

        Args:
            cmd: 命令列表或字符串
            description: 命令描述（用于日志）
        """
        self.logger.info(f"执行: {description}")
        self.logger.debug(f"命令: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str),
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_msg = f"{description}失败:\n{result.stderr}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        return result.stdout

    def run_nucmer(self):
        """运行nucmer进行全基因组比对"""
        cmd = [
            self.nucmer_path,
            '-p', str(self.output_prefix),
            str(self.reference_fasta),
            str(self.query_fasta)
        ]
        self._run_command(cmd, "nucmer全基因组比对")

        if not self.delta_file.exists():
            raise FileNotFoundError(f"nucmer未生成预期的输出文件: {self.delta_file}")

    def run_delta_filter(self):
        """运行delta-filter过滤比对结果"""
        cmd = f"{self.delta_filter_path} -r -q {self.delta_file} > {self.filter_file}"
        self._run_command(cmd, "delta-filter过滤比对结果")

        if not self.filter_file.exists():
            raise FileNotFoundError(f"delta-filter未生成预期的输出文件: {self.filter_file}")

    def run_show_snps(self):
        """运行show-snps提取SNP位点"""
        cmd = f"{self.show_snps_path} -Clr -T -I {self.filter_file} > {self.snps_file}"
        self._run_command(cmd, "show-snps提取SNP位点")

        if not self.snps_file.exists():
            raise FileNotFoundError(f"show-snps未生成预期的输出文件: {self.snps_file}")

    def convert_snps_to_vcf(self):
        """将MUMmer的SNPs文件转换为VCF格式"""
        self.logger.info("转换SNPs文件为VCF格式")

        try:
            with open(self.snps_file, 'r') as infile, open(self.vcf_file, 'w') as outfile:
                # 写入VCF头部
                outfile.write("##fileformat=VCFv4.2\n")
                outfile.write(f"##reference={self.reference_fasta.name}\n")
                outfile.write(f"##source=MUMmer-FastaToVcfConverter\n")
                outfile.write("##INFO=<ID=BUFF,Number=1,Type=Integer,Description=\"Distance from query to nearest mismatch\">\n")
                outfile.write("##INFO=<ID=DIST,Number=1,Type=Integer,Description=\"Distance to nearest feature\">\n")
                outfile.write("##INFO=<ID=LEN_R,Number=1,Type=Integer,Description=\"Length of reference sequence\">\n")
                outfile.write("##INFO=<ID=LEN_Q,Number=1,Type=Integer,Description=\"Length of query sequence\">\n")
                outfile.write("##INFO=<ID=FRM,Number=2,Type=String,Description=\"Frame information\">\n")
                outfile.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")

                # 跳过SNPs文件的头部行
                for line in infile:
                    fields = line.strip().split()
                    if len(fields) < 12:
                        continue  # 跳过不完整的行或头部
                    else:
                        # 找到第一个完整的数据行后，开始处理
                        break

                # 处理数据行
                for line in infile:
                    fields = line.strip().split()
                    if len(fields) < 12:
                        continue  # 跳过不完整的行

                    pos = fields[0]
                    ref = fields[1]
                    alt = fields[2]

                    # 只保留SNP（单碱基替换），过滤indel
                    if ref != '.' and alt != '.' and len(ref) == 1 and len(alt) == 1:
                        id_field = "."
                        qual = "."
                        filter_field = "PASS"

                        # 构建INFO字段
                        info = f"BUFF={fields[5]};DIST={fields[6]};LEN_R={fields[8]};LEN_Q={fields[9]};FRM={fields[10]},{fields[11]}"

                        # 写入VCF行
                        vcf_line = f"{self.chrom_id}\t{pos}\t{id_field}\t{ref}\t{alt}\t{qual}\t{filter_field}\t{info}\n"
                        outfile.write(vcf_line)

            self.logger.info(f"VCF文件已生成: {self.vcf_file}")

        except IOError as e:
            error_msg = f"文件IO错误: {e}"
            self.logger.error(error_msg)
            raise

    def cleanup(self):
        """清理中间文件"""
        if self.cleanup_intermediate:
            self.logger.info("清理中间文件")
            for file in [self.delta_file, self.filter_file, self.snps_file]:
                if file.exists():
                    file.unlink()
                    self.logger.debug(f"已删除: {file}")

    def convert(self):
        """
        执行完整的FASTA到VCF转换流程

        Returns:
            Path: 生成的VCF文件路径
        """
        try:
            self.logger.info("开始FASTA到VCF转换流程")

            # 创建输出目录
            self.output_prefix.parent.mkdir(parents=True, exist_ok=True)

            # 执行流程
            self.run_nucmer()
            self.run_delta_filter()
            self.run_show_snps()
            self.convert_snps_to_vcf()

            # 清理中间文件
            if self.cleanup_intermediate:
                self.cleanup()

            self.logger.info("FASTA到VCF转换完成")
            return self.vcf_file

        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            raise


def fasta_to_vcf(query_fasta,
                 output_vcf,
                 reference_fasta=None,
                 chrom_id="NC_000962.3",
                 cleanup_intermediate=True):
    """
    便捷函数：将FASTA文件转换为VCF

    Args:
        query_fasta: 查询基因组FASTA文件路径
        output_vcf: 输出VCF文件路径
        reference_fasta: 参考基因组FASTA文件路径（可选，默认使用包内置H37Rv）
        chrom_id: 染色体ID（默认为H37Rv的NC_000962.3）
        cleanup_intermediate: 是否清理中间文件

    Returns:
        Path: 生成的VCF文件路径

    Example:
        >>> from mtbdb.tbva import fasta_to_vcf
        >>> # 使用默认H37Rv参考
        >>> vcf = fasta_to_vcf('sample.fa', 'output.vcf')
        >>> # 使用自定义参考
        >>> vcf = fasta_to_vcf('sample.fa', 'output.vcf', reference_fasta='custom_ref.fa')
    """
    # 如果未提供参考基因组，使用默认的H37Rv
    if reference_fasta is None:
        reference_fasta = get_default_reference_fasta()
        if reference_fasta is None:
            raise ValueError(
                "未找到默认参考基因组。请通过 reference_fasta 参数指定参考基因组路径，"
                "或确保 MtbDb 包含参考基因组数据文件。"
            )

    # 从输出VCF路径提取前缀
    output_path = Path(output_vcf)
    output_prefix = output_path.parent / output_path.stem

    converter = FastaToVcfConverter(
        reference_fasta=reference_fasta,
        query_fasta=query_fasta,
        output_prefix=output_prefix,
        chrom_id=chrom_id,
        cleanup_intermediate=cleanup_intermediate
    )

    return converter.convert()
