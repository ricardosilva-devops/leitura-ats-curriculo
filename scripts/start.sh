#!/bin/bash
# =============================================================================
# start.sh - Iniciar a aplicação
# =============================================================================
# Uso: ./scripts/start.sh [dev|prod]

set -e

MODE=${1:-dev}
PORT=${FLASK_PORT:-5000}

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Ativar venv se não estiver ativo
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

cd aplicacao

case $MODE in
    dev)
        echo -e "${GREEN}🚀 Iniciando em modo DESENVOLVIMENTO...${NC}"
        echo "   URL: http://localhost:$PORT"
        echo "   Debug: Ativado (auto-reload)"
        echo ""
        python3 app.py
        ;;
    prod)
        echo -e "${GREEN}🚀 Iniciando em modo PRODUÇÃO (Gunicorn)...${NC}"
        echo "   URL: http://localhost:$PORT"
        echo ""
        gunicorn --config gunicorn_config.py wsgi:app
        ;;
    bg|background)
        echo -e "${GREEN}🚀 Iniciando em BACKGROUND...${NC}"
        nohup gunicorn --config gunicorn_config.py wsgi:app > ../logs/gunicorn.log 2>&1 &
        PID=$!
        echo $PID > ../app.pid
        echo "   PID: $PID"
        echo "   Log: logs/gunicorn.log"
        sleep 2
        if curl -s http://localhost:$PORT/health > /dev/null; then
            echo -e "   ${GREEN}✓${NC} Aplicação iniciada com sucesso!"
        else
            echo -e "   ${YELLOW}⚠${NC} Verificar logs: tail -f logs/gunicorn.log"
        fi
        ;;
    *)
        echo "Uso: ./scripts/start.sh [dev|prod|bg]"
        echo ""
        echo "Modos:"
        echo "  dev  - Flask development server (padrão)"
        echo "  prod - Gunicorn production server"
        echo "  bg   - Gunicorn em background"
        exit 1
        ;;
esac
