#!/bin/bash
# =============================================================================
# health-check.sh - Verificar saúde da aplicação
# =============================================================================
# Uso: ./scripts/health-check.sh [url]

URL=${1:-http://localhost:5000}

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🏥 Health Check - Leitura ATS"
echo "   URL: $URL"
echo ""

# Health endpoint
echo -n "  /health: "
RESPONSE=$(curl -s -w "\n%{http_code}" $URL/health 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC} ($BODY)"
else
    echo -e "${RED}✗ FALHOU${NC} (HTTP $HTTP_CODE)"
    exit 1
fi

# Página principal
echo -n "  /       : "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $URL/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FALHOU${NC} (HTTP $HTTP_CODE)"
    exit 1
fi

# Verificar se aceita uploads
echo -n "  /analyze: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $URL/analyze 2>/dev/null)
if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "415" ]; then
    echo -e "${GREEN}✓ OK${NC} (endpoint ativo, aguardando arquivo)"
else
    echo -e "${YELLOW}? HTTP $HTTP_CODE${NC}"
fi

echo ""
echo -e "${GREEN}✅ Aplicação saudável!${NC}"
