#!/bin/bash
# =============================================================================
# build-docker.sh - Build da imagem Docker
# =============================================================================
# Uso: ./scripts/build-docker.sh [tag]

set -e

TAG=${1:-latest}
IMAGE_NAME="leitura-ats"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🐳 Building Docker image..."
echo "   Image: $IMAGE_NAME:$TAG"
echo ""

# Build
docker build \
    -t $IMAGE_NAME:$TAG \
    -f imagem-aplicacao/Dockerfile \
    .

echo ""
echo -e "${GREEN}✅ Build concluído!${NC}"
echo ""
echo "Para executar:"
echo "  docker run -p 5000:5000 $IMAGE_NAME:$TAG"
echo ""
echo "Para testar:"
echo "  curl http://localhost:5000/health"
