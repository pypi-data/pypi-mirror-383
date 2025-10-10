import json
from typing import Set, Dict, List, Literal
from scipy.stats import hypergeom, fisher_exact
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from statsmodels.stats.multitest import multipletests
from .config import GOs, KEGG_pathways, TF_genes

class BaseEnrichmentAnalyzer:
    # 背景基因集合的大小
    number_of_gene_in_H37Rv = 4008

    def __init__(self, query_gene_set: Set[str]):
        # 用户输入的基因集
        self.query_gene_set = set(query_gene_set)

    def calculate_enrichment_statistics(self, AnnotatedBackgroudGeneSet: Set[str], N: int = number_of_gene_in_H37Rv) -> Dict[str, float]:
        X = len(self.query_gene_set) # Number of genes in the query gene set (通常是某条件下上调或下调的基因总数，或者某感兴趣的基因集。)
        Y = len(self.query_gene_set & AnnotatedBackgroudGeneSet) 
        # N = number_of_gene_in_H37Rv # 背景基因集合的大小
        M = len(AnnotatedBackgroudGeneSet) # Number of genes in the annotated gene set (通常是某个GO term或KEGG pathway中的注释到背景基因总数。)
        # 计算超几何检验的显著性（右尾累积概率）。
        p_value_hypergeom = hypergeom.sf(Y-1, N, M, X)
        # 构造 2×2 列联表 table 并用 fisher_exact 计算 Fisher 精确检验的 p 值与 odds ratio。
        table = [[Y, X - Y], [M - Y, N - M - (X - Y)]]
        odds_ratio, p_value_fisher = fisher_exact(table)
        # 计算期望值
        expected_value = X * M / N
        # 计算富集得分
        enrichment_score = (Y - expected_value) / np.sqrt(expected_value * (N - M) * (N - X) / (N**2))
        
        return {
            'hypergeometric_p_value': p_value_hypergeom,
            'fisher_exact_p_value': p_value_fisher,
            'fisher_exact_odds_ratio': odds_ratio,
            'expected_value': expected_value,
            'enrichment_score': enrichment_score
        }
    # 多重检验校正
    def correct_p_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=['hypergeometric_p_value', 'fisher_exact_p_value'])
        adjusted_p_values_hypergeom = multipletests(df['hypergeometric_p_value'], method='fdr_bh')[1]
        df.loc[:, 'hypergeometric_p_value_adj'] = adjusted_p_values_hypergeom
        adjusted_p_values_fisher = multipletests(df['fisher_exact_p_value'], method='fdr_bh')[1]
        df.loc[:, 'fisher_exact_p_value_adj'] = adjusted_p_values_fisher
        return df
    # 富集分析
    def EnrichmentAnalysis(self, AnnotatedGeneSets: Dict[str, List[str]]) -> pd.DataFrame:
        enrichmentStats = []
        # 计算富集统计量
        def process_set(ClusterId: str, AnnotatedBackgroudGeneSet: Set[str]):            
            enrichment = self.calculate_enrichment_statistics(AnnotatedBackgroudGeneSet)
            result = {"ClusterId": ClusterId, **enrichment}
            return result        
        # 多线程计算富集统计量
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_ClusterId = {executor.submit(process_set, ClusterId, set(genes)): ClusterId for ClusterId, genes in AnnotatedGeneSets.items()}
            for future in as_completed(future_to_ClusterId):
                try:
                    result = future.result()
                    enrichmentStats.append(result)
                except Exception as exc:
                    print(f'Generated an exception: {exc}')       
        enrichmentDF = pd.DataFrame(enrichmentStats)
        return enrichmentDF
    
    # 过滤富集结果
    def FilterClusters(self, df: pd.DataFrame, HypGeo_p_threshold: float = None, Fisher_p_threshold: float = None) -> pd.DataFrame:
        # 根据p值过滤富集结果
        if HypGeo_p_threshold is not None:
            df = df[df['hypergeometric_p_value'] <= HypGeo_p_threshold]
        # 根据fisher检验p值过滤富集结果
        if Fisher_p_threshold is not None:
            df = df[df['fisher_exact_p_value'] <= Fisher_p_threshold]
        # 如果过滤后没有富集结果，则返回空数据框
        if df.shape[0] == 0:
            return df
        else:
            # 多重检验校正
            df = self.correct_p_values(df)
        # 根据p值过滤富集结果
        if HypGeo_p_threshold is not None:
            df = df[df['hypergeometric_p_value_adj'] <= HypGeo_p_threshold]
        
        if Fisher_p_threshold is not None:
            df = df[df['fisher_exact_p_value_adj'] <= Fisher_p_threshold]
        return df

