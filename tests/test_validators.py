"""
Testes do módulo de validação de upload.
"""

import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aplicacao.validators.upload import UploadValidator


@pytest.fixture
def validator():
    """Instância do validador para testes."""
    return UploadValidator()


class TestExtensionValidation:
    """Testes de validação de extensão."""
    
    def test_pdf_extension_allowed(self, validator):
        """Extensão .pdf deve ser permitida."""
        assert validator._is_allowed_extension('document.pdf')
        assert validator._is_allowed_extension('DOCUMENT.PDF')
        assert validator._is_allowed_extension('my.file.pdf')
    
    def test_non_pdf_extension_rejected(self, validator):
        """Outras extensões devem ser rejeitadas."""
        assert not validator._is_allowed_extension('document.txt')
        assert not validator._is_allowed_extension('document.doc')
        assert not validator._is_allowed_extension('document.docx')
        assert not validator._is_allowed_extension('image.png')
        assert not validator._is_allowed_extension('script.py')


class TestMagicBytes:
    """Testes de validação de magic bytes."""
    
    def test_valid_pdf_magic_bytes(self, validator):
        """Arquivo com magic bytes de PDF deve passar."""
        pdf_content = b'%PDF-1.4 rest of content...'
        file_stream = io.BytesIO(pdf_content)
        
        assert validator._has_valid_magic_bytes(file_stream)
    
    def test_invalid_magic_bytes(self, validator):
        """Arquivo sem magic bytes de PDF deve falhar."""
        txt_content = b'This is just a text file'
        file_stream = io.BytesIO(txt_content)
        
        assert not validator._has_valid_magic_bytes(file_stream)
    
    def test_empty_file_magic_bytes(self, validator):
        """Arquivo vazio deve falhar validação de magic bytes."""
        empty_stream = io.BytesIO(b'')
        
        assert not validator._has_valid_magic_bytes(empty_stream)
    
    def test_stream_position_restored(self, validator):
        """Posição do stream deve ser restaurada após verificação."""
        content = b'%PDF-1.4 content here'
        file_stream = io.BytesIO(content)
        file_stream.seek(10)  # Mover posição
        
        validator._has_valid_magic_bytes(file_stream)
        
        assert file_stream.tell() == 0  # Deve voltar ao início


class TestFilenameSanitization:
    """Testes de sanitização de nome de arquivo."""
    
    def test_normal_filename_unchanged(self, validator):
        """Nome normal deve permanecer similar."""
        result = validator.sanitize_filename('meu_curriculo.pdf')
        
        assert result.endswith('.pdf')
        assert 'curriculo' in result.lower()
    
    def test_path_traversal_blocked(self, validator):
        """Tentativa de path traversal deve ser bloqueada."""
        result = validator.sanitize_filename('../../../etc/passwd.pdf')
        
        assert '..' not in result
        assert '/' not in result
        assert result.endswith('.pdf')
    
    def test_special_chars_removed(self, validator):
        """Caracteres especiais devem ser removidos."""
        result = validator.sanitize_filename('currículo<script>.pdf')
        
        assert '<' not in result
        assert '>' not in result
    
    def test_long_filename_truncated(self, validator):
        """Nomes muito longos devem ser truncados."""
        long_name = 'a' * 300 + '.pdf'
        result = validator.sanitize_filename(long_name)
        
        assert len(result) <= 255
        assert result.endswith('.pdf')
    
    def test_empty_filename_returns_default(self, validator):
        """Nome vazio deve retornar nome padrão."""
        result = validator.sanitize_filename('')
        
        assert result.endswith('.pdf')
        assert len(result) > 4


class TestSizeValidation:
    """Testes de validação de tamanho."""
    
    def test_small_file_passes(self, validator):
        """Arquivo pequeno deve passar."""
        is_valid, error = validator.validate_size(1000)  # 1KB
        
        assert is_valid
        assert error is None
    
    def test_large_file_fails(self, validator):
        """Arquivo muito grande deve falhar."""
        is_valid, error = validator.validate_size(100 * 1024 * 1024)  # 100MB
        
        assert not is_valid
        assert error is not None
        assert 'grande' in error.lower() or 'size' in error.lower()
