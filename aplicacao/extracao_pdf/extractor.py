"""
Módulo de Extração de Texto de PDFs

Utiliza PyMuPDF (fitz) para extrair texto de arquivos PDF.
Otimizado para currículos, mantendo estrutura e formatação.
"""

import fitz  # PyMuPDF
import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ExtractionResult:
    """Resultado da extração de PDF"""
    text: str
    page_count: int
    char_count: int
    word_count: int
    has_images: bool
    has_tables: bool
    warnings: List[str]
    sections_detected: List[str]


class PDFExtractor:
    """
    Extrator de texto de PDFs otimizado para currículos.
    
    Features:
    - Extração de texto com preservação de estrutura
    - Detecção de imagens (que ATS não lê)
    - Detecção de tabelas (problemáticas para ATS)
    - Identificação de seções do currículo
    """
    
    # Padrões de seções comuns em currículos
    SECTION_PATTERNS = [
        (r'(?:dados?\s*pessoais?|informa[çc][õo]es?\s*pessoais?)', 'Dados Pessoais'),
        (r'(?:objetivo|objetivo\s*profissional)', 'Objetivo'),
        (r'(?:resumo|resumo\s*profissional|sobre\s*mim|perfil)', 'Resumo'),
        (r'(?:experi[êe]ncia|experi[êe]ncias?\s*profissionais?)', 'Experiência'),
        (r'(?:forma[çc][ãa]o|educa[çc][ãa]o|forma[çc][ãa]o\s*acad[êe]mica)', 'Formação'),
        (r'(?:habilidades?|compet[êe]ncias?|skills?)', 'Habilidades'),
        (r'(?:idiomas?|l[íi]nguas?)', 'Idiomas'),
        (r'(?:certifica[çc][õo]es?|cursos?)', 'Certificações'),
        (r'(?:projetos?|portfolio)', 'Projetos'),
        (r'(?:refer[êe]ncias?)', 'Referências'),
    ]
    
    def __init__(self):
        self.warnings: List[str] = []
    
    def extract(self, pdf_path: str) -> ExtractionResult:
        """
        Extrai texto de um arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            ExtractionResult com texto e metadados
        """
        self.warnings = []
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise ValueError(f"Erro ao abrir PDF: {str(e)}")
        
        text_blocks: List[str] = []
        has_images = False
        has_tables = False
        
        for page_num, page in enumerate(doc, 1):
            # Extrair texto
            page_text = page.get_text("text")
            text_blocks.append(page_text)
            
            # Verificar imagens
            image_list = page.get_images(full=True)
            if image_list:
                has_images = True
                self.warnings.append(
                    f"⚠️ Página {page_num}: Contém {len(image_list)} imagem(ns). "
                    "Sistemas ATS não leem conteúdo de imagens."
                )
            
            # Verificar tabelas (heurística: muitas células alinhadas)
            if self._detect_tables(page):
                has_tables = True
                self.warnings.append(
                    f"⚠️ Página {page_num}: Possível tabela detectada. "
                    "Tabelas podem ser mal interpretadas por sistemas ATS."
                )
        
        # Combinar texto
        full_text = "\n".join(text_blocks)
        
        # Limpar texto
        full_text = self._clean_text(full_text)
        
        # Detectar seções
        sections = self._detect_sections(full_text)
        
        # Estatísticas
        words = full_text.split()
        
        # Validações ATS
        self._validate_ats_compatibility(full_text, len(words))
        
        doc.close()
        
        return ExtractionResult(
            text=full_text,
            page_count=len(text_blocks),
            char_count=len(full_text),
            word_count=len(words),
            has_images=has_images,
            has_tables=has_tables,
            warnings=self.warnings,
            sections_detected=sections
        )
    
    def extract_from_bytes(self, pdf_bytes: bytes) -> ExtractionResult:
        """
        Extrai texto de bytes de PDF (upload via web).
        
        Args:
            pdf_bytes: Bytes do arquivo PDF
            
        Returns:
            ExtractionResult com texto e metadados
        """
        self.warnings = []
        
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Erro ao processar PDF: {str(e)}")
        
        text_blocks: List[str] = []
        has_images = False
        has_tables = False
        
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text("text")
            text_blocks.append(page_text)
            
            image_list = page.get_images(full=True)
            if image_list:
                has_images = True
                self.warnings.append(
                    f"⚠️ Página {page_num}: Contém {len(image_list)} imagem(ns). "
                    "Sistemas ATS não leem conteúdo de imagens."
                )
            
            if self._detect_tables(page):
                has_tables = True
                self.warnings.append(
                    f"⚠️ Página {page_num}: Possível tabela detectada. "
                    "Tabelas podem ser mal interpretadas por sistemas ATS."
                )
        
        full_text = "\n".join(text_blocks)
        full_text = self._clean_text(full_text)
        sections = self._detect_sections(full_text)
        words = full_text.split()
        self._validate_ats_compatibility(full_text, len(words))
        
        doc.close()
        
        return ExtractionResult(
            text=full_text,
            page_count=len(text_blocks),
            char_count=len(full_text),
            word_count=len(words),
            has_images=has_images,
            has_tables=has_tables,
            warnings=self.warnings,
            sections_detected=sections
        )
    
    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto extraído."""
        # Remover múltiplas quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remover espaços múltiplos
        text = re.sub(r' {2,}', ' ', text)
        # Remover linhas só com espaços
        text = re.sub(r'^\s+$', '', text, flags=re.MULTILINE)
        # Strip geral
        text = text.strip()
        return text
    
    def _detect_tables(self, page) -> bool:
        """Detecta se página contém tabelas (heurística)."""
        # Verificar se há muitos blocos de texto alinhados horizontalmente
        blocks = page.get_text("blocks")
        if len(blocks) < 3:
            return False
        
        # Verificar alinhamento vertical (característica de tabelas)
        x_positions = [block[0] for block in blocks if len(block) >= 5]
        if len(x_positions) < 3:
            return False
        
        # Se muitas posições X se repetem, pode ser tabela
        x_counts = {}
        for x in x_positions:
            x_rounded = round(x, -1)  # Arredondar para dezenas
            x_counts[x_rounded] = x_counts.get(x_rounded, 0) + 1
        
        # Se mais de 3 blocos na mesma coluna, provavelmente é tabela
        return any(count >= 3 for count in x_counts.values())
    
    def _detect_sections(self, text: str) -> List[str]:
        """Detecta seções do currículo no texto."""
        text_lower = text.lower()
        found_sections = []
        
        for pattern, name in self.SECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                found_sections.append(name)
        
        return found_sections
    
    def _validate_ats_compatibility(self, text: str, word_count: int):
        """Adiciona warnings de compatibilidade ATS."""
        
        # Verificar tamanho
        if word_count < 100:
            self.warnings.append(
                "⚠️ Currículo muito curto (menos de 100 palavras). "
                "Pode parecer incompleto para sistemas ATS."
            )
        elif word_count > 1500:
            self.warnings.append(
                "⚠️ Currículo muito extenso (mais de 1500 palavras). "
                "Considere condensar para 1-2 páginas."
            )
        
        # Verificar caracteres especiais problemáticos
        special_chars = re.findall(r'[►▪●○◦■□▸‣⁃]', text)
        if special_chars:
            self.warnings.append(
                "⚠️ Caracteres especiais de bullet points detectados. "
                "Prefira usar • ou - para melhor compatibilidade ATS."
            )
        
        # Verificar se há email
        if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            self.warnings.append(
                "⚠️ Nenhum email detectado no currículo. "
                "Certifique-se de incluir formas de contato."
            )
        
        # Verificar se há telefone
        phone_pattern = r'(?:\+55\s?)?\(?[1-9]{2}\)?\s?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}'
        if not re.search(phone_pattern, text):
            self.warnings.append(
                "⚠️ Nenhum telefone detectado no currículo. "
                "Adicione um número para contato."
            )
