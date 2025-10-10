"""
FASTQ to VCF Converter using Varscan Pipeline
基于NGS分析工具链将FASTQ测序数据转换为VCF格式
"""
import subprocess
import os
import shutil
from pathlib import Path
import logging
from .dependency_checker import check_fastq_dependencies
from .config import get_default_reference_fasta


class FastqToVcfConverter:
    """
    使用标准NGS分析流程将FASTQ测序数据转换为VCF格式

    工作流程：
    1. fastq-dump: 解压SRA格式（可选）
    2. fastp: 质量控制和过滤
    3. BWA mem: 短reads比对到参考基因组
    4. samtools view: SAM转BAM
    5. samtools sort: 排序BAM文件
    6. samtools index: 创建索引
    7. samtools mpileup: 生成pileup文件
    8. varscan mpileup2snp: 变异检测生成VCF
    """

    def __init__(self,
                 reference_fasta,
                 output_dir,
                 sample_name,
                 fastq1=None,
                 fastq2=None,
                 sra_file=None,
                 threads=8,
                 cleanup_intermediate=True,
                 check_dependencies=True):
        """
        初始化FASTQ到VCF转换器

        Args:
            reference_fasta: 参考基因组FASTA文件路径（需要有.fai索引）
            output_dir: 输出目录路径
            sample_name: 样本名称（用于命名输出文件）
            fastq1: FASTQ R1文件路径（与sra_file二选一）
            fastq2: FASTQ R2文件路径（双端测序时必需）
            sra_file: SRA文件路径（与fastq1/fastq2二选一）
            threads: 使用的线程数
            cleanup_intermediate: 是否清理中间文件
            check_dependencies: 是否在初始化时检查依赖工具（默认True）
        """
        if not fastq1 and not sra_file:
            raise ValueError("必须提供fastq1或sra_file之一")

        # 设置日志（提前设置，以便依赖检查可以使用）
        self.logger = logging.getLogger(__name__)

        # 检查依赖工具
        if check_dependencies:
            try:
                check_fastq_dependencies(raise_error=True)
                self.logger.info("依赖检查通过：所有必需工具均已安装")
            except Exception as e:
                self.logger.error(f"依赖检查失败: {e}")
                raise

        self.reference_fasta = Path(reference_fasta)
        self.reference_fasta_fai = self.reference_fasta.with_suffix('.fa.fai')
        self.output_dir = Path(output_dir) / sample_name
        self.sample_name = sample_name
        self.fastq1 = Path(fastq1) if fastq1 else None
        self.fastq2 = Path(fastq2) if fastq2 else None
        self.sra_file = Path(sra_file) if sra_file else None
        self.threads = threads
        self.cleanup_intermediate = cleanup_intermediate

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 子目录
        self.raw_data_dir = self.output_dir / "1.raw_data"
        self.fastp_dir = self.output_dir / "2.fastp"
        self.bwa_dir = self.output_dir / "3.bwa_mem"
        self.view_dir = self.output_dir / "4.samtools_view"
        self.sort_dir = self.output_dir / "5.samtools_sort"
        self.mpileup_dir = self.output_dir / "6.samtools_mpileup"
        self.varscan_dir = self.output_dir / "7.varscan_snp"

        # 最终输出文件
        self.vcf_file = self.output_dir / f"{sample_name}.snp.vcf"
        self.log_file = self.output_dir / f"{sample_name}.pipeline.log"

        # 设置文件日志
        self._setup_file_logger()

    def _setup_file_logger(self):
        """设置文件日志记录器"""
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _run_command(self, cmd, description):
        """
        执行shell命令并处理错误

        Args:
            cmd: 命令字符串
            description: 命令描述（用于日志）
        """
        self.logger.info(f"执行: {description}")
        self.logger.info(f"命令: {cmd}")

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            error_msg = f"{description}失败:\n{result.stderr}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        if result.stdout:
            self.logger.debug(result.stdout)

        return result.stdout

    def _make_subdir(self, subdir_path):
        """创建子目录"""
        subdir_path.mkdir(parents=True, exist_ok=True)
        return subdir_path

    def step1_fastq_dump(self):
        """步骤1：从SRA文件提取FASTQ（如果需要）"""
        if not self.sra_file:
            self.logger.info("跳过fastq-dump步骤（已提供FASTQ文件）")
            return

        self._make_subdir(self.raw_data_dir)
        cmd = f"fastq-dump --split-files {self.sra_file} -O {self.raw_data_dir}"
        self._run_command(cmd, "fastq-dump解压SRA文件")

        # 更新FASTQ文件路径
        self.fastq1 = self.raw_data_dir / f"{self.sample_name}_1.fastq"
        self.fastq2 = self.raw_data_dir / f"{self.sample_name}_2.fastq"

    def step2_fastp(self):
        """步骤2：使用fastp进行质量控制"""
        self._make_subdir(self.fastp_dir)

        output_file1 = self.fastp_dir / f"{self.sample_name}_1.qc.fasta"
        output_file2 = self.fastp_dir / f"{self.sample_name}_2.qc.fasta" if self.fastq2 else None
        html_report = self.fastp_dir / f"{self.sample_name}.html"
        json_report = self.fastp_dir / f"{self.sample_name}.json"

        if self.fastq2:
            cmd = (f"fastp --thread {self.threads} "
                   f"-i {self.fastq1} -I {self.fastq2} "
                   f"-o {output_file1} -O {output_file2} "
                   f"-h {html_report} -j {json_report}")
        else:
            cmd = (f"fastp --thread {self.threads} "
                   f"-i {self.fastq1} -o {output_file1} "
                   f"-h {html_report} -j {json_report}")

        self._run_command(cmd, "fastp质量控制")

        # 保存JSON报告到主目录
        shutil.copy(json_report, self.output_dir / f"{self.sample_name}.json")

        # 更新FASTQ路径为QC后的文件
        self.fastq1 = output_file1
        self.fastq2 = output_file2

    def step3_bwa_mem(self):
        """步骤3：使用BWA mem进行比对"""
        self._make_subdir(self.bwa_dir)

        output_sam = self.bwa_dir / f"{self.sample_name}.paired.sam"

        if self.fastq2:
            cmd = (f"bwa mem -t {self.threads} "
                   f"-R '@RG\\tID:{self.sample_name}\\tSM:{self.sample_name}\\tPL:illumina' "
                   f"-M {self.reference_fasta} {self.fastq1} {self.fastq2} > {output_sam}")
        else:
            cmd = (f"bwa mem -t {self.threads} "
                   f"-R '@RG\\tID:{self.sample_name}\\tSM:{self.sample_name}\\tPL:illumina' "
                   f"-M {self.reference_fasta} {self.fastq1} > {output_sam}")

        self._run_command(cmd, "BWA mem比对")

    def step4_samtools_view(self):
        """步骤4：SAM转BAM"""
        self._make_subdir(self.view_dir)

        input_sam = self.bwa_dir / f"{self.sample_name}.paired.sam"
        output_bam = self.view_dir / f"{self.sample_name}.paired.bam"

        cmd = (f"samtools view --threads {self.threads} "
               f"-bhSt {self.reference_fasta_fai} {input_sam} -o {output_bam}")

        self._run_command(cmd, "samtools view转换SAM为BAM")

    def step5_samtools_sort(self):
        """步骤5：排序BAM文件"""
        self._make_subdir(self.sort_dir)

        input_bam = self.view_dir / f"{self.sample_name}.paired.bam"
        output_bam = self.sort_dir / f"{self.sample_name}.sort.bam"

        cmd = f"samtools sort --threads {self.threads} {input_bam} -o {output_bam}"
        self._run_command(cmd, "samtools sort排序BAM文件")

    def step6_samtools_index(self):
        """步骤6：创建BAM索引"""
        input_bam = self.sort_dir / f"{self.sample_name}.sort.bam"
        cmd = f"samtools index -@ {self.threads} {input_bam}"
        self._run_command(cmd, "samtools index创建索引")

    def step7_samtools_mpileup(self):
        """步骤7：生成mpileup文件"""
        self._make_subdir(self.mpileup_dir)

        input_bam = self.sort_dir / f"{self.sample_name}.sort.bam"
        output_pileup = self.mpileup_dir / f"{self.sample_name}.pileup"

        cmd = (f"samtools mpileup -q 30 -Q 20 -B "
               f"-f {self.reference_fasta} {input_bam} > {output_pileup}")

        self._run_command(cmd, "samtools mpileup生成pileup文件")

    def step8_varscan_snp(self):
        """步骤8：使用Varscan检测变异"""
        self._make_subdir(self.varscan_dir)

        input_pileup = self.mpileup_dir / f"{self.sample_name}.pileup"
        output_vcf = self.varscan_dir / f"{self.sample_name}.snp.vcf"

        cmd = (f"varscan mpileup2snp {input_pileup} --output-vcf "
               f"--min-coverage 3 --min-reads2 2 --min-avg-qual 20 "
               f"--min-var-freq 0.01 --min-freq-for-hom 0.9 "
               f"--p-value 99e-02 --strand-filter 0 > {output_vcf}")

        self._run_command(cmd, "varscan检测SNP变异")

        # 复制VCF到主目录
        shutil.copy(output_vcf, self.vcf_file)

    def cleanup(self):
        """清理中间文件"""
        if self.cleanup_intermediate:
            self.logger.info("清理中间文件夹")
            dirs_to_remove = [
                self.raw_data_dir,
                self.fastp_dir,
                self.bwa_dir,
                self.view_dir,
                self.mpileup_dir,
                self.varscan_dir
            ]

            for dir_path in dirs_to_remove:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    self.logger.info(f"已删除: {dir_path}")

    def convert(self):
        """
        执行完整的FASTQ到VCF转换流程

        Returns:
            Path: 生成的VCF文件路径
        """
        try:
            self.logger.info(f"开始FASTQ到VCF转换流程 - 样本: {self.sample_name}")

            # 执行各步骤
            self.step1_fastq_dump()
            self.step2_fastp()
            self.step3_bwa_mem()
            self.step4_samtools_view()
            self.step5_samtools_sort()
            self.step6_samtools_index()
            self.step7_samtools_mpileup()
            self.step8_varscan_snp()

            # 清理中间文件
            if self.cleanup_intermediate:
                self.cleanup()

            self.logger.info(f"FASTQ到VCF转换完成: {self.vcf_file}")
            return self.vcf_file

        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            raise


