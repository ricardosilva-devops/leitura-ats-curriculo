#!/bin/bash
# =============================================================================
# run-docker.sh - Executar container Docker
# =============================================================================
# Uso: ./scripts/run-docker.sh [tag] [port]
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAG=${1:-latest}
PORT=${2:-5000}
IMAGE_NAME="leitura-ats"
CONTAINER_NAME="leitura-ats"

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
echo "DOCKER RUN"
echo "============================================================================="
echo ""
log_info "Image: $IMAGE_NAME:$TAG"
log_info "Port: $PORT"
echo ""

# Remover container anterior se existir
if docker ps -a | grep -q $CONTAINER_NAME; then
    log_info "Removendo container anterior..."
    docker rm -f $CONTAINER_NAME > /dev/null
fi

# Executar
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:5000 \
    $IMAGE_NAME:$TAG

log_ok "Container iniciado"

# Aguardar startup
log_info "Aguardando aplicacao iniciar..."
sleep 3

# Health check
if curl -s http://localhost:$PORT/health > /dev/null; then
    log_ok "Aplicacao rodando em http://localhost:$PORT"
else
    log_warn "Verificar logs: docker logs $CONTAINER_NAME"
fi

echo ""
echo "Comandos uteis:"
echo "  docker logs -f $CONTAINER_NAME  # Ver logs"
echo "  docker stop $CONTAINER_NAME     # Parar"
echo "  docker rm $CONTAINER_NAME       # Remover"
echo ""
