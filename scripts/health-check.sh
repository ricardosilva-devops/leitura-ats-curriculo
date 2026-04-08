#!/bin/bash
# =============================================================================
# health-check.sh - Verificar saude da aplicacao
# =============================================================================
# Uso: ./scripts/health-check.sh [url]
# =============================================================================

# -----------------------------------------------------------------------------
# Configuracoes
# -----------------------------------------------------------------------------
URL=${1:-http://localhost:5000}

# -----------------------------------------------------------------------------
# Funcoes
# -----------------------------------------------------------------------------
log_ok() {
    echo "[OK]   $1"
}

log_fail() {
    echo "[FAIL] $1"
}

log_info() {
    echo "[INFO] $1"
}

# -----------------------------------------------------------------------------
# Execucao
# -----------------------------------------------------------------------------
echo "============================================================================="
echo "HEALTH CHECK - Leitura ATS"
echo "============================================================================="
echo ""
log_info "URL: $URL"
echo ""

ERRORS=0

# Health endpoint
echo -n "Verificando /health ... "
RESPONSE=$(curl -s -w "\n%{http_code}" $URL/health 2>/dev/null)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "200" ]; then
    log_ok "/health retornou 200 ($BODY)"
else
    log_fail "/health retornou HTTP $HTTP_CODE"
    ERRORS=$((ERRORS + 1))
fi

# Pagina principal
echo -n "Verificando /       ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $URL/ 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    log_ok "/ retornou 200"
else
    log_fail "/ retornou HTTP $HTTP_CODE"
    ERRORS=$((ERRORS + 1))
fi

# Endpoint de analise
echo -n "Verificando /analyze ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $URL/analyze 2>/dev/null)
if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "415" ]; then
    log_ok "/analyze endpoint ativo (aguardando arquivo)"
else
    log_info "/analyze retornou HTTP $HTTP_CODE"
fi

echo ""
echo "============================================================================="
if [ $ERRORS -eq 0 ]; then
    echo "RESULTADO: Aplicacao saudavel"
    exit 0
else
    echo "RESULTADO: $ERRORS erro(s) encontrado(s)"
    exit 1
fi
