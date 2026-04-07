"""
Utilitários para respostas HTTP padronizadas.

Centraliza formato de respostas JSON para consistência.
"""

from flask import jsonify
from typing import Any, Optional, Dict


def success_response(data: Dict[str, Any], status_code: int = 200):
    """
    Resposta de sucesso padronizada.
    
    Args:
        data: Dados a incluir na resposta
        status_code: Código HTTP (default: 200)
    
    Returns:
        Tuple (response, status_code)
    """
    response = {
        "success": True,
        **data
    }
    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None
):
    """
    Resposta de erro padronizada.
    
    Args:
        message: Mensagem de erro amigável para o usuário
        status_code: Código HTTP (default: 400)
        error_code: Código interno opcional para debugging
    
    Returns:
        Tuple (response, status_code)
    """
    response = {
        "success": False,
        "error": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    return jsonify(response), status_code


# Mensagens de erro padronizadas
ERROR_MESSAGES = {
    "no_file": "Nenhum arquivo enviado",
    "no_file_selected": "Nenhum arquivo selecionado",
    "invalid_extension": "Apenas arquivos PDF são aceitos",
    "invalid_mime": "Tipo de arquivo inválido. Envie um PDF válido",
    "invalid_pdf": "Arquivo não é um PDF válido",
    "file_too_large": "Arquivo muito grande. O tamanho máximo é 16MB",
    "empty_pdf": "Não foi possível extrair texto do PDF. O arquivo pode estar vazio ou ser uma imagem escaneada",
    "processing_error": "Erro ao processar o arquivo. Tente novamente",
    "internal_error": "Erro interno do servidor. Tente novamente mais tarde"
}
