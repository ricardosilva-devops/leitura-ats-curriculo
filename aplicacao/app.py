"""
Aplicação Flask - Leitura ATS de Currículos Técnicos

Plataforma web para análise heurística de currículos técnicos em PDF,
identificando palavras-chave da área de TI e verificando estrutura para legibilidade automatizada.
"""

import os
import sys
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify

# Adicionar diretório atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from validators import upload_validator
from utils import success_response, error_response, ERROR_MESSAGES, AnalysisLogger
from extracao_pdf.extractor import PDFExtractor
from leitura_ats.engine import ATSEngine, ATSAnalysisResult


# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =============================================================================

def create_app(config_class=None):
    """
    Factory function para criar a aplicação Flask.
    
    Args:
        config_class: Classe de configuração (opcional, detecta automaticamente)
    
    Returns:
        Aplicação Flask configurada
    """
    app = Flask(__name__)
    
    # Carregar configuração
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # Configurar logging
    _configure_logging(app)
    
    # Inicializar logger de análises com config da app
    _init_analysis_logger(app)
    
    # Registrar rotas
    _register_routes(app)
    
    # Registrar handlers de erro
    _register_error_handlers(app)
    
    # Adicionar headers de segurança
    _register_security_headers(app)
    
    return app


def _configure_logging(app):
    """Configura logging da aplicação."""
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not app.config.get('DEBUG'):
        # Em produção, reduzir verbosidade de bibliotecas externas
        logging.getLogger('werkzeug').setLevel(logging.WARNING)


def _register_security_headers(app):
    """Adiciona headers de segurança HTTP em todas as respostas."""
    @app.after_request
    def add_security_headers(response):
        # Proteção contra XSS
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Controle de cache para respostas sensíveis
        if request.endpoint == 'analyze':
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        
        # CSP básico (permite recursos locais)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'"
        )
        
        return response


# Instâncias globais dos engines (reutilizadas entre requests)
pdf_extractor = PDFExtractor()
ats_engine = ATSEngine()

# Logger de análises - será inicializado com config da app
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
analysis_logger = None  # Inicializado em create_app()


def _init_analysis_logger(app):
    """Inicializa logger de análises com configuração da app."""
    global analysis_logger
    analysis_logger = AnalysisLogger(
        log_dir=LOG_DIR,
        detailed=app.config.get('LOG_DETAILED', False)
    )


# =============================================================================
# HELPERS
# =============================================================================

def result_to_dict(result: ATSAnalysisResult) -> dict:
    """Converte ATSAnalysisResult para dict serializável em JSON."""
    response = {
        "final_score": result.final_score,
        "keyword_score": result.keyword_score,
        "structure_score": result.structure_score,
        "readability_score": result.readability_score,
        "match_level": result.match_level,
        "recommendation": result.recommendation,
        "keywords_found": [
            {
                "keyword": k.keyword,
                "found_as": k.found_as,
                "match_type": k.match_type,
                "importance": k.importance
            }
            for k in result.keywords_found
        ],
        "keywords_critical": result.keywords_critical,
        "keywords_by_area": result.keywords_by_area,
        "sections_detected": [
            {"name": s.name, "detected": s.detected}
            for s in result.sections_detected
        ],
        "sections_missing": result.sections_missing,
        "contact_info": result.contact_info,
        "warnings": result.warnings,
        "suggestions": result.suggestions,
        "positives": result.positives,
        # Novos campos
        "ats_checklist": [
            {
                "item": c.item,
                "passed": c.passed,
                "category": c.category,
                "severity": c.severity,
                "suggestion": c.suggestion
            }
            for c in result.ats_checklist
        ],
        "metrics_found": result.metrics_found,
        "action_verbs_found": result.action_verbs_found,
        "date_format_valid": result.date_format_valid,
        # Metadados
        "total_words": result.total_words,
        "unique_keywords": result.unique_keywords,
        "processing_time_ms": result.processing_time_ms
    }
    
    # Adicionar dados estruturados extraídos
    if result.extracted_data:
        ed = result.extracted_data
        response["extracted_data"] = {
            "name": ed.name,
            "email": ed.email,
            "phone": ed.phone,
            "linkedin": ed.linkedin,
            "location": ed.location,
            "summary": ed.summary,
            "objective": ed.objective,
            "experiences": [
                {
                    "company": exp.company,
                    "role": exp.role,
                    "period": exp.period,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "description": exp.description
                }
                for exp in ed.experiences
            ],
            "education": [
                {
                    "course": edu.course,
                    "institution": edu.institution,
                    "period": edu.period,
                    "start_date": edu.start_date,
                    "end_date": edu.end_date,
                    "status": edu.status
                }
                for edu in ed.education
            ],
            "skills": ed.skills,
            "skills_by_category": ed.skills_by_category,
            "languages": ed.languages,
            "certifications": ed.certifications
        }
    
    return response


