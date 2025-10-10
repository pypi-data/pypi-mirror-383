"""
SNP to VCF Converter
将MUMmer show-snps输出文件转换为标准VCF格式
"""
from pathlib import Path
import logging
from datetime import datetime


class SnpToVcfConverter:
    """
    将MUMmer show-snps输出文件转换为VCF格式

    适用场景：
    - 已有MUMmer show-snps工具生成的SNP文件
    - 需要将SNP数据转换为标准VCF格式用于下游分析
    - 无需重新运行全基因组比对

    输入格式：
    - MUMmer show-snps的输出文件（-T选项生成的tab分隔格式）

    输出格式：
    - 标准VCF v4.2格式文件
    """

    def __init__(self,
                 snp_file,
                 output_vcf,
                 chrom_id="NC_000962.3",
                 reference_name=None,
                 filter_indels=True):
        """
        初始化SNP到VCF转换器

        Args:
            snp_file: MUMmer show-snps输出文件路径
            output_vcf: 输出VCF文件路径
            chrom_id: 染色体ID（默认为H37Rv的NC_000962.3）
            reference_name: 参考基因组名称（用于VCF头部，可选）
            filter_indels: 是否过滤indel，仅保留SNP（默认True）
        """
        self.snp_file = Path(snp_file)
        self.output_vcf = Path(output_vcf)
        self.chrom_id = chrom_id
        self.reference_name = reference_name or self.snp_file.stem
        self.filter_indels = filter_indels

        # 设置日志
        self.logger = logging.getLogger(__name__)

        # 验证输入文件
        if not self.snp_file.exists():
            raise FileNotFoundError(f"SNP文件不存在: {self.snp_file}")

    def _parse_snp_line(self, line):
        """
        解析单行SNP数据

        Args:
            line: SNP文件的一行数据

        Returns:
            dict: 包含解析后的SNP信息，如果解析失败则返回None
        """
        fields = line.strip().split()

        # 检查字段数量（show-snps -T格式至少需要12列）
        if len(fields) < 12:
            return None

        try:
            snp_data = {
                'pos': fields[0],
                'ref': fields[1],
                'alt': fields[2],
                'buff': fields[5],
                'dist': fields[6],
                'len_r': fields[8],
                'len_q': fields[9],
                'frm1': fields[10],
                'frm2': fields[11]
            }
            return snp_data
        except (IndexError, ValueError) as e:
            self.logger.warning(f"解析SNP行失败: {line.strip()} - {e}")
            return None

    def _is_snp(self, ref, alt):
        """
        判断是否为SNP（单核苷酸多态性）

        Args:
            ref: 参考碱基
            alt: 替代碱基

        Returns:
            bool: 如果是单碱基替换则返回True
        """
        return (ref != '.' and
                alt != '.' and
                len(ref) == 1 and
                len(alt) == 1)

    def _write_vcf_header(self, outfile):
        """
        写入VCF格式头部

        Args:
            outfile: 输出文件对象
        """
        # VCF版本
        outfile.write("##fileformat=VCFv4.2\n")

        # 文件生成日期
        date_str = datetime.now().strftime("%Y%m%d")
        outfile.write(f"##fileDate={date_str}\n")

        # 来源信息
        outfile.write("##source=MtbDb-SnpToVcfConverter\n")
        outfile.write(f"##reference={self.reference_name}\n")

        # INFO字段定义
        outfile.write("##INFO=<ID=BUFF,Number=1,Type=Integer,Description=\"Distance from query to nearest mismatch\">\n")
        outfile.write("##INFO=<ID=DIST,Number=1,Type=Integer,Description=\"Distance to nearest feature\">\n")
        outfile.write("##INFO=<ID=LEN_R,Number=1,Type=Integer,Description=\"Length of reference sequence\">\n")
        outfile.write("##INFO=<ID=LEN_Q,Number=1,Type=Integer,Description=\"Length of query sequence\">\n")
        outfile.write("##INFO=<ID=FRM,Number=2,Type=String,Description=\"Frame information (reference,query)\">\n")

        # 列标题
        outfile.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")

    def _write_vcf_body(self, outfile):
        """
        写入VCF数据行

        Args:
            outfile: 输出文件对象

        Returns:
            tuple: (总SNP数, 写入的SNP数, 过滤的indel数)
        """
        total_snps = 0
        written_snps = 0
        filtered_indels = 0

        with open(self.snp_file, 'r') as infile:
            # 跳过头部行，找到第一个完整数据行
            for line in infile:
                snp_data = self._parse_snp_line(line)
                if snp_data:
                    # 找到第一个有效数据行后退出循环
                    break

            # 如果没有找到有效数据行，直接返回
            if not snp_data:
                self.logger.warning("未找到有效的SNP数据行")
                return (0, 0, 0)

            # 处理找到的第一行以及后续所有数据行
            while True:
                if snp_data:
                    total_snps += 1

                    ref = snp_data['ref']
                    alt = snp_data['alt']

                    # 判断是否为SNP
                    if self._is_snp(ref, alt):
                        # 构建VCF行
                        id_field = "."
                        qual = "."
                        filter_field = "PASS"
                        info = (f"BUFF={snp_data['buff']};"
                               f"DIST={snp_data['dist']};"
                               f"LEN_R={snp_data['len_r']};"
                               f"LEN_Q={snp_data['len_q']};"
                               f"FRM={snp_data['frm1']},{snp_data['frm2']}")

                        vcf_line = (f"{self.chrom_id}\t{snp_data['pos']}\t{id_field}\t"
                                   f"{ref}\t{alt}\t{qual}\t{filter_field}\t{info}\n")
                        outfile.write(vcf_line)
                        written_snps += 1
                    elif self.filter_indels:
                        filtered_indels += 1

                # 读取下一行
                try:
                    line = next(infile)
                    snp_data = self._parse_snp_line(line)
                except StopIteration:
                    break

        return (total_snps, written_snps, filtered_indels)

    def convert(self):
        """
        执行SNP到VCF的转换

        Returns:
            Path: 生成的VCF文件路径
        """
        try:
            self.logger.info("开始SNP到VCF转换")
            self.logger.info(f"输入文件: {self.snp_file}")
            self.logger.info(f"输出VCF: {self.output_vcf}")
            self.logger.info(f"染色体ID: {self.chrom_id}")

            # 创建输出目录
            self.output_vcf.parent.mkdir(parents=True, exist_ok=True)

            # 写入VCF文件
            with open(self.output_vcf, 'w') as outfile:
                # 写入头部
                self._write_vcf_header(outfile)

                # 写入数据
                total, written, filtered = self._write_vcf_body(outfile)

            # 输出统计信息
            self.logger.info(f"转换完成:")
            self.logger.info(f"  总变异位点: {total}")
            self.logger.info(f"  写入SNP: {written}")
            if self.filter_indels and filtered > 0:
                self.logger.info(f"  过滤indel: {filtered}")
            self.logger.info(f"VCF文件已生成: {self.output_vcf}")

            return self.output_vcf

        except Exception as e:
            self.logger.error(f"转换过程中发生错误: {e}")
            raise


def snp_to_vcf(snp_file,
               output_vcf,
               chrom_id="NC_000962.3",
               reference_name=None,
               filter_indels=True):
    """
    便捷函数：将MUMmer SNP文件转换为VCF格式

    这是一个快捷方式，用于简单场景。如需更多控制，请使用SnpToVcfConverter类。

    Args:
        snp_file: MUMmer show-snps输出文件路径
        output_vcf: 输出VCF文件路径
        chrom_id: 染色体ID（默认为H37Rv的NC_000962.3）
        reference_name: 参考基因组名称（可选）
        filter_indels: 是否过滤indel，仅保留SNP（默认True）

    Returns:
        Path: 生成的VCF文件路径

    Example:
        >>> from mtbdb.tbva import snp_to_vcf
        >>> vcf_file = snp_to_vcf('sample.snps', 'sample.vcf')
        >>> print(f"VCF文件已生成: {vcf_file}")
    """
    converter = SnpToVcfConverter(
        snp_file=snp_file,
        output_vcf=output_vcf,
        chrom_id=chrom_id,
        reference_name=reference_name,
        filter_indels=filter_indels
    )

    return converter.convert()
