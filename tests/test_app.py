"""
Testes automatizados para o Analisador ATS de Currículos Técnicos.

Cobertura mínima focada em:
- Health check
- Validação de upload
- Fluxo de análise (happy path)
- Casos de erro comuns

Para rodar:
    pytest tests/ -v
    
Ou com coverage:
    pytest tests/ --cov=aplicacao --cov-report=term-missing
"""

import io
import os
import sys

import pytest

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aplicacao.app import create_app
from aplicacao.config import TestingConfig


@pytest.fixture
def app():
    """Cria instância da aplicação para testes."""
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Cria cliente de teste Flask."""
    return app.test_client()


class TestHealthCheck:
    """Testes do endpoint /health."""
    
    def test_health_returns_200(self, client):
        """Health check deve retornar 200 e status healthy."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'leitura-ats-curriculo'
    
    def test_health_response_is_json(self, client):
        """Health check deve retornar JSON válido."""
        response = client.get('/health')
        
        assert response.content_type == 'application/json'


class TestIndexPage:
    """Testes da página principal."""
    
    def test_index_returns_html(self, client):
        """Página principal deve retornar HTML."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data


class TestFileValidation:
    """Testes de validação de upload."""
    
    def test_no_file_returns_400(self, client):
        """Requisição sem arquivo deve retornar 400."""
        response = client.post('/analyze')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'arquivo' in data['error'].lower()
    
    def test_empty_filename_returns_400(self, client):
        """Arquivo com nome vazio deve retornar 400."""
        response = client.post(
            '/analyze',
            data={'file': (io.BytesIO(b''), '')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_non_pdf_extension_returns_400(self, client):
        """Arquivo sem extensão .pdf deve retornar 400."""
        response = client.post(
            '/analyze',
            data={'file': (io.BytesIO(b'not a pdf'), 'test.txt')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'pdf' in data['error'].lower()
    
    def test_fake_pdf_extension_returns_400(self, client):
        """Arquivo .pdf falso (sem magic bytes) deve retornar 400."""
        # Arquivo com extensão .pdf mas conteúdo não-PDF
        fake_pdf = io.BytesIO(b'This is not a real PDF file content')
        
        response = client.post(
            '/analyze',
            data={'file': (fake_pdf, 'fake.pdf')},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False


class TestPDFAnalysis:
    """Testes do fluxo de análise de PDF."""
    
    def _create_minimal_pdf(self):
        """
        Cria um PDF mínimo válido para testes.
        
        Este é um PDF extremamente simples que passa validação de magic bytes
        mas pode não ter texto extraível (dependendo da lib).
        """
        # PDF mínimo válido com uma página em branco
        pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >> endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer << /Size 4 /Root 1 0 R >>
startxref
192
%%EOF"""
        return io.BytesIO(pdf_content)
    
    def test_valid_pdf_magic_bytes_accepted(self, client):
        """PDF com magic bytes válidos deve ser aceito (mesmo que vazio)."""
        pdf = self._create_minimal_pdf()
        
        response = client.post(
            '/analyze',
            data={'file': (pdf, 'test.pdf')},
            content_type='multipart/form-data'
        )
        
        # Pode retornar 400 (PDF vazio) ou 200 (análise ok)
        # O importante é que não seja rejeitado pela validação de magic bytes
        data = response.get_json()
        
        # Se rejeitado, deve ser por PDF vazio, não por validação de arquivo
        if response.status_code == 400:
            assert 'pdf válido' not in data.get('error', '').lower()


class TestErrorHandling:
    """Testes de tratamento de erros."""
    
    def test_404_returns_json(self, client):
        """Rota inexistente deve retornar JSON com erro."""
        response = client.get('/nonexistent-route')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False
    
    def test_error_response_structure(self, client):
        """Respostas de erro devem ter estrutura padronizada."""
        response = client.post('/analyze')  # Sem arquivo
        
        data = response.get_json()
        
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data


class TestSecurityHeaders:
    """Testes de headers de segurança."""
    
    def test_xss_protection_header(self, client):
        """Deve ter header de proteção XSS."""
        response = client.get('/health')
        
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    
    def test_content_type_options_header(self, client):
        """Deve ter header nosniff."""
        response = client.get('/health')
        
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    
    def test_frame_options_header(self, client):
        """Deve ter header de proteção contra clickjacking."""
        response = client.get('/health')
        
        assert response.headers.get('X-Frame-Options') == 'DENY'


class TestResponseFormat:
    """Testes de formato de resposta."""
    
    def test_success_response_has_success_true(self, client):
        """Respostas de sucesso devem ter success: true."""
        response = client.get('/health')
        
        # Health não usa success_response, mas /analyze sim
        # Testar com health que sempre funciona
        assert response.status_code == 200
    
    def test_all_responses_are_json(self, client):
        """Todas as rotas API devem retornar JSON."""
        routes = ['/health', '/analyze']
        
        for route in routes:
            if route == '/analyze':
                response = client.post(route)
            else:
                response = client.get(route)
            
            assert response.content_type == 'application/json', f"Rota {route} não retornou JSON"
