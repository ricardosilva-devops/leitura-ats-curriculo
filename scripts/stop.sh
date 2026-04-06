#!/bin/bash
# =============================================================================
# stop.sh - Parar a aplicação
# =============================================================================
# Uso: ./scripts/stop.sh

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🛑 Parando aplicação..."

# Verificar se existe arquivo PID
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        rm app.pid
        echo -e "  ${GREEN}✓${NC} Processo $PID finalizado"
    else
        rm app.pid
        echo -e "  ${YELLOW}⚠${NC} Processo $PID não encontrado (já parado?)"
    fi
else
    # Tentar encontrar processo gunicorn
    PIDS=$(pgrep -f "gunicorn.*wsgi:app" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "  Encontrados processos: $PIDS"
        kill $PIDS 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} Processos finalizados"
    else
        echo -e "  ${YELLOW}⚠${NC} Nenhum processo encontrado"
    fi
fi

# Verificar porta 5000
if lsof -i :5000 &>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} Porta 5000 ainda em uso. Verificar:"
    lsof -i :5000 | head -3
else
    echo -e "  ${GREEN}✓${NC} Porta 5000 liberada"
fi
