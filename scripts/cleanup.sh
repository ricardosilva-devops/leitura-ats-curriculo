#!/bin/bash
# =============================================================================
# cleanup.sh - Limpar arquivos temporários e logs
# =============================================================================
# Uso: ./scripts/cleanup.sh [--all]

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ALL=${1:-""}

echo "🧹 Limpeza do projeto..."
echo ""

# Logs antigos (mais de 7 dias)
echo "📋 Removendo logs antigos..."
LOGS_REMOVED=$(find aplicacao/logs -name "*.txt" -mtime +7 -delete -print 2>/dev/null | wc -l || echo "0")
echo -e "  ${GREEN}✓${NC} $LOGS_REMOVED arquivos de log removidos"

# Cache Python
echo "🐍 Limpando cache Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} Cache Python limpo"

# Docker (se --all)
if [ "$ALL" = "--all" ]; then
    echo "🐳 Limpando Docker..."
    docker system prune -f 2>/dev/null || echo "  (Docker não disponível)"
fi

# Relatório
echo ""
echo "📊 Uso de disco:"
echo "  aplicacao/logs: $(du -sh aplicacao/logs 2>/dev/null | cut -f1 || echo '0K')"
echo "  venv:           $(du -sh venv 2>/dev/null | cut -f1 || echo '0K')"

echo ""
echo -e "${GREEN}✅ Limpeza concluída!${NC}"