# =============================================================================
# ROTAS (registradas via função)
# =============================================================================

def _register_routes(app):
    """Registra todas as rotas da aplicação."""
    
    @app.route('/')
    def index():
        """Página principal com formulário de upload."""
        return render_template('index.html')
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        """
        Endpoint para análise de currículo técnico em PDF.
        
        Validações:
        - Presença do arquivo
        - Extensão .pdf
        - MIME type application/pdf
        - Magic bytes de PDF válidos
        
        Returns:
            JSON com análise ATS completa ou erro padronizado
        """
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return error_response(ERROR_MESSAGES["no_file"], 400, "NO_FILE")
        
        file = request.files['file']
        
        # Verificar se arquivo foi selecionado
        if file.filename == '':
            return error_response(ERROR_MESSAGES["no_file_selected"], 400, "NO_FILE_SELECTED")
        
        # Validação robusta do arquivo (extensão + MIME + magic bytes)
        is_valid, validation_error = upload_validator.validate(file)
        if not is_valid:
            return error_response(validation_error, 400, "INVALID_FILE")
        
        # Sanitizar nome do arquivo
        safe_filename = upload_validator.sanitize_filename(file.filename)
        
        try:
            # Ler bytes do arquivo
            pdf_bytes = file.read()
            
            # Verificar tamanho
            max_size = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
            if len(pdf_bytes) > max_size:
                return error_response(ERROR_MESSAGES["file_too_large"], 413, "FILE_TOO_LARGE")
            
            # Extrair texto do PDF
            extraction_result = pdf_extractor.extract_from_bytes(pdf_bytes)
            
            # Verificar se extraiu algo
            if not extraction_result.text.strip():
                return error_response(ERROR_MESSAGES["empty_pdf"], 400, "EMPTY_PDF")
            
            # Executar análise ATS
            ats_result = ats_engine.analyze(extraction_result.text)
            
            # Preparar resposta
            response_data = {
                "extraction": {
                    "page_count": extraction_result.page_count,
                    "word_count": extraction_result.word_count,
                    "char_count": extraction_result.char_count,
                    "has_images": extraction_result.has_images,
                    "has_tables": extraction_result.has_tables,
                    "warnings": extraction_result.warnings,
                    "sections_detected": extraction_result.sections_detected,
                    "text_preview": extraction_result.text[:500] + "..." if len(extraction_result.text) > 500 else extraction_result.text
                },
                "analysis": result_to_dict(ats_result)
            }
            
            # Salvar log (respeitando configuração de privacidade)
            try:
                analysis_logger.log_analysis(
                    filename=safe_filename,
                    extracted_text=extraction_result.text,
                    response=response_data,
                    logger=app.logger
                )
            except Exception as log_error:
                app.logger.warning(f"Falha ao salvar log: {log_error}")
            
            return success_response(response_data)
        
        except ValueError as e:
            return error_response(str(e), 400, "VALIDATION_ERROR")
        
        except Exception as e:
            # Log do erro real para debugging (sem expor ao usuário)
            app.logger.error(f"Erro ao processar PDF: {str(e)}", exc_info=True)
            return error_response(ERROR_MESSAGES["processing_error"], 500, "PROCESSING_ERROR")
    
    @app.route('/health')
    def health():
        """
        Endpoint de health check.
        
        Retorna status básico sem expor informações sensíveis.
        """
        return jsonify({
            "status": "healthy",
            "service": "leitura-ats-curriculo"
        })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

def _register_error_handlers(app):
    """Registra handlers de erro globais."""
    
    @app.errorhandler(413)
    def too_large(e):
        """Handler para arquivo muito grande."""
        return error_response(ERROR_MESSAGES["file_too_large"], 413, "FILE_TOO_LARGE")
    
    @app.errorhandler(500)
    def server_error(e):
        """Handler para erro interno."""
        app.logger.error(f"Erro interno: {e}", exc_info=True)
        return error_response(ERROR_MESSAGES["internal_error"], 500, "INTERNAL_ERROR")
    
    @app.errorhandler(404)
    def not_found(e):
        """Handler para rota não encontrada."""
        return error_response("Recurso não encontrado", 404, "NOT_FOUND")


# =============================================================================
# COMPATIBILIDADE / CRIAÇÃO DA APLICAÇÃO
# =============================================================================

# Criar instância global para compatibilidade com wsgi.py e gunicorn
app = create_app()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Em desenvolvimento, usar servidor Flask built-in
    # Em produção, usar gunicorn via wsgi.py
    import sys
    
    # Verificar se está em modo de produção
    env = os.environ.get('FLASK_ENV', os.environ.get('APP_ENV', 'development'))
    
    if env == 'production':
        print("⚠️  Modo produção detectado. Use gunicorn em vez de app.run().")
        print("   Comando: gunicorn -c gunicorn_config.py wsgi:application")
        sys.exit(1)
    
    # Desenvolvimento: rodar com debug
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
