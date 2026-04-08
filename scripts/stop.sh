#!/bin/bash
# =============================================================================
# stop.sh - Parar a aplicacao
# =============================================================================
# Uso: ./scripts/stop.sh
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PORT=${FLASK_PORT:-5000}

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

# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------
echo "============================================================================="
echo "PARANDO APLICACAO"
echo "============================================================================="
echo ""

# Verificar se existe arquivo PID
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        rm app.pid
        log_ok "Processo $PID finalizado"
    else
        rm app.pid
        log_warn "Processo $PID nao encontrado (ja parado?)"
    fi
else
    # Tentar encontrar processo gunicorn
    PIDS=$(pgrep -f "gunicorn.*wsgi:application" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        log_info "Processos encontrados: $PIDS"
        kill $PIDS 2>/dev/null || true
        log_ok "Processos finalizados"
    else
        log_warn "Nenhum processo encontrado"
    fi
fi

# Verificar porta
if lsof -i :$PORT &>/dev/null; then
    log_warn "Porta $PORT ainda em uso:"
    lsof -i :$PORT | head -3
else
    log_ok "Porta $PORT liberada"
fi

echo ""
