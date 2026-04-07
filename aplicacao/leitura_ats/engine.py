"""
=============================================================================
ATS ENGINE - Motor de Análise de Currículos
=============================================================================

Implementação em Python de um sistema ATS (Applicant Tracking System)
para análise de currículos, usando técnicas de NLP:

- Tokenização e normalização de texto
- Stemming (redução à raiz) com RSLP Stemmer para Português
- Remoção de stopwords
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Cosine Similarity
- Dicionário de sinônimos técnicos
- N-grams para detectar termos compostos

Baseado no motor original em TypeScript do projeto job-search-simple.

Autor: Ricardo da Silva Júnior
Data: Abril/2026
Versão: 1.0.0 (Python)
=============================================================================
"""

import re
import math
import time
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from unidecode import unidecode

try:
    from .stopwords import STOPWORDS_PT
    from ..analise_keywords.synonyms import TECH_SYNONYMS, find_canonical_term
    from ..analise_keywords.keywords import (
        CRITICAL_KEYWORDS, KEYWORDS_CRITICAL, KEYWORDS_HIGH, KEYWORDS_MEDIUM,
        SECTION_KEYWORDS, get_area_for_keywords, get_keyword_importance
    )
except ImportError:
    from leitura_ats.stopwords import STOPWORDS_PT
    from analise_keywords.synonyms import TECH_SYNONYMS, find_canonical_term
    from analise_keywords.keywords import (
        CRITICAL_KEYWORDS, KEYWORDS_CRITICAL, KEYWORDS_HIGH, KEYWORDS_MEDIUM,
        SECTION_KEYWORDS, get_area_for_keywords, get_keyword_importance
    )


