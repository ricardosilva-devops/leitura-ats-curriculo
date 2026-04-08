#!/bin/bash
# =============================================================================
# cleanup.sh - Limpar arquivos temporarios e logs
# =============================================================================
# Uso: ./scripts/cleanup.sh [--all]
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ALL=${1:-""}

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

# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------
echo "============================================================================="
echo "LIMPEZA DO PROJETO"
echo "============================================================================="
echo ""

# Logs antigos (mais de 7 dias)
log_info "Removendo logs antigos (>7 dias)..."
LOGS_REMOVED=$(find logs -name "*.txt" -mtime +7 -delete -print 2>/dev/null | wc -l || echo "0")
log_ok "$LOGS_REMOVED arquivos de log removidos"

# Cache Python
log_info "Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
log_ok "Cache Python limpo"

# Docker (se --all)
if [ "$ALL" = "--all" ]; then
    log_info "Limpando Docker..."
    docker system prune -f 2>/dev/null || echo "[INFO] Docker nao disponivel"
fi

# Relatorio
echo ""
echo "-----------------------------------------------------------------------------"
echo "USO DE DISCO"
echo "-----------------------------------------------------------------------------"
echo "  logs: $(du -sh logs 2>/dev/null | cut -f1 || echo '0K')"
echo "  venv: $(du -sh venv 2>/dev/null | cut -f1 || echo '0K')"

echo ""
echo "============================================================================="
echo "LIMPEZA CONCLUIDA"
echo "============================================================================="
