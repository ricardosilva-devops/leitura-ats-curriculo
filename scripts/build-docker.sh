#!/bin/bash
# =============================================================================
# build-docker.sh - Build da imagem Docker
# =============================================================================
# Uso: ./scripts/build-docker.sh [tag]
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TAG=${1:-latest}
IMAGE_NAME="leitura-ats"

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
echo "DOCKER BUILD"
echo "============================================================================="
echo ""
log_info "Image: $IMAGE_NAME:$TAG"
log_info "Dockerfile: imagem-aplicacao/Dockerfile"
echo ""

docker build \
    -t $IMAGE_NAME:$TAG \
    -f imagem-aplicacao/Dockerfile \
    .

echo ""
log_ok "Build concluido: $IMAGE_NAME:$TAG"
echo ""
echo "Proximos passos:"
echo "  Executar:  docker run -p 5000:5000 $IMAGE_NAME:$TAG"
echo "  Testar:    curl http://localhost:5000/health"
echo ""