# Baixar recursos NLTK necessários (executar apenas uma vez)
def ensure_nltk_data():
    """Garante que os dados NLTK necessários estão disponíveis."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
    
    try:
        nltk.data.find('stemmers/rslp')
    except LookupError:
        nltk.download('rslp', quiet=True)


# =============================================================================
# DATACLASSES DE RESULTADO
# =============================================================================

@dataclass
class KeywordMatch:
    """Match de keyword com detalhes."""
    keyword: str
    found_as: str
    match_type: str  # "exact", "stem", "synonym", "ngram"
    importance: str  # "critical", "high", "medium", "low"


@dataclass
class SectionAnalysis:
    """Análise de seção do currículo."""
    name: str
    detected: bool
    content_preview: str = ""
    word_count: int = 0


@dataclass
class ATSChecklistItem:
    """Item do checklist de compatibilidade ATS."""
    item: str
    passed: bool
    category: str  # "estrutura", "conteudo", "formatacao", "keywords"
    severity: str = "info"  # "critical", "warning", "info"
    suggestion: str = ""


@dataclass
class ExperienceItem:
    """Item de experiência profissional extraído."""
    company: str
    role: str = ""
    period: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


@dataclass
class EducationItem:
    """Item de formação acadêmica extraído."""
    course: str
    institution: str = ""
    period: str = ""
    start_date: str = ""
    end_date: str = ""
    status: str = ""  # "concluído", "cursando"


@dataclass
class ExtractedData:
    """Dados estruturados extraídos do currículo."""
    # Dados pessoais
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    location: str = ""
    
    # Resumo/Objetivo
    summary: str = ""
    objective: str = ""
    
    # Experiências
    experiences: List[ExperienceItem] = field(default_factory=list)
    
    # Formação
    education: List[EducationItem] = field(default_factory=list)
    
    # Habilidades
    skills: List[str] = field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = field(default_factory=dict)
    
    # Idiomas
    languages: List[str] = field(default_factory=list)
    
    # Certificações
    certifications: List[str] = field(default_factory=list)


@dataclass
class ATSAnalysisResult:
    """Resultado completo da análise ATS."""
    # Scores principais (0-100)
    final_score: int
    keyword_score: int
    structure_score: int
    readability_score: int
    
    # Classificação
    match_level: str  # "Excelente", "Bom", "Regular", "Fraco"
    recommendation: str
    
    # Keywords
    keywords_found: List[KeywordMatch]
    keywords_critical: List[str]
    keywords_by_area: Dict[str, dict]
    
    # Estrutura
    sections_detected: List[SectionAnalysis]
    sections_missing: List[str]
    
    # Dados extraídos
    contact_info: Dict[str, Optional[str]]
    
    # Alertas e sugestões
    warnings: List[str]
    suggestions: List[str]
    positives: List[str]
    
    # Checklist ATS (novo)
    ats_checklist: List[ATSChecklistItem] = field(default_factory=list)
    
    # Métricas de conteúdo (novo)
    metrics_found: int = 0  # Quantidade de números/métricas encontradas
    action_verbs_found: int = 0  # Quantidade de verbos de ação
    date_format_valid: bool = True  # Formato de datas válido (MM/AAAA)
    
    # Metadados
    total_words: int = 0
    unique_keywords: int = 0
    processing_time_ms: int = 0
    
    # Campo opcional (deve vir por último)
    extracted_data: Optional[ExtractedData] = None


# =============================================================================
# CLASSE PRINCIPAL: ATS ENGINE
# =============================================================================

class ATSEngine:
    """
    Motor de análise ATS para currículos.
    
    Analisa o texto de um currículo e fornece métricas
    de legibilidade para sistemas ATS.
    """
    
    def __init__(self):
        """Inicializa o motor ATS."""
        ensure_nltk_data()
        self.stemmer = RSLPStemmer()
        
    def analyze(self, resume_text: str) -> ATSAnalysisResult:
        """
        Executa análise ATS completa do currículo.
        
        Args:
            resume_text: Texto extraído do currículo
            
        Returns:
            ATSAnalysisResult com métricas detalhadas
        """
        start_time = time.time()
        
        # Normalizar texto
        text_normalized = self._normalize_text(resume_text)
        text_lower = text_normalized.lower()
        
        # Tokenizar
        tokens = self._tokenize(text_normalized)
        stems = {self.stemmer.stem(t) for t in tokens}
        
        # 1. Extrair e analisar keywords
        keywords_found, keywords_critical = self._find_keywords(tokens, text_lower)
        keywords_by_area = get_area_for_keywords([k.keyword for k in keywords_found])
        
        # 2. Analisar estrutura (seções)
        sections_detected, sections_missing = self._analyze_sections(text_lower)
        
        # 3. Extrair dados de contato
        contact_info = self._extract_contact_info(resume_text)
        
        # 4. Extrair dados estruturados
        extracted_data = self._extract_structured_data(resume_text, keywords_found)
        
        # 5. Analisar métricas de conteúdo (novo)
        metrics_found = self._count_metrics(resume_text)
        action_verbs = self._count_action_verbs(resume_text)
        date_format_valid = self._validate_date_formats(resume_text)
        
        # 6. Gerar checklist ATS (novo)
        ats_checklist = self._generate_ats_checklist(
            resume_text, sections_detected, sections_missing,
            contact_info, keywords_found, metrics_found, date_format_valid
        )
        
        # 7. Calcular scores
        keyword_score = self._calculate_keyword_score(keywords_found, keywords_critical)
        structure_score = self._calculate_structure_score(sections_detected, sections_missing)
        readability_score = self._calculate_readability_score(resume_text, tokens)
        
        # Bônus por métricas e verbos de ação
        content_bonus = min((metrics_found * 2) + (action_verbs // 3), 10)
        
        # Score final ponderado
        final_score = int(
            (keyword_score * 0.40) +
            (structure_score * 0.35) +
            (readability_score * 0.25) +
            content_bonus
        )
        final_score = min(100, final_score)
        
        # 8. Gerar alertas e sugestões
        warnings, suggestions, positives = self._generate_feedback(
            keywords_found, sections_detected, sections_missing,
            contact_info, len(tokens), keywords_critical,
            metrics_found, action_verbs, date_format_valid
        )
        
        # 9. Classificação
        match_level, recommendation = self._get_classification(final_score)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ATSAnalysisResult(
            final_score=final_score,
            keyword_score=keyword_score,
            structure_score=structure_score,
            readability_score=readability_score,
            match_level=match_level,
            recommendation=recommendation,
            keywords_found=keywords_found,
            keywords_critical=keywords_critical,
            keywords_by_area=keywords_by_area,
            sections_detected=sections_detected,
            sections_missing=sections_missing,
            contact_info=contact_info,
            extracted_data=extracted_data,
            warnings=warnings,
            suggestions=suggestions,
            positives=positives,
            ats_checklist=ats_checklist,
            metrics_found=metrics_found,
            action_verbs_found=action_verbs,
            date_format_valid=date_format_valid,
            total_words=len(tokens),
            unique_keywords=len(set(k.keyword for k in keywords_found)),
            processing_time_ms=processing_time
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para análise."""
        # Remover múltiplos espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text)
        # Manter pontuação básica
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto removendo stopwords.
        
        Args:
            text: Texto normalizado
            
        Returns:
            Lista de tokens significativos
        """
        # Normalizar para ASCII (remover acentos para stemming)
        text_ascii = unidecode(text.lower())
        
        # Tokenizar
        try:
            tokens = word_tokenize(text_ascii, language='portuguese')
        except LookupError:
            # Fallback se punkt não estiver disponível
            tokens = text_ascii.split()
        
        # Filtrar
        filtered = [
            token for token in tokens
            if len(token) > 1
            and token not in STOPWORDS_PT
            and not token.isdigit()
            and re.match(r'^[a-z0-9\-/]+$', token)
        ]
        
        return filtered
    
    def _extract_ngrams(self, tokens: List[str], n: int) -> List[str]:
        """Extrai N-grams dos tokens."""
        return [' '.join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
    
    def _find_keywords(
        self, tokens: List[str], text_lower: str
    ) -> Tuple[List[KeywordMatch], List[str]]:
        """
        Encontra keywords técnicas no currículo.
        
        Classifica em 3 níveis de importância:
        - critical: Keywords principais (Linux, AWS, Docker, etc.)
        - high: Keywords secundárias (logs, tuning, backup, etc.)
        - medium: Keywords de contexto operacional (chamados, suporte, etc.)
        
        Returns:
            Tuple de (keywords encontradas, keywords críticas encontradas)
        """
        keywords_found = []
        keywords_critical = []
        seen = set()
        
        # Termos que precisam de match exato (muito curtos ou ambíguos)
        # Removido 'go' pois causa muitos falsos positivos
        exact_match_terms = {'sh', 'py', 'ha', 'dr', 'ad', 'dd', 'tf', 'n2', 'n3', 'ci', 'cd'}
        
        def term_exists(term: str) -> bool:
            """Verifica se termo existe no texto, respeitando boundaries."""
            if term in exact_match_terms or len(term) <= 2:
                # Para termos curtos, exigir boundary de palavra
                pattern = r'\b' + re.escape(term) + r'\b'
                return bool(re.search(pattern, text_lower))
            return term in text_lower
        
        # Buscar em todos os sinônimos
        for canonical, synonyms in TECH_SYNONYMS.items():
            all_terms = [canonical] + synonyms
            
            for term in all_terms:
                if term_exists(term) and term not in seen:
                    seen.add(term)
                    seen.add(canonical)  # Marcar canônico também
                    
                    # Usar nova função de classificação
                    importance = get_keyword_importance(canonical)
                    
                    keywords_found.append(KeywordMatch(
                        keyword=canonical,
                        found_as=term,
                        match_type="exact" if term == canonical else "synonym",
                        importance=importance
                    ))
                    
                    if importance == "critical":
                        keywords_critical.append(canonical)
                    break
        
        # Buscar keywords críticas diretamente (3 níveis)
        all_keywords = KEYWORDS_CRITICAL | KEYWORDS_HIGH | KEYWORDS_MEDIUM
        for kw in all_keywords:
            if kw not in seen and term_exists(kw):
                seen.add(kw)
                importance = get_keyword_importance(kw)
                
                keywords_found.append(KeywordMatch(
                    keyword=kw,
                    found_as=kw,
                    match_type="exact",
                    importance=importance
                ))
                
                if importance == "critical":
                    keywords_critical.append(kw)
        
        # Ordenar por importância (critical > high > medium)
        importance_order = {"critical": 0, "high": 1, "medium": 2}
        keywords_found.sort(key=lambda k: importance_order.get(k.importance, 3))
        
        return keywords_found, list(set(keywords_critical))
    
    def _analyze_sections(
        self, text_lower: str
    ) -> Tuple[List[SectionAnalysis], List[str]]:
        """
        Analisa seções do currículo.
        
        Returns:
            Tuple de (seções detectadas, seções faltando)
        """
        sections_detected = []
        sections_missing = []
        
        essential_sections = ["dados_pessoais", "experiencia", "formacao", "habilidades"]
        
        # Normalizar texto removendo acentos para busca mais robusta
        text_normalized = unidecode(text_lower)
        
        # Verificar se há dados de contato (email/telefone) mesmo sem título "Dados Pessoais"
        has_contact_data = bool(
            re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_lower) or  # email
            re.search(r'\(?[1-9]{2}\)?\s?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}', text_lower)  # telefone
        )
        
        for section_key, patterns in SECTION_KEYWORDS.items():
            # Verificar em ambos: texto original e normalizado
            detected = any(
                pattern in text_lower or unidecode(pattern) in text_normalized 
                for pattern in patterns
            )
            
            # Para dados_pessoais, considerar presente se houver email/telefone
            if section_key == "dados_pessoais" and not detected and has_contact_data:
                detected = True
            
            section_names = {
                "dados_pessoais": "Dados Pessoais",
                "objetivo": "Objetivo",
                "resumo": "Resumo/Perfil",
                "experiencia": "Experiência Profissional",
                "formacao": "Formação Acadêmica",
                "habilidades": "Habilidades Técnicas",
                "idiomas": "Idiomas",
                "certificacoes": "Certificações/Cursos",
                "projetos": "Projetos/Portfolio"
            }
            
            name = section_names.get(section_key, section_key)
            
            if detected:
                sections_detected.append(SectionAnalysis(
                    name=name,
                    detected=True
                ))
            elif section_key in essential_sections:
                sections_missing.append(name)
        
        return sections_detected, sections_missing
    
    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extrai informações de contato do currículo."""
        info = {
            "email": None,
            "telefone": None,
            "linkedin": None,
            "github": None
        }
        
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info["email"] = email_match.group()
        
        # Telefone BR
        phone_match = re.search(
            r'(?:\+55\s?)?\(?[1-9]{2}\)?\s?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}',
            text
        )
        if phone_match:
            info["telefone"] = phone_match.group()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.IGNORECASE)
        if linkedin_match:
            info["linkedin"] = linkedin_match.group()
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.IGNORECASE)
        if github_match:
            info["github"] = github_match.group()
        
        return info
    
    def _calculate_keyword_score(
        self, keywords: List[KeywordMatch], critical: List[str]
    ) -> int:
        """Calcula score de keywords (0-100)."""
        if not keywords:
            return 0
        
        base_score = min(len(keywords) * 5, 60)  # Até 60 pontos por quantidade
        critical_bonus = min(len(critical) * 8, 40)  # Até 40 pontos por críticas
        
        return min(base_score + critical_bonus, 100)
    
    def _calculate_structure_score(
        self, detected: List[SectionAnalysis], missing: List[str]
    ) -> int:
        """Calcula score de estrutura (0-100)."""
        essential_count = 4  # dados, experiência, formação, habilidades
        detected_essential = len(detected)
        missing_essential = len(missing)
        
        base_score = (detected_essential / essential_count) * 70
        penalty = missing_essential * 15
        bonus = max(len(detected) - essential_count, 0) * 5  # Seções extras
        
        return max(0, min(100, int(base_score - penalty + bonus)))
    
    def _calculate_readability_score(
        self, text: str, tokens: List[str]
    ) -> int:
        """Calcula score de legibilidade ATS (0-100)."""
        score = 70  # Base
        
        word_count = len(tokens)
        
        # Penalizar muito curto ou muito longo
        if word_count < 100:
            score -= 20
        elif word_count > 1500:
            score -= 10
        
        # Verificar formatação problemática
        special_bullets = len(re.findall(r'[►▪●○◦■□▸‣⁃]', text))
        if special_bullets > 5:
            score -= 15
        
        # Verificar excesso de caracteres especiais
        special_chars = len(re.findall(r'[^\w\s\.\,\;\:\-\(\)\@\/\+]', text))
        if special_chars > 50:
            score -= 10
        
        # Bônus por boa quantidade de palavras
        if 200 <= word_count <= 800:
            score += 15
        
        return max(0, min(100, score))
    
    def _count_metrics(self, text: str) -> int:
        """
        Conta métricas quantitativas no currículo.
        
        Métricas (números + indicadores) são importantes para ATS pois
        demonstram resultados tangíveis. Ex: "reduzi 30%", "100 usuários"
        """
        metrics = 0
        
        # Padrões de métricas
        patterns = [
            r'\d+\s*%',  # Percentuais: 30%, 100%
            r'\d+\s*(?:horas?|dias?|meses?|anos?)',  # Tempo: 5 horas, 2 anos
            r'R\$\s*[\d\.,]+',  # Valores em reais
            r'\$\s*[\d\.,]+',  # Valores em dólar
            r'\d+\s*(?:usuários?|clientes?|chamados?|tickets?)',  # Volumes
            r'(?:reduzi|aumentei|melhorei|otimizei)[^.]*\d+',  # Verbos de resultado + número
            r'\d+\s*x\s*(?:mais|maior|menor)',  # Multiplicadores: 3x mais
            r'(?:top|primeiro|segundo|terceiro)\s*\d*',  # Rankings
            r'\d{1,3}(?:\.\d{3})*\s*(?:processos?|transações?|registros?)',  # Grandes números
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics += len(matches)
        
        return metrics
    
    def _count_action_verbs(self, text: str) -> int:
        """
        Conta verbos de ação no currículo.
        
        Verbos de ação no início de bullets demonstram proatividade
        e são bem vistos por ATS e recrutadores.
        """
        # Lista de verbos de ação em português (primeira pessoa passado)
        action_verbs = [
            'implementei', 'desenvolvi', 'criei', 'gerenciei', 'coordenei',
            'liderei', 'otimizei', 'automatizei', 'reduzi', 'aumentei',
            'melhorei', 'projetei', 'configurei', 'administrei', 'mantive',
            'integrei', 'migrei', 'implantei', 'padronizei', 'documentei',
            'analisei', 'monitorei', 'resolvi', 'diagnostiquei', 'suportei',
            'treinei', 'capacitei', 'elaborei', 'planejei', 'executei',
            'conduzi', 'estruturei', 'organizei', 'reestruturei', 'modernizei',
            'participei', 'contribuí', 'atuei', 'colaborei', 'trabalhei',
            # Infinitivos (menos impactantes mas ainda contam)
            'desenvolver', 'implementar', 'gerenciar', 'administrar', 'criar',
            'otimizar', 'automatizar', 'integrar', 'configurar', 'monitorar'
        ]
        
        text_lower = text.lower()
        count = 0
        
        for verb in action_verbs:
            # Contar ocorrências do verbo (início de frase ou após bullet)
            pattern = rf'(?:^|[-•*]\s*|[\n\r]\s*){verb}\b'
            matches = re.findall(pattern, text_lower)
            count += len(matches)
        
        return count
    
    def _validate_date_formats(self, text: str) -> bool:
        """
        Valida se as datas estão em formato padrão (MM/AAAA ou Mês/AAAA).
        
        Datas consistentes ajudam no parsing do ATS.
        """
        # Padrões de data válidos
        valid_patterns = [
            r'\d{1,2}/\d{4}',  # MM/AAAA ou M/AAAA
            r'(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)[a-zç]*\.?\s*(?:de\s*)?\d{4}',  # Mês AAAA
            r'(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s*(?:de\s*)?\d{4}',
        ]
        
        # Padrões de data problemáticos
        invalid_patterns = [
            r'\d{4}\s*[-–/]\s*\d{4}',  # AAAA - AAAA (sem mês)
            r'\d{1,2}/\d{1,2}/\d{2}(?!\d)',  # DD/MM/AA (ano curto)
        ]
        
        # Contar padrões válidos e inválidos
        valid_count = 0
        invalid_count = 0
        
        text_lower = text.lower()
        
        for pattern in valid_patterns:
            valid_count += len(re.findall(pattern, text_lower))
        
        for pattern in invalid_patterns:
            invalid_count += len(re.findall(pattern, text_lower))
        
        # Válido se tem mais datas válidas que inválidas (ou nenhuma inválida)
        return invalid_count == 0 or valid_count > invalid_count * 2
    
    def _generate_ats_checklist(
        self,
        text: str,
        sections_detected: List[SectionAnalysis],
        sections_missing: List[str],
        contact: Dict[str, Optional[str]],
        keywords: List[KeywordMatch],
        metrics_found: int,
        date_format_valid: bool
    ) -> List[ATSChecklistItem]:
        """
        Gera checklist de compatibilidade ATS.
        
        Baseado nas melhores práticas documentadas:
        - Estrutura de uma coluna
        - Títulos de seção padronizados
        - Formato de arquivo (PDF texto / DOCX)
        - Keywords contextualizadas
        - Métricas de resultado
        - Dados de contato completos
        """
        checklist = []
        
        # 1. ESTRUTURA
        # Verificar seções essenciais
        essential_detected = len(sections_detected) >= 4
        checklist.append(ATSChecklistItem(
            item="Seções essenciais detectadas (Dados, Experiência, Formação, Habilidades)",
            passed=essential_detected,
            category="estrutura",
            severity="critical" if not essential_detected else "info",
            suggestion="Use títulos padronizados: 'Experiência Profissional', 'Formação Acadêmica', 'Habilidades'"
        ))
        
        # Verificar se não há seções faltando
        no_missing = len(sections_missing) == 0
        checklist.append(ATSChecklistItem(
            item="Todas as seções obrigatórias presentes",
            passed=no_missing,
            category="estrutura",
            severity="warning" if not no_missing else "info",
            suggestion=f"Adicione as seções: {', '.join(sections_missing)}" if sections_missing else ""
        ))
        
        # 2. CONTATO
        has_email = bool(contact.get("email"))
        checklist.append(ATSChecklistItem(
            item="Email de contato presente",
            passed=has_email,
            category="conteudo",
            severity="critical" if not has_email else "info",
            suggestion="Adicione um email profissional no topo do currículo"
        ))
        
        has_phone = bool(contact.get("telefone"))
        checklist.append(ATSChecklistItem(
            item="Telefone de contato presente",
            passed=has_phone,
            category="conteudo",
            severity="warning" if not has_phone else "info",
            suggestion="Adicione telefone com DDD para facilitar contato"
        ))
        
        # 3. KEYWORDS
        has_critical = len([k for k in keywords if k.importance == "critical"]) >= 3
        checklist.append(ATSChecklistItem(
            item="Keywords técnicas principais presentes (3+)",
            passed=has_critical,
            category="keywords",
            severity="warning" if not has_critical else "info",
            suggestion="Adicione tecnologias relevantes: Linux, AWS, Docker, Python, etc."
        ))
        
        has_variety = len(set(k.keyword for k in keywords)) >= 8
        checklist.append(ATSChecklistItem(
            item="Variedade de keywords técnicas (8+)",
            passed=has_variety,
            category="keywords",
            severity="info",
            suggestion="Diversifique as tecnologias mencionadas"
        ))
        
        # 4. CONTEÚDO
        has_metrics = metrics_found >= 3
        checklist.append(ATSChecklistItem(
            item="Métricas e resultados quantificados (3+)",
            passed=has_metrics,
            category="conteudo",
            severity="warning" if not has_metrics else "info",
            suggestion="Adicione números: 'reduzi 30%', 'gerenciei 50 servidores', etc."
        ))
        
        checklist.append(ATSChecklistItem(
            item="Formato de datas consistente (MM/AAAA)",
            passed=date_format_valid,
            category="formatacao",
            severity="warning" if not date_format_valid else "info",
            suggestion="Use formato consistente: 'Janeiro 2023' ou '01/2023'"
        ))
        
        # 5. FORMATAÇÃO
        # Verificar caracteres especiais problemáticos
        special_chars = len(re.findall(r'[►▪●○◦■□▸‣⁃★☆✓✗✔✘]', text))
        no_special = special_chars < 5
        checklist.append(ATSChecklistItem(
            item="Bullets e caracteres simples (sem símbolos especiais)",
            passed=no_special,
            category="formatacao",
            severity="warning" if not no_special else "info",
            suggestion="Use bullets simples (-,*,•) em vez de símbolos decorativos"
        ))
        
        # Verificar tamanho adequado
        word_count = len(text.split())
        good_length = 150 <= word_count <= 1200
        checklist.append(ATSChecklistItem(
            item="Tamanho adequado (150-1200 palavras)",
            passed=good_length,
            category="estrutura",
            severity="warning" if not good_length else "info",
            suggestion="Currículo muito curto" if word_count < 150 else "Currículo muito longo" if word_count > 1200 else ""
        ))
        
        return checklist
    
    def _generate_feedback(
        self,
        keywords: List[KeywordMatch],
        sections_detected: List[SectionAnalysis],
        sections_missing: List[str],
        contact: Dict[str, Optional[str]],
        word_count: int,
        critical_keywords: List[str],
        metrics_found: int = 0,
        action_verbs: int = 0,
        date_format_valid: bool = True
    ) -> Tuple[List[str], List[str], List[str]]:
        """Gera warnings, sugestões e pontos positivos."""
        warnings = []
        suggestions = []
        positives = []
        
        # Warnings
        if not contact.get("email"):
            warnings.append("⚠️ Nenhum email detectado - essencial para contato")
        
        if not contact.get("telefone"):
            warnings.append("⚠️ Nenhum telefone detectado - adicione para facilitar contato")
        
        if sections_missing:
            for section in sections_missing:
                warnings.append(f"⚠️ Seção '{section}' não detectada - pode prejudicar análise")
        
        if word_count < 150:
            warnings.append("⚠️ Currículo muito curto - adicione mais detalhes")
        
        if not date_format_valid:
            warnings.append("⚠️ Formato de datas inconsistente - use padrão MM/AAAA")
        
        if metrics_found < 2:
            warnings.append("⚠️ Poucas métricas quantitativas - adicione números e resultados")
        
        # Sugestões
        if not contact.get("linkedin"):
            suggestions.append("💡 Adicione seu perfil LinkedIn para credibilidade")
        
        if not contact.get("github") and any(k.keyword in ["python", "javascript", "devops"] for k in keywords):
            suggestions.append("💡 Perfil técnico: considere adicionar link do GitHub")
        
        if len(critical_keywords) < 5:
            suggestions.append("💡 Adicione mais tecnologias específicas (ex: Linux, AWS, Docker)")
        
        if action_verbs < 5:
            suggestions.append("💡 Use mais verbos de ação no infinitivo: 'implementar', 'desenvolver', 'otimizar'")
        
        if metrics_found >= 2 and metrics_found < 5:
            suggestions.append("💡 Bom uso de métricas - adicione mais números para destacar resultados")
        
        # Positivos
        if len(keywords) >= 10:
            positives.append("✅ Boa quantidade de keywords técnicas identificadas")
        
        if len(sections_detected) >= 4:
            positives.append("✅ Currículo bem estruturado com seções claras")
        
        if contact.get("email") and contact.get("telefone"):
            positives.append("✅ Informações de contato completas")
        
        if len(critical_keywords) >= 5:
            positives.append("✅ Tecnologias relevantes bem destacadas")
        
        if 200 <= word_count <= 800:
            positives.append("✅ Tamanho adequado para análise ATS")
        
        if metrics_found >= 5:
            positives.append("✅ Excelente uso de métricas e resultados quantificados")
        
        if action_verbs >= 8:
            positives.append("✅ Bom uso de verbos de ação nas experiências")
        
        if date_format_valid:
            positives.append("✅ Formato de datas consistente e adequado")
        
        return warnings, suggestions, positives
    
    def _extract_structured_data(self, text: str, keywords_found: List[KeywordMatch]) -> ExtractedData:
        """
        Extrai dados estruturados do currículo.
        
        Identifica e extrai:
        - Nome do candidato
        - Resumo/Objetivo profissional
        - Experiências (empresa, cargo, período)
        - Formação acadêmica
        - Habilidades técnicas
        - Idiomas
        - Certificações
        """
        data = ExtractedData()
        
        # Preservar quebras de linha originais
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # 1. Extrair nome (geralmente primeira linha)
        data.name = self._extract_name(lines)
        
        # 2. Extrair contato
        contact = self._extract_contact_info(text)
        data.email = contact.get("email", "")
        data.phone = contact.get("telefone", "")
        data.linkedin = contact.get("linkedin", "")
        
        # 3. Extrair localização
        data.location = self._extract_location(text, lines)
        
        # 4. Extrair resumo/objetivo
        data.summary, data.objective = self._extract_summary(text)
        
        # 5. Extrair experiências
        data.experiences = self._extract_experiences(text)
        
        # 6. Extrair formação
        data.education = self._extract_education(text)
        
        # 7. Extrair habilidades DA SEÇÃO do currículo (não auto-gerar)
        skills_flat, skills_by_cat = self._extract_skills_from_section(text)
        
        # Se conseguiu extrair da seção, usar. Senão, fallback para keywords
        if skills_flat:
            data.skills = skills_flat
            data.skills_by_category = skills_by_cat
        else:
            # Fallback: usar keywords filtradas
            non_skill_keywords = {'júnior', 'junior', 'pleno', 'sênior', 'senior', 'remoto', 
                                  'presencial', 'híbrido', 'hibrido', 'inglês', 'ingles', 
                                  'português', 'portugues', 'espanhol', 'alemão', 'alemao'}
            data.skills = [k.keyword for k in keywords_found 
                           if k.keyword.lower() not in non_skill_keywords]
            data.skills_by_category = self._categorize_skills(keywords_found)
        
        # 8. Extrair idiomas
        data.languages = self._extract_languages(text)
        
        # 9. Extrair certificações
        data.certifications = self._extract_certifications(text)
        
        return data
    
    def _extract_name(self, lines: List[str]) -> str:
        """Extrai nome do candidato das primeiras linhas."""
        for line in lines[:3]:
            line = line.strip()
            if not line:
                continue
            
            # Ignorar linhas com email, telefone, URLs, etc.
            if any(x in line.lower() for x in ['@', 'http', 'www', 'telefone', 'e-mail', 'linkedin']):
                continue
            
            # Ignorar linhas muito longas (provavelmente não é nome)
            if len(line) > 50:
                continue
            
            words = line.split()
            # Nome tem entre 2 e 5 palavras
            if 2 <= len(words) <= 5:
                # Verificar se parece um nome (palavras começam com maiúscula)
                if all(w[0].isupper() or w.lower() in ['de', 'da', 'do', 'dos', 'das', 'e', 'jr', 'júnior', 'filho', 'neto'] 
                       for w in words if w):
                    return line
        
        return ""
    
    def _extract_location(self, text: str, lines: List[str]) -> str:
        """Extrai localização do candidato."""
        # Lista de estados brasileiros
        estados = ['RS', 'SP', 'RJ', 'MG', 'PR', 'SC', 'BA', 'PE', 'CE', 'DF', 'GO', 'ES', 
                   'PA', 'MA', 'PB', 'RN', 'AL', 'PI', 'MT', 'MS', 'SE', 'RO', 'TO', 'AC', 'AP', 'AM', 'RR']
        
        # Padrão: Cidade, UF ou Cidade - UF
        for line in lines[:10]:  # Verificar primeiras 10 linhas
            for estado in estados:
                # Padrão: "Cidade, UF" ou "Cidade - UF"
                pattern = rf'([A-Za-zÀ-ÿ\s]+(?:do Sul|do Norte|de Dentro|das Flores)?)\s*[,\-–]\s*{estado}\b'
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    cidade = match.group(1).strip()
                    # Limpar a cidade de prefixos indesejados
                    cidade = re.sub(r'^(telefone|email|e-mail|linkedin|github|endere[çc]o)[\s:]*', '', cidade, flags=re.IGNORECASE)
                    if cidade:
                        return f"{cidade}, {estado}"
        
        # Cidades conhecidas
        cidades_conhecidas = [
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre', 'Curitiba',
            'Salvador', 'Recife', 'Fortaleza', 'Brasília', 'Florianópolis', 'Campinas',
            'Caxias do Sul', 'Joinville', 'Blumenau', 'Londrina', 'Maringá', 'Santos',
            'Ribeirão Preto', 'Sorocaba', 'Uberlândia', 'Goiânia', 'Manaus', 'Belém'
        ]
        
        for cidade in cidades_conhecidas:
            if cidade.lower() in text.lower():
                return cidade
        
        return ""
    
    def _extract_summary(self, text: str) -> Tuple[str, str]:
        """Extrai resumo e objetivo profissional."""
        summary = ""
        objective = ""
        
        # Encontrar seção de resumo por cabeçalho
        summary_headers = [
            r'(?:resumo\s*profissional|perfil\s*profissional|resumo|perfil|sobre\s*mim|apresenta[çc][aã]o)\s*[\n:]',
        ]
        
        for header_pattern in summary_headers:
            match = re.search(header_pattern, text, re.IGNORECASE)
            if match:
                start = match.end()
                # Encontrar próxima seção
                next_section = re.search(
                    r'\n\s*(experi[êe]ncia|forma[çc][aã]o|habilidades|objetivo|principais|compet[êe]ncias|educa[çc][aã]o)',
                    text[start:], re.IGNORECASE
                )
                end = start + next_section.start() if next_section else min(start + 1000, len(text))
                
                summary = text[start:end].strip()
                summary = re.sub(r'\s+', ' ', summary)[:1500]  # Aumentado para 1500 caracteres
                break
        
        # Encontrar objetivo
        objective_headers = [
            r'(?:objetivo\s*profissional|objetivo|meta\s*profissional)\s*[\n:]',
        ]
        
        for header_pattern in objective_headers:
            match = re.search(header_pattern, text, re.IGNORECASE)
            if match:
                start = match.end()
                next_section = re.search(
                    r'\n\s*(experi[êe]ncia|forma[çc][aã]o|habilidades|resumo|principais|compet[êe]ncias)',
                    text[start:], re.IGNORECASE
                )
                end = start + next_section.start() if next_section else min(start + 500, len(text))
                
                objective = text[start:end].strip()
                objective = re.sub(r'\s+', ' ', objective)[:400]
                break
        
        return summary, objective
    
    def _extract_experiences(self, text: str) -> List[ExperienceItem]:
        """
        Extrai experiências profissionais do currículo.
        
        Suporta múltiplos formatos:
        - Cargo | Empresa | Período
        - Cargo - Empresa - Período  
        - Empresa\nCargo - Período
        - Diferentes formatos de data (MM/YYYY, Mês/YYYY, Mês de YYYY)
        """
        experiences = []
        
        # Encontrar seção de experiência
        exp_headers = [
            r'experi[êe]ncias?\s*profission(?:al|ais)',
            r'experi[êe]ncia\s*de\s*trabalho',
            r'experi[êe]ncia',
            r'hist[óo]rico\s*profissional',
            r'carreira\s*profissional',
            r'atua[çc][aã]o\s*profissional',
        ]
        
        exp_start = None
        for header in exp_headers:
            match = re.search(header, text, re.IGNORECASE)
            if match:
                exp_start = match.end()
                break
        
        if exp_start is None:
            return experiences
        
        # Encontrar fim da seção (próxima seção)
        next_sections = [
            r'\n\s*(?:forma[çc][aã]o|educa[çc][aã]o|habilidades|compet[êe]ncias|idiomas|certifica[çc][õo]es|cursos|outras?\s*informa[çc][õo]es)',
        ]
        
        exp_end = len(text)
        for section in next_sections:
            match = re.search(section, text[exp_start:], re.IGNORECASE)
            if match:
                exp_end = exp_start + match.start()
                break
        
        exp_text = text[exp_start:exp_end]
        
        # Padrão para linha de experiência (cargo | empresa | período)
        # Formato: "Cargo Sênior/Pleno/Júnior/N1/N2 (opcional) | Empresa (Ramo) | Mês de ANO a Mês de ANO"
        exp_line_pattern = r'([A-Za-zÀ-ÿ\s]+(?:Sênior|Senior|Pleno|Júnior|Junior|Jr|N\d+)?(?:\s*\([^)]+\))?)\s*[|\-–]\s*([A-Za-zÀ-ÿ\s\(\)\.]+)\s*[|\-–]\s*([A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4}\s*(?:a|até|[-–])\s*(?:[A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4}|Atual|Presente|atual|presente|atualmente))'
        
        # Padrão alternativo para datas em formato MM/YYYY ou apenas "Ano a Ano"
        date_patterns = [
            r'([A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4})\s*(?:a|até|[-–])\s*([A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4}|Atual|Presente|atual|presente|atualmente)',
            r'(\d{1,2}[/\.]\d{4})\s*(?:a|até|[-–])\s*(\d{1,2}[/\.]\d{4}|Atual|Presente)',
            r'(\d{4})\s*(?:a|até|[-–])\s*(\d{4}|Atual|Presente)',
        ]
        
        # Lista de cargos conhecidos para ajudar na identificação
        cargo_keywords = [
            'analista', 'desenvolvedor', 'developer', 'gerente', 'manager', 'coordenador',
            'supervisor', 'diretor', 'técnico', 'assistente', 'estagiário', 'estagiario',
            'consultor', 'especialista', 'specialist', 'engineer', 'engenheiro', 'arquiteto',
            'architect', 'líder', 'lider', 'lead', 'head', 'programador', 'administrador',
            'dba', 'devops', 'sre', 'sysadmin', 'suporte', 'atendente', 'operador'
        ]
        
        # Processar linha por linha buscando experiências
        lines = exp_text.split('\n')
        current_exp = None
        description_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Tentar detectar uma nova experiência
            # Verificar se a linha tem formato "Cargo | Empresa | Período"
            match = re.search(exp_line_pattern, line, re.IGNORECASE)
            if match:
                # Salvar experiência anterior
                if current_exp and (current_exp.company or current_exp.role):
                    current_exp.description = '\n'.join(description_lines)
                    experiences.append(current_exp)
                
                current_exp = ExperienceItem(
                    company=match.group(2).strip(),
                    role=match.group(1).strip(),
                    period=match.group(3).strip()
                )
                # Extrair datas
                for date_pattern in date_patterns:
                    date_match = re.search(date_pattern, match.group(3), re.IGNORECASE)
                    if date_match:
                        current_exp.start_date = date_match.group(1)
                        current_exp.end_date = date_match.group(2)
                        break
                
                description_lines = []
                continue
            
            # Verificar se linha parece início de nova experiência (tem cargo + data)
            has_cargo = any(kw in line.lower() for kw in cargo_keywords)
            has_date = False
            for date_pattern in date_patterns:
                if re.search(date_pattern, line, re.IGNORECASE):
                    has_date = True
                    break
            
            if has_cargo and has_date:
                # Salvar experiência anterior
                if current_exp and (current_exp.company or current_exp.role):
                    current_exp.description = '\n'.join(description_lines)
                    experiences.append(current_exp)
                
                current_exp = ExperienceItem(company="")
                
                # Extrair cargo
                for kw in cargo_keywords:
                    if kw in line.lower():
                        # Encontrar o cargo completo (incluindo N1, N2, SLA, etc.)
                        cargo_match = re.search(
                            rf'([A-Za-zÀ-ÿ\s]*{kw}[A-Za-zÀ-ÿ\s]*(?:Sênior|Senior|Pleno|Júnior|Junior|Jr|N\d+)?(?:\s*\([^)]+\))?)',
                            line, re.IGNORECASE
                        )
                        if cargo_match:
                            current_exp.role = cargo_match.group(1).strip()[:100]
                            break
                
                # Extrair empresa (texto entre cargo e data, ou após "|")
                pipe_match = re.search(r'[|\-–]\s*([A-Za-zÀ-ÿ\s\(\)\.]+?)\s*[|\-–]', line)
                if pipe_match:
                    current_exp.company = pipe_match.group(1).strip()[:100]
                
                # Extrair período
                for date_pattern in date_patterns:
                    date_match = re.search(date_pattern, line, re.IGNORECASE)
                    if date_match:
                        current_exp.period = date_match.group(0)
                        current_exp.start_date = date_match.group(1)
                        current_exp.end_date = date_match.group(2)
                        break
                
                description_lines = []
                continue
            
            # Se já temos uma experiência em andamento, acumular descrição
            if current_exp:
                # Manter o bullet se existir, apenas limpar espaços extras
                if line and len(line) > 5:
                    # Se começa com bullet, formatar consistentemente
                    if re.match(r'^[-•*]\s*', line):
                        clean_line = re.sub(r'^[-•*]\s*', '- ', line)  # Padroniza para "- "
                    else:
                        clean_line = line
                    description_lines.append(clean_line)
        
        # Não esquecer da última experiência
        if current_exp and (current_exp.company or current_exp.role):
            current_exp.description = '\n'.join(description_lines)
            experiences.append(current_exp)
        
        return experiences[:10]
    
    def _extract_education(self, text: str) -> List[EducationItem]:
        """Extrai formação acadêmica com datas e instituições."""
        from datetime import datetime
        education = []
        
        # Encontrar seção de formação
        edu_pattern = r'(?:forma[çc][aã]o|educa[çc][aã]o|gradua[çc][aã]o|acadêmico|escolaridade)[\s\w]*[:\n]+'
        edu_match = re.search(edu_pattern, text, re.IGNORECASE)
        
        if not edu_match:
            return education
        
        # Texto após cabeçalho
        edu_start = edu_match.end()
        next_section = re.search(
            r'\n{2,}(?:experi[êe]ncia|habilidades|competências|idiomas|certifica[çc][õo]es|cursos)',
            text[edu_start:], re.IGNORECASE
        )
        edu_end = edu_start + next_section.start() if next_section else min(edu_start + 1000, len(text))
        
        edu_text = text[edu_start:edu_end]
        
        # Padrões de data
        date_patterns = [
            r'([A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4})\s*(?:a|até|[-–])\s*([A-Za-zÀ-ÿ]+\s*(?:de\s*)?\d{4}|Atual|Presente|atual|presente|cursando)',
            r'(\d{1,2}[/\.]\d{4})\s*(?:a|até|[-–])\s*(\d{1,2}[/\.]\d{4}|Atual|Presente|cursando)',
            r'(\d{4})\s*(?:a|até|[-–])\s*(\d{4}|Atual|Presente|cursando)',
        ]
        
        # Padrões de curso e instituição
        course_patterns = [
            r'(Bacharel(?:ado)?|Tecnólogo|Licenciatura|Mestrado|Doutorado|MBA|Pós[-\s]?Graduação|Técnico|Ensino\s*Médio|Superior)\s*(?:em|in)?\s*([A-Za-zÀ-ÿ\s]+)',
            r'(Graduação|Curso\s*Superior|Curso\s*Técnico)\s*(?:em|in)?\s*([A-Za-zÀ-ÿ\s]+)',
        ]
        
        institution_keywords = [
            'universidade', 'faculdade', 'instituto', 'escola', 'centro',
            'unisinos', 'ufrgs', 'puc', 'senac', 'senai', 'fatec', 'ifrs', 'ufsc'
        ]
        
        # Processar linha por linha
        lines = edu_text.split('\n')
        current_edu = None
        current_year = datetime.now().year
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Tentar detectar curso
            course_found = None
            for pattern in course_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    course_found = f"{match.group(1).strip()} {match.group(2).strip()}".strip()
                    break
            
            if course_found:
                # Salvar anterior se existe
                if current_edu and current_edu.course:
                    education.append(current_edu)
                
                current_edu = EducationItem(course=course_found)
                
                # Procurar datas na mesma linha
                for date_pattern in date_patterns:
                    date_match = re.search(date_pattern, line, re.IGNORECASE)
                    if date_match:
                        current_edu.start_date = date_match.group(1)
                        current_edu.end_date = date_match.group(2)
                        
                        # Determinar status
                        end_lower = date_match.group(2).lower()
                        if any(x in end_lower for x in ['atual', 'presente', 'cursando']):
                            current_edu.status = "cursando"
                        else:
                            # Extrair ano final
                            year_match = re.search(r'\d{4}', date_match.group(2))
                            if year_match:
                                end_year = int(year_match.group())
                                if end_year > current_year:
                                    current_edu.status = "cursando"
                                else:
                                    current_edu.status = "concluído"
                        
                        if current_edu.start_date and current_edu.end_date:
                            current_edu.period = f"{current_edu.start_date} - {current_edu.end_date}"
                        break
                
                continue
            
            # Se temos edu ativa, procurar instituição
            if current_edu:
                line_lower = line.lower()
                if any(kw in line_lower for kw in institution_keywords):
                    # Limpar e extrair nome da instituição
                    inst = re.sub(r'^[-•*]\s*', '', line)
                    inst = re.sub(r'\d{4}.*$', '', inst)  # Remover datas
                    if inst and len(inst) > 3:
                        current_edu.institution = inst.strip()[:100]
                
                # Procurar datas se ainda não temos
                if not current_edu.period:
                    for date_pattern in date_patterns:
                        date_match = re.search(date_pattern, line, re.IGNORECASE)
                        if date_match:
                            current_edu.start_date = date_match.group(1)
                            current_edu.end_date = date_match.group(2)
                            
                            # Determinar status
                            end_lower = date_match.group(2).lower()
                            if any(x in end_lower for x in ['atual', 'presente', 'cursando']):
                                current_edu.status = "cursando"
                            else:
                                year_match = re.search(r'\d{4}', date_match.group(2))
                                if year_match:
                                    end_year = int(year_match.group())
                                    if end_year > current_year:
                                        current_edu.status = "cursando"
                                    else:
                                        current_edu.status = "concluído"
                            
                            if current_edu.start_date and current_edu.end_date:
                                current_edu.period = f"{current_edu.start_date} - {current_edu.end_date}"
                            break
        
        # Salvar último item
        if current_edu and current_edu.course:
            education.append(current_edu)
        
        return education[:10]
    
    def _extract_skills_from_section(self, text: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """
        Extrai habilidades da seção de habilidades do currículo.
        Retorna (skills_flat, skills_by_category).
        Detecta se há categorização no texto e preserva.
        """
        skills_flat = []
        skills_by_category = {}
        
        # Padrões para encontrar seção de habilidades
        skills_patterns = [
            r'(?:habilidades?\s*(?:t[ée]cnicas?|e\s*idiomas?))[:\s]*\n',
            r'(?:compet[êe]ncias?\s*t[ée]cnicas?)[:\s]*\n',
            r'(?:conhecimentos?\s*t[ée]cnicos?)[:\s]*\n',
            r'(?:tecnologias?|stack\s*t[ée]cnica?)[:\s]*\n',
            r'(?:ferramentas?\s*e\s*tecnologias?)[:\s]*\n',
        ]
        
        # Encontrar seção
        skills_match = None
        for pattern in skills_patterns:
            skills_match = re.search(pattern, text, re.IGNORECASE)
            if skills_match:
                break
        
        if not skills_match:
            return skills_flat, skills_by_category
        
        # Extrair texto da seção
        skills_start = skills_match.end()
        next_section = re.search(
            r'\n{2,}(?:experi[êe]ncia|forma[çc][aã]o|educa[çc][aã]o|idiomas|certifica[çc][õo]es|cursos|projetos)',
            text[skills_start:], re.IGNORECASE
        )
        skills_end = skills_start + next_section.start() if next_section else min(skills_start + 1500, len(text))
        
        skills_text = text[skills_start:skills_end]
        
        # Detectar se há categorias
        # Padrão: "Cloud:", "DevOps:", "Programação:", etc.
        category_pattern = r'^([A-Za-zÀ-ÿ\s/]+):\s*(.+)$'
        
        has_categories = False
        lines = skills_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Tentar match de categoria
            cat_match = re.match(category_pattern, line)
            if cat_match:
                has_categories = True
                category_name = cat_match.group(1).strip()
                skills_str = cat_match.group(2).strip()
                
                # Separar skills (pode ser vírgula, pipe, ponto-vírgula)
                skills_in_cat = re.split(r'[,;|]', skills_str)
                skills_in_cat = [s.strip() for s in skills_in_cat if s.strip() and len(s.strip()) > 1]
                
                if skills_in_cat:
                    # Normalizar nome da categoria
                    cat_key = unidecode(category_name.lower()).replace(' ', '_').replace('/', '_')
                    skills_by_category[cat_key] = skills_in_cat
                    skills_flat.extend(skills_in_cat)
        
        # Se não tem categorias, extrair como lista flat
        if not has_categories:
            for line in lines:
                line = line.strip()
                # Limpar bullets
                line = re.sub(r'^[-•*]\s*', '', line)
                if not line or len(line) < 2:
                    continue
                
                # Separar por delimitadores
                skills = re.split(r'[,;|]', line)
                for skill in skills:
                    skill = skill.strip()
                    if skill and len(skill) > 1 and skill not in skills_flat:
                        # Filtrar palavras não-técnicas
                        if skill.lower() not in ['júnior', 'junior', 'pleno', 'sênior', 'senior', 
                                                   'remoto', 'presencial', 'híbrido', 'hibrido']:
                            skills_flat.append(skill)
        
        return skills_flat, skills_by_category
    
    def _categorize_skills(self, keywords: List[KeywordMatch]) -> Dict[str, List[str]]:
        """Categoriza habilidades encontradas."""
        categories = {
            'cloud': [],
            'devops': [],
            'programacao': [],
            'banco_dados': [],
            'infra': [],
            'seguranca': [],
            'metodologias': [],
            'ferramentas': [],
            'outros': [],
        }
        
        # Palavras que NÃO são skills técnicas (filtrar)
        non_skills = {
            'júnior', 'junior', 'pleno', 'sênior', 'senior', 'remoto', 'presencial',
            'híbrido', 'hibrido', 'inglês', 'ingles', 'português', 'portugues',
            'espanhol', 'alemão', 'alemao', 'francês', 'frances', 'alta disponibilidade',
            'go'  # "go" sozinho pode ser falso positivo (golang deve ser explícito)
        }
        
        # Mapeamento de keywords para categorias
        category_mapping = {
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 's3', 'ec2', 'lambda', 'eks', 'ecs', 'glacier', 'rds', 'cloudformation'],
            'devops': ['docker', 'kubernetes', 'k8s', 'terraform', 'ansible', 'jenkins', 'gitlab', 'ci/cd', 'pipeline', 'helm', 'argocd'],
            'programacao': ['python', 'javascript', 'java', 'c#', 'csharp', 'golang', 'rust', 'php', 'ruby', 'typescript', 'nodejs', 'node.js', 'react', 'angular', 'vue', 'shell', 'bash', 'powershell'],
            'banco_dados': ['mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'oracle', 'sql', 'nosql', 'mariadb', 'elasticsearch', 'dynamodb'],
            'infra': ['linux', 'windows', 'nginx', 'apache', 'vmware', 'virtualização', 'virtualization', 'redes', 'tcp/ip', 'dns', 'dhcp', 'firewall', 'load balancer', 'haproxy', 'supervisor', 'gunicorn'],
            'seguranca': ['security', 'segurança', 'firewall', 'ssl', 'tls', 'vpn', 'iam', 'sso', 'oauth'],
            'metodologias': ['agile', 'scrum', 'kanban', 'itil', 'sre', 'lean', 'devops'],
            'ferramentas': ['git', 'jira', 'confluence', 'grafana', 'zabbix', 'prometheus', 'nagios', 'bitbucket', 'github', 'datadog'],
        }
        
        for kw in keywords:
            keyword_lower = kw.keyword.lower()
            
            # Filtrar palavras que não são skills
            if keyword_lower in non_skills:
                continue
            
            categorized = False
            
            for category, terms in category_mapping.items():
                if any(term in keyword_lower for term in terms):
                    if kw.keyword not in categories[category]:
                        categories[category].append(kw.keyword)
                    categorized = True
                    break
            
            if not categorized:
                # Colocar em "outros" apenas se for uma skill real
                if keyword_lower not in non_skills and kw.keyword not in categories['outros']:
                    categories['outros'].append(kw.keyword)
        
        # Remover categorias vazias e duplicatas
        return {k: list(set(v)) for k, v in categories.items() if v}
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extrai idiomas do currículo."""
        languages = []
        
        # Padrões de idiomas
        lang_patterns = [
            r'(portugu[êe]s|ingl[êe]s|espanhol|alem[ãa]o|franc[êe]s|italiano|mandarim|japon[êe]s|coreano)\s*[-–:]?\s*(nativo|fluente|avan[çc]ado|intermedi[áa]rio|b[áa]sico)?',
            r'(English|Spanish|Portuguese|German|French|Italian|Mandarin|Japanese|Korean)\s*[-–:]?\s*(native|fluent|advanced|intermediate|basic)?',
        ]
        
        text_lower = text.lower()
        
        for pattern in lang_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                lang = match.group(1).strip().title()
                level = match.group(2).strip().title() if match.group(2) else ""
                lang_str = f"{lang} ({level})" if level else lang
                if lang_str not in languages:
                    languages.append(lang_str)
        
        return languages[:10]
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extrai certificações do currículo."""
        certifications = []
        
        # Primeiro, tentar encontrar seção de certificações
        cert_section = None
        cert_headers = [
            r'certifica[çc][õo]es?[\s:]*\n',
            r'certificates?[\s:]*\n',
            r'qualifica[çc][õo]es?[\s:]*\n',
        ]
        
        for header in cert_headers:
            match = re.search(header, text, re.IGNORECASE)
            if match:
                start = match.end()
                # Encontrar fim da seção
                next_section = re.search(
                    r'\n\s*(experi[êe]ncia|forma[çc][aã]o|habilidades|idiomas|outras)',
                    text[start:], re.IGNORECASE
                )
                end = start + next_section.start() if next_section else min(start + 500, len(text))
                cert_section = text[start:end]
                break
        
        # Padrões de certificações conhecidas - apenas certificações formais
        cert_patterns = [
            r'(AWS\s+(?:Certified\s+)?(?:Solutions?\s*Architect|Developer|SysOps|DevOps|Cloud\s*Practitioner)[A-Za-z\s\-]*)',
            r'(Azure\s+(?:Certified\s+)?(?:Administrator|Developer|Solutions?\s*Architect|Fundamentals)[A-Za-z\s\-]*)',
            r'(Google\s+Cloud\s+(?:Certified\s+)?(?:Professional|Associate)[A-Za-z\s\-]*)',
            r'(LPIC[-\s]?\d+)',
            r'(Linux\s+(?:Professional\s+Institute|Foundation)\s+[A-Za-z\s\-]*)',
            r'(CompTIA\s+(?:A\+|Network\+|Security\+|Linux\+|Cloud\+)[A-Za-z\s\-]*)',
            r'(CCNA|CCNP|CCIE)',
            r'(Cisco\s+Certified\s+[A-Za-z\s\-]+)',
            r'(PMP|PMI\s+[A-Za-z\s\-]*)',
            r'(ITIL\s*(?:v?\d+|Foundation|Intermediate|Expert)?)',
            r'((?:Certified\s+)?Scrum\s*Master)',
            r'((?:Certified\s+)?Product\s*Owner)',
            r'(CKA|CKAD|CKS)',  # Siglas de certificação Kubernetes - não "kubernetes" sozinho
            r'((?:Certified\s+)?Kubernetes\s+(?:Administrator|Developer|Security))',
            r'(Docker\s+Certified\s+[A-Za-z\s\-]*)',
            r'(HashiCorp\s+(?:Certified\s+)?Terraform\s+(?:Associate|Professional))',
            r'(Red\s*Hat\s+(?:Certified\s+)?(?:System\s+)?(?:Administrator|Engineer))',
            r'(RHCSA|RHCE|RHCA)',
            r'(OCP|Oracle\s+Certified\s+[A-Za-z\s\-]*)',
            r'(MCSA|MCSE|Microsoft\s+Certified\s+[A-Za-z\s\-]*)',
        ]
        
        # Buscar no texto inteiro (ou na seção de certificações)
        search_text = cert_section if cert_section else text
        
        for pattern in cert_patterns:
            matches = re.finditer(pattern, search_text, re.IGNORECASE)
            for match in matches:
                cert = match.group(1).strip()
                # Filtrar termos muito genéricos
                if cert.lower() in ['kubernetes', 'docker', 'linux', 'aws', 'azure']:
                    continue
                if cert and cert not in certifications:
                    certifications.append(cert[:100])
        
        return certifications[:20]
    
    def _get_classification(self, score: int) -> Tuple[str, str]:
        """Retorna classificação e recomendação baseado no score."""
        if score >= 80:
            return (
                "Excelente",
                "🟢 Currículo otimizado para ATS - estrutura clara e keywords bem distribuídas"
            )
        elif score >= 60:
            return (
                "Bom",
                "🟢 Currículo adequado - pequenos ajustes podem melhorar a visibilidade"
            )
        elif score >= 40:
            return (
                "Regular",
                "🟡 Currículo precisa de melhorias - revise estrutura e adicione keywords"
            )
        else:
            return (
                "Fraco",
                "🔴 Currículo mal otimizado para ATS - considere reformular estrutura"
            )


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def format_analysis_result(result: ATSAnalysisResult) -> str:
    """
    Formata resultado da análise em texto legível.
    
    Args:
        result: Resultado da análise ATS
        
    Returns:
        String formatada para exibição
    """
    output = []
    output.append("=" * 60)
    output.append("📊 ANÁLISE ATS DO CURRÍCULO")
    output.append("=" * 60)
    output.append("")
    
    # Score principal
    output.append(f"🎯 SCORE FINAL: {result.final_score}/100 - {result.match_level}")
    output.append(f"   {result.recommendation}")
    output.append("")
    
    # Scores detalhados
    output.append("📈 SCORES DETALHADOS:")
    output.append(f"   • Keywords Técnicas: {result.keyword_score}/100")
    output.append(f"   • Estrutura: {result.structure_score}/100")
    output.append(f"   • Legibilidade ATS: {result.readability_score}/100")
    output.append("")
    
    # Keywords encontradas
    if result.keywords_found:
        output.append(f"🔑 KEYWORDS IDENTIFICADAS ({len(result.keywords_found)}):")
        critical = [k for k in result.keywords_found if k.importance == "critical"]
        if critical:
            output.append(f"   Críticas: {', '.join(k.keyword for k in critical[:10])}")
        others = [k for k in result.keywords_found if k.importance != "critical"]
        if others:
            output.append(f"   Outras: {', '.join(k.keyword for k in others[:10])}")
        output.append("")
    
    # Áreas identificadas
    if result.keywords_by_area:
        output.append("🎯 ÁREAS DE ATUAÇÃO:")
        for area, data in sorted(result.keywords_by_area.items(), 
                                  key=lambda x: x[1]['count'], reverse=True):
            output.append(f"   • {area.title()}: {data['count']} keywords")
        output.append("")
    
    # Seções
    output.append("📋 ESTRUTURA DO CURRÍCULO:")
    for section in result.sections_detected:
        output.append(f"   ✅ {section.name}")
    for section in result.sections_missing:
        output.append(f"   ❌ {section} (não encontrada)")
    output.append("")
    
    # Contato
    output.append("📞 DADOS DE CONTATO:")
    for key, value in result.contact_info.items():
        status = "✅" if value else "❌"
        output.append(f"   {status} {key.title()}: {value or 'Não encontrado'}")
    output.append("")
    
    # Feedback
    if result.warnings:
        output.append("⚠️ ALERTAS:")
        for w in result.warnings:
            output.append(f"   {w}")
        output.append("")
    
    if result.suggestions:
        output.append("💡 SUGESTÕES:")
        for s in result.suggestions:
            output.append(f"   {s}")
        output.append("")
    
    if result.positives:
        output.append("✅ PONTOS POSITIVOS:")
        for p in result.positives:
            output.append(f"   {p}")
        output.append("")
    
    # Metadados
    output.append("-" * 60)
    output.append(f"Total de palavras: {result.total_words}")
    output.append(f"Keywords únicas: {result.unique_keywords}")
    output.append(f"Tempo de processamento: {result.processing_time_ms}ms")
    
    return "\n".join(output)
