"""
Validadores de upload de arquivo.

Validação robusta de arquivos PDF com:
- Verificação de extensão
- Verificação de MIME type
- Verificação de magic bytes (assinatura do arquivo)
- Sanitização de nome de arquivo
- Verificação de tamanho
"""

import re
from typing import Tuple, Optional
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


class FileValidationError(Exception):
    """Erro de validação de arquivo."""
    pass


class UploadValidator:
    """
    Validador de uploads de PDF.
    
    Implementa múltiplas camadas de validação para segurança:
    1. Extensão do arquivo
    2. MIME type reportado
    3. Magic bytes (assinatura real do arquivo)
    4. Tamanho do arquivo
    """
    
    # Magic bytes de PDF
    PDF_MAGIC = b'%PDF'
    
    # MIME types aceitos
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/x-pdf',  # Variante menos comum
    }
    
    # Extensões aceitas
    ALLOWED_EXTENSIONS = {'pdf'}
    
    def __init__(self, max_size_bytes: int = 16 * 1024 * 1024):
        """
        Args:
            max_size_bytes: Tamanho máximo em bytes (default: 16MB)
        """
        self.max_size_bytes = max_size_bytes
    
    def validate(self, file: FileStorage) -> Tuple[bool, Optional[str]]:
        """
        Valida arquivo de upload.
        
        Args:
            file: Objeto FileStorage do Flask/Werkzeug
            
        Returns:
            Tuple (é_válido, mensagem_erro)
        """
        # 1. Verificar se arquivo foi enviado
        if file is None:
            return False, "Nenhum arquivo enviado"
        
        # 2. Verificar nome do arquivo
        if not file.filename or file.filename == '':
            return False, "Nenhum arquivo selecionado"
        
        # 3. Verificar extensão
        if not self._has_valid_extension(file.filename):
            return False, "Apenas arquivos PDF são aceitos"
        
        # 4. Verificar MIME type
        if not self._has_valid_mime_type(file):
            return False, "Tipo de arquivo inválido. Envie um PDF válido"
        
        # 5. Verificar magic bytes (assinatura real do arquivo)
        if not self._has_valid_magic_bytes(file):
            return False, "Arquivo não é um PDF válido"
        
        return True, None
    
    def validate_size(self, content_length: Optional[int]) -> Tuple[bool, Optional[str]]:
        """
        Valida tamanho do arquivo antes do upload.
        
        Args:
            content_length: Tamanho reportado no header Content-Length
            
        Returns:
            Tuple (é_válido, mensagem_erro)
        """
        if content_length and content_length > self.max_size_bytes:
            max_mb = self.max_size_bytes // (1024 * 1024)
            return False, f"Arquivo muito grande. O tamanho máximo é {max_mb}MB"
        return True, None
    
    def _has_valid_extension(self, filename: str) -> bool:
        """Verifica se extensão é permitida."""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.ALLOWED_EXTENSIONS
    
    def _has_valid_mime_type(self, file: FileStorage) -> bool:
        """Verifica MIME type reportado."""
        # content_type pode ser None em alguns casos
        if not file.content_type:
            return False
        return file.content_type.lower() in self.ALLOWED_MIME_TYPES
    
    def _has_valid_magic_bytes(self, file: FileStorage) -> bool:
        """
        Verifica assinatura real do arquivo (magic bytes).
        
        PDF começa com '%PDF' (0x25 0x50 0x44 0x46)
        """
        # Salvar posição atual
        current_pos = file.stream.tell()
        
        try:
            # Ir para início e ler primeiros bytes
            file.stream.seek(0)
            header = file.stream.read(4)
            
            # Verificar assinatura PDF
            return header == self.PDF_MAGIC
        finally:
            # Restaurar posição original
            file.stream.seek(current_pos)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitiza nome do arquivo para segurança.
        
        Remove caracteres perigosos e normaliza o nome.
        """
        # Usar secure_filename do Werkzeug
        safe_name = secure_filename(filename)
        
        # Se ficou vazio, usar nome genérico
        if not safe_name:
            safe_name = "documento.pdf"
        
        # Garantir extensão .pdf
        if not safe_name.lower().endswith('.pdf'):
            safe_name += '.pdf'
        
        # Limitar tamanho do nome
        if len(safe_name) > 100:
            safe_name = safe_name[:96] + '.pdf'
        
        return safe_name


# Instância padrão para uso direto
upload_validator = UploadValidator()
