# =============================================================================
# Dockerfile - Leitura ATS Currículo
# =============================================================================
# Imagem multi-stage otimizada para Kubernetes
# Build: docker build -t leitura-ats:v1.0.0 -f imagem-aplicacao/Dockerfile .

# -----------------------------------------------------------------------------
# Stage 1: Builder - Compilar dependências
# -----------------------------------------------------------------------------
FROM python:3.12-slim as builder

WORKDIR /build

# Instalar dependências de compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e criar wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Imagem final
# -----------------------------------------------------------------------------
FROM python:3.12-slim

# Labels para metadata
LABEL maintainer="ricardo-silva-jr" \
      version="1.0.0" \
      description="Leitura ATS - Analisador de Currículos"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    FLASK_ENV=production

WORKDIR $APP_HOME

# Criar usuário não-root (requisito de segurança)
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Instalar dependências de runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar wheels compilados
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

# Baixar dados NLTK
RUN python -c "import nltk; \
    nltk.download('punkt', quiet=True); \
    nltk.download('punkt_tab', quiet=True); \
    nltk.download('rslp', quiet=True)"

# Copiar código da aplicação
COPY aplicacao/ $APP_HOME/

# Criar diretórios para logs
RUN mkdir -p $APP_HOME/logs \
    && chown -R appuser:appgroup $APP_HOME

# Trocar para usuário não-privilegiado
USER appuser

# Porta da aplicação
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
