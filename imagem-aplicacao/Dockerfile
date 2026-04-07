# =============================================================================
# Dockerfile - Leitura ATS Currículo
# =============================================================================
# Build: docker build -t leitura-ats:v1.0.0 -f imagem-aplicacao/Dockerfile .

FROM python:3.12-slim

# Labels para metadata
LABEL maintainer="ricardo-silva-jr" \
      version="1.0.0" \
      description="Leitura ATS - Analisador de Currículos"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    FLASK_ENV=production \
    NLTK_DATA=/app/nltk_data \
    GUNICORN_WORKERS=2

WORKDIR $APP_HOME

# Criar usuário não-root (requisito de segurança)
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixar dados NLTK para diretório acessível
RUN mkdir -p /app/nltk_data && python -c "import nltk; \
    nltk.download('punkt', download_dir='/app/nltk_data', quiet=True); \
    nltk.download('punkt_tab', download_dir='/app/nltk_data', quiet=True); \
    nltk.download('rslp', download_dir='/app/nltk_data', quiet=True)"

# Copiar código da aplicação
COPY aplicacao/ $APP_HOME/

# Criar diretórios para logs e ajustar permissões
RUN mkdir -p $APP_HOME/logs \
    && chown -R appuser:appgroup $APP_HOME \
    && chown -R appuser:appgroup /app/nltk_data

# Trocar para usuário não-privilegiado
USER appuser

# Porta da aplicação
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
