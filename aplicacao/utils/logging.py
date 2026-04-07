"""
Módulo de logging com foco em privacidade.

Controla o que é logado baseado em configuração.
Por padrão, NÃO loga texto completo do currículo.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional


class AnalysisLogger:
    """
    Logger de análises com controle de privacidade.
    
    Por padrão, não loga dados sensíveis (texto do currículo, dados pessoais).
    Log detalhado só é ativado via variável de ambiente LOG_DETAILED=true.
    """
    
    def __init__(self, log_dir: str, detailed: bool = False):
        """
        Args:
            log_dir: Diretório para salvar logs
            detailed: Se True, loga texto completo (APENAS para debugging)
        """
        self.log_dir = log_dir
        self.detailed = detailed
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """Cria diretório de logs se não existir."""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def log_analysis(
        self,
        filename: str,
        extracted_text: str,
        response: Dict[str, Any],
        logger: Optional[logging.Logger] = None
    ) -> str:
        """
        Salva log da análise.
        
        Args:
            filename: Nome do arquivo analisado (sanitizado)
            extracted_text: Texto extraído (só logado se detailed=True)
            response: Resposta da análise
            logger: Logger Flask opcional
            
        Returns:
            Caminho do arquivo de log
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"analise_{timestamp}.txt"
        log_path = os.path.join(self.log_dir, log_filename)
        
        analysis = response.get("analysis", {})
        extraction = response.get("extraction", {})
        
        with open(log_path, 'w', encoding='utf-8') as f:
            self._write_header(f, filename)
            self._write_metadata(f, extraction, analysis)
            self._write_scores(f, analysis)
            
            # Texto extraído - APENAS se log detalhado estiver ativo
            if self.detailed:
                self._write_extracted_text(f, extracted_text)
                self._write_extracted_data(f, analysis.get("extracted_data", {}))
            else:
                f.write("\n" + "-" * 80 + "\n")
                f.write("TEXTO EXTRAÍDO\n")
                f.write("-" * 80 + "\n")
                f.write("[Log detalhado desativado por privacidade]\n")
                f.write("[Ative com LOG_DETAILED=true se necessário para debugging]\n")
            
            self._write_keywords(f, analysis)
            self._write_feedback(f, analysis)
            self._write_footer(f)
        
        if logger:
            logger.info(f"Log salvo em: {log_path}")
        
        return log_path
    
    def _write_header(self, f, filename: str):
        """Escreve cabeçalho do log."""
        f.write("=" * 80 + "\n")
        f.write(f"LOG DE ANÁLISE ATS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # Não logar nome original do arquivo (pode conter nome da pessoa)
        f.write(f"Arquivo: [sanitizado]\n")
        f.write(f"Log detalhado: {'ATIVO' if self.detailed else 'DESATIVADO'}\n")
    
    def _write_metadata(self, f, extraction: Dict, analysis: Dict):
        """Escreve metadados da extração."""
        f.write(f"Páginas: {extraction.get('page_count', 0)}\n")
        f.write(f"Palavras: {extraction.get('word_count', 0)}\n")
        f.write(f"Tempo de processamento: {analysis.get('processing_time_ms', 0)}ms\n\n")
    
    def _write_scores(self, f, analysis: Dict):
        """Escreve scores da análise."""
        f.write("-" * 80 + "\n")
        f.write("SCORES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Score Final: {analysis.get('final_score', 0)}/100\n")
        f.write(f"Keywords: {analysis.get('keyword_score', 0)}/100\n")
        f.write(f"Estrutura: {analysis.get('structure_score', 0)}/100\n")
        f.write(f"Legibilidade: {analysis.get('readability_score', 0)}/100\n")
        f.write(f"Classificação: {analysis.get('match_level', '-')}\n")
        f.write(f"Recomendação: {analysis.get('recommendation', '-')}\n\n")
    
    def _write_extracted_text(self, f, text: str):
        """Escreve texto extraído (apenas em modo detalhado)."""
        f.write("-" * 80 + "\n")
        f.write("TEXTO EXTRAÍDO DO PDF [MODO DETALHADO]\n")
        f.write("-" * 80 + "\n")
        f.write(text + "\n\n")
    
    def _write_extracted_data(self, f, extracted_data: Dict):
        """Escreve dados estruturados (apenas em modo detalhado)."""
        if not extracted_data:
            return
        
        f.write("-" * 80 + "\n")
        f.write("DADOS ESTRUTURADOS [MODO DETALHADO]\n")
        f.write("-" * 80 + "\n\n")
        
        # Dados pessoais
        f.write(">>> DADOS PESSOAIS:\n")
        f.write(f"    Nome: {extracted_data.get('name', '-')}\n")
        f.write(f"    Email: {extracted_data.get('email', '-')}\n")
        f.write(f"    Telefone: {extracted_data.get('phone', '-')}\n")
        f.write(f"    Localização: {extracted_data.get('location', '-')}\n\n")
        
        # Experiências
        f.write(">>> EXPERIÊNCIAS:\n")
        for exp in extracted_data.get('experiences', []):
            f.write(f"    - {exp.get('role', '-')} @ {exp.get('company', '-')}\n")
        f.write("\n")
    
    def _write_keywords(self, f, analysis: Dict):
        """Escreve keywords encontradas."""
        f.write("-" * 80 + "\n")
        f.write("KEYWORDS IDENTIFICADAS\n")
        f.write("-" * 80 + "\n")
        
        keywords = analysis.get('keywords_found', [])
        if keywords:
            # Agrupar por importância
            by_importance = {}
            for kw in keywords:
                imp = kw.get('importance', 'medium')
                by_importance.setdefault(imp, []).append(kw.get('keyword', ''))
            
            for imp in ['critical', 'high', 'medium', 'low']:
                if imp in by_importance:
                    f.write(f"  [{imp.upper()}]: {', '.join(by_importance[imp])}\n")
        else:
            f.write("  Nenhuma keyword técnica identificada\n")
        f.write("\n")
    
    def _write_feedback(self, f, analysis: Dict):
        """Escreve feedback da análise."""
        f.write("-" * 80 + "\n")
        f.write("FEEDBACK\n")
        f.write("-" * 80 + "\n")
        
        f.write("ALERTAS:\n")
        for w in analysis.get('warnings', []):
            f.write(f"  ⚠️ {w}\n")
        
        f.write("\nSUGESTÕES:\n")
        for s in analysis.get('suggestions', []):
            f.write(f"  💡 {s}\n")
        
        f.write("\nPONTOS POSITIVOS:\n")
        for p in analysis.get('positives', []):
            f.write(f"  ✅ {p}\n")
        f.write("\n")
    
    def _write_footer(self, f):
        """Escreve rodapé do log."""
        f.write("=" * 80 + "\n")
        f.write("FIM DO LOG\n")
        f.write("=" * 80 + "\n")
