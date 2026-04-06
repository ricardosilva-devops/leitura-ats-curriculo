#!/bin/bash
# =============================================================================
# run-docker.sh - Executar container Docker
# =============================================================================
# Uso: ./scripts/run-docker.sh [tag] [port]

set -e

TAG=${1:-latest}
PORT=${2:-5000}
IMAGE_NAME="leitura-ats"
CONTAINER_NAME="leitura-ats"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🐳 Iniciando container..."
echo "   Image: $IMAGE_NAME:$TAG"
echo "   Port: $PORT"
echo ""

# Remover container anterior se existir
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "  Removendo container anterior..."
    docker rm -f $CONTAINER_NAME > /dev/null
fi

# Executar
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:5000 \
    $IMAGE_NAME:$TAG

echo ""
echo -e "${GREEN}✅ Container iniciado!${NC}"
echo ""

# Aguardar startup
echo "⏳ Aguardando aplicação iniciar..."
sleep 3

# Health check
if curl -s http://localhost:$PORT/health > /dev/null; then
    echo -e "${GREEN}✓ Aplicação rodando em http://localhost:$PORT${NC}"
else
    echo -e "${YELLOW}⚠ Verificar logs: docker logs $CONTAINER_NAME${NC}"
fi

echo ""
echo "Comandos úteis:"
echo "  docker logs -f $CONTAINER_NAME  # Ver logs"
echo "  docker stop $CONTAINER_NAME     # Parar"
echo "  docker rm $CONTAINER_NAME       # Remover"
