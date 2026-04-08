#!/bin/bash
# =============================================================================
# start.sh - Iniciar a aplicacao
# =============================================================================
# Uso: ./scripts/start.sh [dev|prod|bg]
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODE=${1:-dev}
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

activate_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        else
            echo "[ERROR] Ambiente virtual nao encontrado. Execute ./scripts/setup.sh primeiro."
            exit 1
        fi
    fi
}

# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------
activate_venv
cd aplicacao

case $MODE in
    dev)
        echo "============================================================================="
        echo "INICIANDO - Modo Desenvolvimento"
        echo "============================================================================="
        echo ""
        log_info "URL: http://localhost:$PORT"
        log_info "Debug: Ativado (auto-reload)"
        echo ""
        python3 app.py
        ;;
    prod)
        echo "============================================================================="
        echo "INICIANDO - Modo Producao (Gunicorn)"
        echo "============================================================================="
        echo ""
        log_info "URL: http://localhost:$PORT"
        echo ""
        gunicorn --config gunicorn_config.py wsgi:application
        ;;
    bg|background)
        echo "============================================================================="
        echo "INICIANDO - Modo Background"
        echo "============================================================================="
        echo ""
        nohup gunicorn --config gunicorn_config.py wsgi:application > ../logs/gunicorn.log 2>&1 &
        PID=$!
        echo $PID > ../app.pid
        log_info "PID: $PID"
        log_info "Log: logs/gunicorn.log"
        sleep 2
        if curl -s http://localhost:$PORT/health > /dev/null; then
            log_ok "Aplicacao iniciada com sucesso"
        else
            log_warn "Verificar logs: tail -f logs/gunicorn.log"
        fi
        ;;
    *)
        echo "Uso: ./scripts/start.sh [dev|prod|bg]"
        echo ""
        echo "Modos:"
        echo "  dev  - Flask development server (padrao)"
        echo "  prod - Gunicorn production server"
        echo "  bg   - Gunicorn em background"
        exit 1
        ;;
esac