class GOEnrichmentAnalyzer(BaseEnrichmentAnalyzer):
    GOdf = pd.DataFrame(GOs)
    def GOEnrichmentAnalysis(self, HypGeo_p_threshold: float = 0.05, Fisher_p_threshold: float = None) -> pd.DataFrame:
        AnnotatedGeneSets = self.GOdf.set_index('GO_id')['Annotated_Genes'].to_dict()
        EnrichedGO = self.EnrichmentAnalysis(AnnotatedGeneSets)
        EnrichedGO = self.FilterClusters(EnrichedGO, HypGeo_p_threshold, Fisher_p_threshold)
        EnrichedGO = pd.merge(EnrichedGO, self.GOdf, left_on="ClusterId", right_on="GO_id", how="left")
        return EnrichedGO

class KEGGEnrichmentAnalyzer(BaseEnrichmentAnalyzer):
    KEGGdf = pd.DataFrame(KEGG_pathways)
    def KEGGEnrichmentAnalysis(self, HypGeo_p_threshold: float = 0.05, Fisher_p_threshold: float = None) -> pd.DataFrame:
        GeneSets = self.KEGGdf.set_index('pathway_id')['mtu_genes'].apply(json.loads).to_dict()
        EnrichedKEGG = self.EnrichmentAnalysis(GeneSets)
        EnrichedKEGG = self.FilterClusters(EnrichedKEGG, HypGeo_p_threshold, Fisher_p_threshold)
        EnrichedKEGG = pd.merge(EnrichedKEGG, self.KEGGdf, left_on="ClusterId", right_on="pathway_id", how="left")
        return EnrichedKEGG

class TFEnrichmentAnalyzer(BaseEnrichmentAnalyzer):
    GeneUpRegulatedByTF = {item["transcription_factor"]:[each['target_locus'] for each in item["regulation"]["up"]] for item in TF_genes}
    GeneDownRegulatedByTF = {item["transcription_factor"]:[each['target_locus'] for each in item["regulation"]["down"]] for item in TF_genes}
    AllGeneRegulatedByTF = {
        item["transcription_factor"]: list(set(
            [each['target_locus'] for each in item["regulation"]["up"]] +
            [each['target_locus'] for each in item["regulation"]["down"]]
        ))
        for item in TF_genes
    }
    def __init__(self, query_gene_set: Set[str]):
        super().__init__(query_gene_set)

    def TfRegulationEnrichmentAnalysis(
        self,
        query_gene_set_type: Literal["up", "down", "all"] = "all",
        HypGeo_p_threshold: float = 0.05,
        Fisher_p_threshold: float = None
    ) -> pd.DataFrame:
        if query_gene_set_type == "up":
            GeneSets = self.GeneUpRegulatedByTF
        elif query_gene_set_type == "down":
            GeneSets = self.GeneDownRegulatedByTF
        else:  # "all"
            GeneSets = self.AllGeneRegulatedByTF
        
        EnrichedTfReg = self.EnrichmentAnalysis(GeneSets)
        EnrichedTfReg = self.FilterClusters(EnrichedTfReg, HypGeo_p_threshold, Fisher_p_threshold)
        
        # Merge with TF information
        TFdf = pd.DataFrame(TF_genes)
        EnrichedTfReg = pd.merge(EnrichedTfReg, TFdf, left_on="ClusterId", right_on="transcription_factor", how="left")
        
        return EnrichedTfReg