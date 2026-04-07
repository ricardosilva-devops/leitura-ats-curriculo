"""
Aplicação Flask - Leitura ATS de Currículos

Plataforma web para análise de currículos em PDF,
identificando palavras-chave e verificando compatibilidade ATS.
"""

import os
import json
from datetime import datetime
from dataclasses import asdict
from flask import Flask, render_template, request, jsonify

import sys
import os

# Adicionar diretório atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extracao_pdf.extractor import PDFExtractor
from leitura_ats.engine import ATSEngine, ATSAnalysisResult, format_analysis_result


# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =============================================================================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Instâncias dos engines
pdf_extractor = PDFExtractor()
ats_engine = ATSEngine()


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
# LOGGING
# =============================================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')

def save_analysis_log(filename: str, extracted_text: str, response: dict):
    """Salva log detalhado da análise em arquivo TXT."""
    # Criar diretório de logs se não existir
    os.makedirs(LOG_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"analise_{timestamp}.txt"
    log_path = os.path.join(LOG_DIR, log_filename)
    
    analysis = response.get("analysis", {})
    extracted_data = analysis.get("extracted_data", {})
    
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"LOG DE ANÁLISE ATS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Arquivo: {filename}\n")
        f.write(f"Páginas: {response['extraction']['page_count']}\n")
        f.write(f"Palavras: {response['extraction']['word_count']}\n")
        f.write(f"Tempo de processamento: {analysis.get('processing_time_ms', 0)}ms\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("SCORES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Score Final: {analysis.get('final_score', 0)}/100\n")
        f.write(f"Keywords: {analysis.get('keyword_score', 0)}/100\n")
        f.write(f"Estrutura: {analysis.get('structure_score', 0)}/100\n")
        f.write(f"Legibilidade: {analysis.get('readability_score', 0)}/100\n")
        f.write(f"Classificação: {analysis.get('match_level', '-')}\n")
        f.write(f"Recomendação: {analysis.get('recommendation', '-')}\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("TEXTO EXTRAÍDO DO PDF\n")
        f.write("-" * 80 + "\n")
        f.write(extracted_text + "\n\n")
        
        f.write("-" * 80 + "\n")
        f.write("DADOS ESTRUTURADOS EXTRAÍDOS\n")
        f.write("-" * 80 + "\n\n")
        
        if extracted_data:
            f.write(">>> DADOS PESSOAIS:\n")
            f.write(f"    Nome: {extracted_data.get('name', 'NÃO ENCONTRADO')}\n")
            f.write(f"    Email: {extracted_data.get('email', 'NÃO ENCONTRADO')}\n")
            f.write(f"    Telefone: {extracted_data.get('phone', 'NÃO ENCONTRADO')}\n")
            f.write(f"    LinkedIn: {extracted_data.get('linkedin', 'NÃO ENCONTRADO')}\n")
            f.write(f"    Localização: {extracted_data.get('location', 'NÃO ENCONTRADO')}\n")
            f.write("\n")
            
            f.write(">>> RESUMO PROFISSIONAL:\n")
            summary = extracted_data.get('summary', '')
            f.write(f"    {summary if summary else 'NÃO ENCONTRADO'}\n")
            f.write("\n")
            
            f.write(">>> OBJETIVO:\n")
            objective = extracted_data.get('objective', '')
            f.write(f"    {objective if objective else 'NÃO ENCONTRADO'}\n")
            f.write("\n")
            
            f.write(">>> EXPERIÊNCIAS PROFISSIONAIS:\n")
            experiences = extracted_data.get('experiences', [])
            if experiences:
                for i, exp in enumerate(experiences, 1):
                    f.write(f"\n    [{i}] {exp.get('role', 'Cargo não identificado')}\n")
                    f.write(f"        Empresa: {exp.get('company', 'Não identificada')}\n")
                    f.write(f"        Período: {exp.get('period', 'Não identificado')}\n")
                    f.write(f"        Data Início: {exp.get('start_date', '-')}\n")
                    f.write(f"        Data Fim: {exp.get('end_date', '-')}\n")
                    f.write(f"        Descrição: {exp.get('description', '-')[:200]}...\n")
            else:
                f.write("    NÃO ENCONTRADAS\n")
            f.write("\n")
            
            f.write(">>> FORMAÇÃO ACADÊMICA:\n")
            education = extracted_data.get('education', [])
            if education:
                for edu in education:
                    f.write(f"    - {edu}\n")
            else:
                f.write("    NÃO ENCONTRADA\n")
            f.write("\n")
            
            f.write(">>> HABILIDADES POR CATEGORIA:\n")
            skills_by_cat = extracted_data.get('skills_by_category', {})
            if skills_by_cat:
                for cat, skills in skills_by_cat.items():
                    f.write(f"    {cat.upper()}: {', '.join(skills)}\n")
            else:
                f.write("    NÃO CATEGORIZADAS\n")
            f.write("\n")
            
            f.write(">>> TODAS AS SKILLS ENCONTRADAS:\n")
            skills = extracted_data.get('skills', [])
            if skills:
                f.write(f"    {', '.join(skills)}\n")
            else:
                f.write("    NENHUMA\n")
            f.write("\n")
            
            f.write(">>> IDIOMAS:\n")
            languages = extracted_data.get('languages', [])
            if languages:
                for lang in languages:
                    f.write(f"    - {lang}\n")
            else:
                f.write("    NÃO ENCONTRADOS\n")
            f.write("\n")
            
            f.write(">>> CERTIFICAÇÕES:\n")
            certifications = extracted_data.get('certifications', [])
            if certifications:
                for cert in certifications:
                    f.write(f"    - {cert}\n")
            else:
                f.write("    NÃO ENCONTRADAS\n")
        else:
            f.write("NENHUM DADO ESTRUTURADO FOI EXTRAÍDO\n")
        
        f.write("\n")
        f.write("-" * 80 + "\n")
        f.write("KEYWORDS IDENTIFICADAS\n")
        f.write("-" * 80 + "\n")
        keywords = analysis.get('keywords_found', [])
        if keywords:
            for kw in keywords:
                f.write(f"    [{kw.get('importance', '-').upper()}] {kw.get('keyword', '-')} ")
                f.write(f"(encontrado como: '{kw.get('found_as', '-')}', tipo: {kw.get('match_type', '-')})\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("CONTATO EXTRAÍDO\n")
        f.write("-" * 80 + "\n")
        contact = analysis.get('contact_info', {})
        for key, value in contact.items():
            f.write(f"    {key}: {value if value else 'NÃO ENCONTRADO'}\n")
        f.write("\n")
        
        f.write("-" * 80 + "\n")
        f.write("FEEDBACK\n")
        f.write("-" * 80 + "\n")
        f.write("ALERTAS:\n")
        for w in analysis.get('warnings', []):
            f.write(f"    ⚠️ {w}\n")
        f.write("\nSUGESTÕES:\n")
        for s in analysis.get('suggestions', []):
            f.write(f"    💡 {s}\n")
        f.write("\nPONTOS POSITIVOS:\n")
        for p in analysis.get('positives', []):
            f.write(f"    ✅ {p}\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("FIM DO LOG\n")
        f.write("=" * 80 + "\n")
    
    app.logger.info(f"Log salvo em: {log_path}")
    return log_path


# =============================================================================
# ROTAS
# =============================================================================

@app.route('/')
def index():
    """Página principal com formulário de upload."""
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint para análise de currículo.
    
    Recebe PDF via upload e retorna análise ATS completa.
    """
    # Verificar se arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({
            "success": False,
            "error": "Nenhum arquivo enviado"
        }), 400
    
    file = request.files['file']
    
    # Verificar se arquivo foi selecionado
    if file.filename == '':
        return jsonify({
            "success": False,
            "error": "Nenhum arquivo selecionado"
        }), 400
    
    # Verificar extensão
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            "success": False,
            "error": "Apenas arquivos PDF são aceitos"
        }), 400
    
    try:
        # Ler bytes do arquivo
        pdf_bytes = file.read()
        
        # Extrair texto do PDF
        extraction_result = pdf_extractor.extract_from_bytes(pdf_bytes)
        
        # Verificar se extraiu algo
        if not extraction_result.text.strip():
            return jsonify({
                "success": False,
                "error": "Não foi possível extrair texto do PDF. "
                         "O arquivo pode estar vazio ou ser uma imagem."
            }), 400
        
        # Executar análise ATS
        ats_result = ats_engine.analyze(extraction_result.text)
        
        # Preparar resposta
        response = {
            "success": True,
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
        
        # Salvar log de debug em arquivo TXT
        save_analysis_log(file.filename, extraction_result.text, response)
        
        return jsonify(response)
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
    except Exception as e:
        app.logger.error(f"Erro ao processar PDF: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erro interno ao processar o arquivo. Tente novamente."
        }), 500


@app.route('/health')
def health():
    """Endpoint de health check."""
    return jsonify({
        "status": "healthy",
        "service": "leitura-ats-curriculo"
    })


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(413)
def too_large(e):
    """Handler para arquivo muito grande."""
    return jsonify({
        "success": False,
        "error": "Arquivo muito grande. O tamanho máximo é 16MB."
    }), 413


@app.errorhandler(500)
def server_error(e):
    """Handler para erro interno."""
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor. Tente novamente mais tarde."
    }), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    # Rodar em modo desenvolvimento
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