def fastq_to_vcf(output_dir,
                 sample_name,
                 fastq1=None,
                 fastq2=None,
                 sra_file=None,
                 reference_fasta=None,
                 threads=8,
                 cleanup_intermediate=True):
    """
    便捷函数：将FASTQ文件转换为VCF

    Args:
        output_dir: 输出目录路径
        sample_name: 样本名称
        fastq1: FASTQ R1文件路径（与sra_file二选一）
        fastq2: FASTQ R2文件路径（双端测序时必需）
        sra_file: SRA文件路径（与fastq1/fastq2二选一）
        reference_fasta: 参考基因组FASTA文件路径（可选，默认使用包内置H37Rv）
        threads: 使用的线程数
        cleanup_intermediate: 是否清理中间文件

    Returns:
        Path: 生成的VCF文件路径

    Example:
        >>> from mtbdb.tbva import fastq_to_vcf
        >>> # 使用默认H37Rv参考
        >>> vcf = fastq_to_vcf('output', 'sample001', fastq1='R1.fq', fastq2='R2.fq')
        >>> # 使用自定义参考
        >>> vcf = fastq_to_vcf('output', 'sample001', fastq1='R1.fq', fastq2='R2.fq',
        ...                    reference_fasta='custom_ref.fa')
    """
    # 如果未提供参考基因组，使用默认的H37Rv
    if reference_fasta is None:
        reference_fasta = get_default_reference_fasta()
        if reference_fasta is None:
            raise ValueError(
                "未找到默认参考基因组。请通过 reference_fasta 参数指定参考基因组路径，"
                "或确保 MtbDb 包含参考基因组数据文件。"
            )

    converter = FastqToVcfConverter(
        reference_fasta=reference_fasta,
        output_dir=output_dir,
        sample_name=sample_name,
        fastq1=fastq1,
        fastq2=fastq2,
        sra_file=sra_file,
        threads=threads,
        cleanup_intermediate=cleanup_intermediate
    )

    return converter.convert()
