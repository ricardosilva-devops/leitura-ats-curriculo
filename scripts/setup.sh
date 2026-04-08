#!/bin/bash
# =============================================================================
# setup.sh - Configuracao inicial do ambiente
# =============================================================================
# Uso: ./scripts/setup.sh
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_MIN_VERSION="3.10"

cd "$PROJECT_DIR"

# -----------------------------------------------------------------------------
# Funcoes
# -----------------------------------------------------------------------------
log_info() {
    echo "[INFO] $1"
}

log_ok() {
    echo "[OK]   $1"
}

log_warn() {
    echo "[WARN] $1"
}

log_error() {
    echo "[ERROR] $1"
    exit 1
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 nao encontrado. Instale Python $PYTHON_MIN_VERSION ou superior."
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_ok "Python $PYTHON_VERSION encontrado"
}

# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------
echo "============================================================================="
echo "SETUP - Leitura ATS Curriculos"
echo "============================================================================="
echo ""

log_info "Verificando pre-requisitos..."
check_python

log_info "Configurando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_ok "Ambiente virtual criado"
else
    log_ok "Ambiente virtual ja existe"
fi

source venv/bin/activate

log_info "Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
log_ok "Dependencias instaladas"

log_info "Baixando dados NLTK..."
python3 -c "
import nltk
import sys
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('rslp', quiet=True)
except Exception as e:
    print('[ERROR] Falha ao baixar NLTK: ' + str(e))
    sys.exit(1)
"
log_ok "Dados NLTK baixados"

log_info "Criando diretorios..."
mkdir -p logs
log_ok "Diretorio de logs criado"

log_info "Verificando instalacao..."
cd aplicacao
python3 -c "from app import create_app; app = create_app()"
cd ..
log_ok "Aplicacao carrega corretamente"

echo ""
echo "============================================================================="
echo "SETUP CONCLUIDO"
echo "============================================================================="
echo ""
echo "Proximos passos:"
echo "  1. Ativar ambiente: source venv/bin/activate"
echo "  2. Iniciar app:     ./scripts/start.sh"
echo "  3. Acessar:         http://localhost:5000"
echo ""
