#!/bin/bash
# =============================================================================
# setup.sh - Configuração inicial do ambiente
# =============================================================================
# Uso: ./scripts/setup.sh

set -e

echo "🔧 Configurando ambiente Leitura ATS..."
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar Python
echo "📦 Verificando pré-requisitos..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.10+ primeiro."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"

# Criar ambiente virtual
echo ""
echo "🐍 Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "  ${GREEN}✓${NC} Ambiente virtual criado"
else
    echo -e "  ${YELLOW}⚠${NC} Ambiente virtual já existe"
fi

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
echo ""
echo "📥 Instalando dependências..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "  ${GREEN}✓${NC} Dependências instaladas"

# Baixar dados NLTK
echo ""
echo "📚 Baixando dados NLTK..."
python3 -c "
import nltk
import sys
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('rslp', quiet=True)
    print('  ✓ Dados NLTK baixados')
except Exception as e:
    print(f'  ✗ Erro: {e}')
    sys.exit(1)
"

# Criar diretórios necessários
echo ""
echo "📁 Criando diretórios..."
mkdir -p logs
echo -e "  ${GREEN}✓${NC} Pasta de logs criada"

# Verificar instalação
echo ""
echo "🧪 Verificando instalação..."
cd aplicacao
python3 -c "from app import app; print('  ✓ Aplicação carrega corretamente')"
cd ..

# Criar .env se não existir
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "  ${GREEN}✓${NC} Arquivo .env criado (copie de .env.example)"
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Setup concluído com sucesso!${NC}"
echo "================================================"
echo ""
echo "Próximos passos:"
echo "  1. Ativar ambiente: source venv/bin/activate"
echo "  2. Iniciar app:     ./scripts/start.sh"
echo "  3. Acessar:         http://localhost:5000"
echo ""
