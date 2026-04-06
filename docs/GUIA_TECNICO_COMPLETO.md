# 📚 GUIA TÉCNICO COMPLETO - Leitura ATS

## Documentação Detalhada de Todas as Tecnologias e Configurações

Este documento explica em detalhes cada componente, configuração e parâmetro do projeto, com exemplos práticos para facilitar o entendimento.

---

# ÍNDICE

1. [Visão Geral do Projeto](#1-visão-geral-do-projeto)
2. [Python/Flask - A Aplicação](#2-pythonflask---a-aplicação)
3. [Docker - Containerização](#3-docker---containerização)
4. [Nginx - Servidor Web/Proxy](#4-nginx---servidor-webproxy)
5. [Gunicorn - Servidor WSGI](#5-gunicorn---servidor-wsgi)
6. [Supervisor - Gerenciador de Processos](#6-supervisor---gerenciador-de-processos)
7. [Terraform - Infraestrutura AWS](#7-terraform---infraestrutura-aws)
8. [Kubernetes - Orquestração](#8-kubernetes---orquestração)
9. [Fluxo Completo de uma Requisição](#9-fluxo-completo-de-uma-requisição)
10. [Glossário de Termos](#10-glossário-de-termos)

---

# 1. VISÃO GERAL DO PROJETO

## O que é este projeto?

Uma aplicação web que analisa currículos em PDF, simulando como sistemas ATS (Applicant Tracking System) leem documentos. O objetivo é ajudar candidatos a otimizar seus currículos.

## Arquitetura Completa

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              INTERNET                                    │
│                                  │                                       │
│                                  ▼                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      AWS CLOUD                                     │  │
│  │                                                                    │  │
│  │   ┌─────────────────────────────────────────────────────────────┐ │  │
│  │   │                 LOAD BALANCER (ALB)                         │ │  │
│  │   │         Distribui tráfego entre os pods                     │ │  │
│  │   └─────────────────────────┬───────────────────────────────────┘ │  │
│  │                             │                                      │  │
│  │   ┌─────────────────────────▼───────────────────────────────────┐ │  │
│  │   │                  KUBERNETES (EKS)                            │ │  │
│  │   │                                                              │ │  │
│  │   │   ┌──────────────────┐    ┌──────────────────┐              │ │  │
│  │   │   │      POD 1       │    │      POD 2       │              │ │  │
│  │   │   │                  │    │                  │              │ │  │
│  │   │   │  ┌────────────┐  │    │  ┌────────────┐  │              │ │  │
│  │   │   │  │ SUPERVISOR │  │    │  │ SUPERVISOR │  │              │ │  │
│  │   │   │  │     │      │  │    │  │     │      │  │              │ │  │
│  │   │   │  │  ┌──┴──┐   │  │    │  │  ┌──┴──┐   │  │              │ │  │
│  │   │   │  │  │     │   │  │    │  │  │     │   │  │              │ │  │
│  │   │   │  │ NGINX GUNI │  │    │  │ NGINX GUNI │  │              │ │  │
│  │   │   │  │  :80  CORN │  │    │  │  :80  CORN │  │              │ │  │
│  │   │   │  │      :8000 │  │    │  │      :8000 │  │              │ │  │
│  │   │   │  │     │      │  │    │  │     │      │  │              │ │  │
│  │   │   │  │  ┌──┴──┐   │  │    │  │  ┌──┴──┐   │  │              │ │  │
│  │   │   │  │  │FLASK│   │  │    │  │  │FLASK│   │  │              │ │  │
│  │   │   │  │  │ APP │   │  │    │  │  │ APP │   │  │              │ │  │
│  │   │   │  └──┴─────┴───┘  │    │  └──┴─────┴───┘  │              │ │  │
│  │   │   └──────────────────┘    └──────────────────┘              │ │  │
│  │   │                                                              │ │  │
│  │   └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                    │  │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │
│  │   │   ECR    │  │    S3    │  │CloudWatch│  │   VPC    │         │  │
│  │   │(imagens) │  │(arquivos)│  │  (logs)  │  │  (rede)  │         │  │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘         │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│                     TUDO PROVISIONADO VIA TERRAFORM                      │
└──────────────────────────────────────────────────────────────────────────┘
```

## Fluxo Simplificado

```
Usuário → Load Balancer → Nginx → Gunicorn → Flask → Resposta
            (AWS)         (proxy)  (WSGI)    (Python)
```

---

# 2. PYTHON/FLASK - A APLICAÇÃO

## 2.1 O que é Flask?

Flask é um **microframework** Python para criar aplicações web. "Micro" significa que é simples e não impõe muitas regras, diferente do Django que é mais completo.

### Exemplo Básico de Flask:

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Olá, Mundo!'

if __name__ == '__main__':
    app.run()
```

## 2.2 Estrutura da Nossa Aplicação

```
aplicacao/
├── app.py                 # Arquivo principal Flask
├── wsgi.py                # Entry point para Gunicorn
├── gunicorn_config.py     # Configurações do Gunicorn
│
├── leitura_ats/           # Motor de análise ATS
│   ├── __init__.py
│   ├── engine.py          # Lógica principal
│   └── stopwords.py       # Palavras ignoradas
│
├── extracao_pdf/          # Extração de texto do PDF
│   ├── __init__.py
│   └── extractor.py
│
├── analise_keywords/      # Palavras-chave técnicas
│   ├── __init__.py
│   ├── keywords.py        # Lista de keywords
│   └── synonyms.py        # Sinônimos (k8s = kubernetes)
│
├── templates/             # HTML
│   └── index.html
│
└── static/                # CSS e JavaScript
    ├── css/style.css
    └── js/main.js
```

## 2.3 Arquivo Principal: app.py

```python
# =============================================================================
# IMPORTS
# =============================================================================

from flask import Flask, request, jsonify, render_template
import os

# Flask(__name__) cria a aplicação
# __name__ é uma variável Python que contém o nome do módulo atual
app = Flask(__name__)

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

# SECRET_KEY: usado para criptografia de sessões e cookies
# Em produção, NUNCA deixe um valor fixo - use variável de ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-desenvolvimento')

# MAX_CONTENT_LENGTH: tamanho máximo de upload
# 16 * 1024 * 1024 = 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# =============================================================================
# ROTAS (ENDPOINTS)
# =============================================================================

# @app.route define uma URL que a aplicação responde
# methods=['GET'] significa que responde apenas a requisições GET

@app.route('/')
def index():
    """
    Página inicial - retorna o HTML
    render_template() busca o arquivo em templates/
    """
    return render_template('index.html')


@app.route('/health')
def health():
    """
    Health check - usado pelo Kubernetes para verificar se a aplicação está viva
    Kubernetes chama esta URL periodicamente
    Se retornar 200, a aplicação está saudável
    Se retornar erro, Kubernetes reinicia o container
    """
    return jsonify({'status': 'healthy'})


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint principal - recebe o PDF e retorna a análise
    methods=['POST'] significa que só aceita POST (envio de dados)
    """
    # request.files contém arquivos enviados via formulário
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    
    # Verificar se é PDF
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Apenas arquivos PDF são aceitos'}), 400
    
    # Processar o arquivo...
    # (código de análise ATS)
    
    return jsonify({
        'success': True,
        'analysis': {
            'score': 75,
            'keywords_found': ['python', 'aws', 'docker']
        }
    })


# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

if __name__ == '__main__':
    # Só executa se rodar diretamente: python app.py
    # Em produção, Gunicorn importa o app e não executa este bloco
    
    # debug=True: recarrega automaticamente quando código muda
    # host='0.0.0.0': aceita conexões de qualquer IP (necessário no Docker)
    # port=5000: porta da aplicação
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### Explicação dos Parâmetros:

| Parâmetro | Valor | Explicação |
|-----------|-------|------------|
| `debug=True` | Boolean | Modo desenvolvimento: recarrega código automaticamente, mostra erros detalhados |
| `host='0.0.0.0'` | String | Aceita conexões de qualquer IP. `127.0.0.1` só aceita do próprio computador |
| `port=5000` | Integer | Porta TCP onde a aplicação escuta |

## 2.4 Arquivo WSGI: wsgi.py

```python
# =============================================================================
# WSGI Entry Point
# =============================================================================
# WSGI = Web Server Gateway Interface
# É o padrão que permite servidores web (Gunicorn) se comunicarem com apps Python

from app import app

# Gunicorn importa este arquivo e usa o objeto 'app'
# Comando: gunicorn wsgi:app
#          wsgi = nome do arquivo (wsgi.py)
#          app = nome do objeto Flask

if __name__ == "__main__":
    app.run()
```

## 2.5 Motor ATS: engine.py (Simplificado)

```python
from dataclasses import dataclass
from typing import List, Dict
import nltk
from nltk.stem import RSLPStemmer  # Stemmer para Português

@dataclass
class ATSResult:
    """
    @dataclass: cria automaticamente __init__, __repr__, etc.
    É uma forma moderna de criar classes de dados em Python
    """
    final_score: int
    keyword_score: int
    structure_score: int
    keywords_found: List[str]


class ATSEngine:
    """
    Motor principal de análise ATS
    """
    
    def __init__(self):
        # RSLPStemmer: reduz palavras à raiz
        # "trabalhando" → "trabalh"
        # "trabalhei" → "trabalh"
        # Isso permite encontrar variações da mesma palavra
        self.stemmer = RSLPStemmer()
        
        # Palavras-chave técnicas que buscamos
        self.tech_keywords = {
            'python', 'java', 'javascript', 'aws', 'docker',
            'kubernetes', 'linux', 'sql', 'git', 'api'
        }
    
    def analyze(self, text: str) -> ATSResult:
        """
        Analisa o texto do currículo
        
        Args:
            text: Texto extraído do PDF
            
        Returns:
            ATSResult com scores e keywords encontradas
        """
        # Tokenização: divide texto em palavras
        # "Eu sei Python" → ["Eu", "sei", "Python"]
        tokens = nltk.word_tokenize(text.lower())
        
        # Encontrar keywords
        found = []
        for token in tokens:
            # Aplicar stemming
            stem = self.stemmer.stem(token)
            if token in self.tech_keywords or stem in self.tech_keywords:
                found.append(token)
        
        # Calcular scores
        keyword_score = min(100, len(found) * 10)
        structure_score = self._analyze_structure(text)
        
        final_score = int(
            keyword_score * 0.4 +      # 40% peso
            structure_score * 0.35 +   # 35% peso
            self._readability(text) * 0.25  # 25% peso
        )
        
        return ATSResult(
            final_score=final_score,
            keyword_score=keyword_score,
            structure_score=structure_score,
            keywords_found=list(set(found))  # Remove duplicatas
        )
    
    def _analyze_structure(self, text: str) -> int:
        """
        Verifica se o currículo tem seções importantes
        """
        sections = ['experiência', 'formação', 'habilidades', 'educação']
        found = sum(1 for s in sections if s in text.lower())
        return int((found / len(sections)) * 100)
    
    def _readability(self, text: str) -> int:
        """
        Analisa legibilidade do texto
        """
        # Exemplo simplificado
        sentences = text.split('.')
        avg_words = len(text.split()) / max(len(sentences), 1)
        
        # Textos muito longos ou muito curtos penalizam
        if 15 <= avg_words <= 25:
            return 100
        elif 10 <= avg_words <= 30:
            return 70
        else:
            return 50
```

### Conceitos Importantes:

| Conceito | Explicação | Exemplo |
|----------|------------|---------|
| **Tokenização** | Dividir texto em unidades (palavras) | "Eu amo Python" → ["Eu", "amo", "Python"] |
| **Stemming** | Reduzir palavra à raiz | "correndo", "corri", "correr" → "corr" |
| **Stopwords** | Palavras ignoradas (sem significado) | "o", "a", "de", "para", "em" |
| **TF-IDF** | Importância de uma palavra no documento | Palavras raras = mais importantes |

---

# 3. DOCKER - CONTAINERIZAÇÃO

## 3.1 O que é Docker?

Docker é uma plataforma que **empacota** sua aplicação com todas as dependências em um **container**. Um container é como uma "caixa" isolada que roda em qualquer lugar.

### Analogia:
- **Sem Docker**: "Funciona na minha máquina" 😅
- **Com Docker**: Funciona em QUALQUER máquina 🎉

### Diferença entre Container e Máquina Virtual:

```
MÁQUINA VIRTUAL                    CONTAINER
┌─────────────────┐               ┌─────────────────┐
│     App 1       │               │     App 1       │
├─────────────────┤               ├─────────────────┤
│  Bibliotecas    │               │  Bibliotecas    │
├─────────────────┤               └────────┬────────┘
│  Sistema Op.    │                        │
│  (Ubuntu)       │               ┌────────┴────────┐
├─────────────────┤               │     Docker      │
│  Hypervisor     │               ├─────────────────┤
├─────────────────┤               │  Sistema Op.    │
│  Hardware       │               │  (Host)         │
└─────────────────┘               └─────────────────┘

Pesado (~GB)                      Leve (~MB)
Inicia em minutos                 Inicia em segundos
```

## 3.2 Nosso Dockerfile Explicado

```dockerfile
# =============================================================================
# STAGE 1: BUILDER
# =============================================================================
# Multi-stage build: primeiro estágio compila, segundo executa
# Resultado: imagem final menor e mais segura

FROM python:3.12-slim as builder
# FROM: imagem base (Python 3.12 versão slim/leve)
# as builder: dá nome a este estágio para referência posterior

WORKDIR /build
# WORKDIR: define diretório de trabalho
# Todos os comandos seguintes executam neste diretório
# Se não existir, é criado automaticamente

# Instalar dependências de compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# RUN: executa comandos no container durante o build
# apt-get update: atualiza lista de pacotes
# apt-get install -y: instala sem perguntar (yes automático)
# --no-install-recommends: não instala pacotes opcionais (menor tamanho)
# gcc, build-essential: compiladores necessários para algumas libs Python
# rm -rf /var/lib/apt/lists/*: limpa cache (reduz tamanho da imagem)

# O && conecta comandos: só executa o próximo se o anterior der certo
# A \ permite quebrar linha no Dockerfile

COPY requirements.txt .
# COPY: copia arquivo do host para o container
# . significa "diretório atual" (/build)

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt
# pip wheel: cria "wheels" (pacotes pré-compilados)
# --no-cache-dir: não guarda cache (menor tamanho)
# --no-deps: não baixa dependências (já estão no requirements.txt)
# --wheel-dir: onde salvar os wheels
# -r requirements.txt: lê dependências deste arquivo


# =============================================================================
# STAGE 2: RUNTIME
# =============================================================================
# Este estágio cria a imagem final que será usada em produção

FROM python:3.12-slim
# Começa do zero com imagem limpa
# Não tem gcc, compiladores - só o necessário para executar

# Labels: metadados da imagem (aparecem no docker inspect)
LABEL maintainer="ricardo-silva-jr" \
      version="1.0.0" \
      description="Leitura ATS - Analisador de Currículos"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    FLASK_ENV=production
# ENV: define variáveis de ambiente disponíveis no container
# PYTHONDONTWRITEBYTECODE=1: não cria arquivos .pyc
# PYTHONUNBUFFERED=1: logs aparecem imediatamente (não ficam em buffer)
# APP_HOME=/app: variável customizada para usar depois

WORKDIR $APP_HOME
# Usa a variável definida acima

# Criar usuário não-root (SEGURANÇA!)
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser
# Por segurança, aplicações não devem rodar como root
# Se alguém hackear a aplicação, terá permissões limitadas
# groupadd: cria grupo
# useradd: cria usuário
# --gid/--uid 1000: IDs específicos (padrão para primeiro usuário)

# Instalar curl (para health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar wheels do estágio builder e instalar
COPY --from=builder /build/wheels /wheels
# COPY --from=builder: copia do estágio anterior (builder)
# Isso é a magia do multi-stage: compilamos no builder, usamos aqui

RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels
# --no-index: não busca no PyPI (usa só os wheels locais)
# --find-links: onde estão os pacotes

# Baixar dados NLTK
RUN python -c "import nltk; \
    nltk.download('punkt', quiet=True); \
    nltk.download('punkt_tab', quiet=True); \
    nltk.download('rslp', quiet=True)"
# NLTK precisa baixar dados (tokenizadores, etc)
# Fazemos no build para não baixar toda vez que o container inicia

# Copiar código da aplicação
COPY aplicacao/ $APP_HOME/

# Criar diretório de logs e ajustar permissões
RUN mkdir -p $APP_HOME/logs \
    && chown -R appuser:appgroup $APP_HOME
# chown: muda dono dos arquivos
# -R: recursivo (inclui subpastas)

# Mudar para usuário não-privilegiado
USER appuser
# A partir daqui, tudo roda como appuser, não root

# Documentar porta exposta
EXPOSE 5000
# EXPOSE: documenta qual porta o container usa
# Não abre a porta! Só documenta.
# Quem abre é o -p no docker run

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
# HEALTHCHECK: Docker verifica periodicamente se container está saudável
# --interval=30s: verifica a cada 30 segundos
# --timeout=5s: espera no máximo 5 segundos por resposta
# --start-period=10s: espera 10s antes de começar a verificar (tempo de inicialização)
# --retries=3: após 3 falhas consecutivas, marca como unhealthy
# curl -f: falha silenciosamente se HTTP erro
# || exit 1: se curl falhar, retorna código 1 (erro)

# Comando de inicialização
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
# CMD: comando executado quando container inicia
# Formato array ["cmd", "arg1", "arg2"] é preferido (mais seguro)
# gunicorn: servidor WSGI
# --config: arquivo de configuração
# wsgi:app: módulo:objeto (wsgi.py, objeto app)
```

## 3.3 Comandos Docker Importantes

```bash
# BUILD: criar imagem a partir do Dockerfile
docker build -t leitura-ats:v1.0.0 -f imagem-aplicacao/Dockerfile .
#        -t: tag (nome:versão)
#        -f: caminho do Dockerfile
#        . : contexto (diretório atual)

# RUN: executar container
docker run -p 5000:5000 leitura-ats:v1.0.0
#      -p 5000:5000: mapeia porta_host:porta_container
#      Acesse http://localhost:5000

# RUN em background (detached)
docker run -d -p 5000:5000 --name minha-app leitura-ats:v1.0.0
#      -d: detached (background)
#      --name: nome do container

# Ver containers rodando
docker ps

# Ver logs
docker logs minha-app
docker logs -f minha-app  # -f = follow (tempo real)

# Entrar no container
docker exec -it minha-app bash
#        -it: interativo com terminal

# Parar container
docker stop minha-app

# Remover container
docker rm minha-app

# Ver imagens
docker images

# Remover imagem
docker rmi leitura-ats:v1.0.0
```

## 3.4 .dockerignore

```
# Arquivos que NÃO devem ir para o container
# Similar ao .gitignore

# Ambiente virtual Python (recriamos no container)
venv/
__pycache__/
*.pyc

# Git
.git/
.gitignore

# Arquivos locais
*.log
.env
.env.local

# IDE
.vscode/
.idea/

# Documentos
*.md
*.txt
docs/
```

---

# 4. NGINX - SERVIDOR WEB/PROXY

## 4.1 O que é Nginx?

Nginx (pronuncia-se "engine-x") é um **servidor web** de alta performance. No nosso caso, usamos como **proxy reverso**.

### Proxy Reverso vs Servidor Direto:

```
SEM PROXY (não recomendado):
Cliente → Gunicorn/Flask
          (exposto diretamente)

COM PROXY (recomendado):
Cliente → Nginx → Gunicorn/Flask
          (protege e otimiza)
```

### Por que usar Nginx na frente?

1. **Performance**: Serve arquivos estáticos (CSS, JS) muito mais rápido
2. **Segurança**: Esconde detalhes da aplicação, filtra requisições
3. **SSL/TLS**: Gerencia HTTPS de forma otimizada
4. **Compressão**: Comprime respostas (gzip)
5. **Cache**: Pode cachear respostas
6. **Load Balancing**: Distribui carga entre múltiplos backends

## 4.2 Nosso nginx.conf Explicado

```nginx
# =============================================================================
# CONFIGURAÇÃO PRINCIPAL
# =============================================================================

worker_processes auto;
# Quantos processos worker criar
# auto = usa número de CPUs disponíveis
# 1 CPU = 1 worker, 4 CPUs = 4 workers

error_log /var/log/nginx/error.log warn;
# Onde salvar logs de erro
# warn = nível de log (debug, info, notice, warn, error, crit)

pid /tmp/nginx.pid;
# Arquivo que guarda o PID do processo principal
# /tmp/ porque nosso usuário não-root não pode escrever em /var/run/


# =============================================================================
# EVENTOS
# =============================================================================

events {
    worker_connections 1024;
    # Máximo de conexões simultâneas por worker
    # 4 workers × 1024 = 4096 conexões simultâneas
    
    use epoll;
    # Método de I/O assíncrono (Linux)
    # epoll é mais eficiente que select/poll
    
    multi_accept on;
    # Aceita múltiplas conexões de uma vez
}


# =============================================================================
# HTTP
# =============================================================================

http {
    include /etc/nginx/mime.types;
    # Inclui arquivo com tipos MIME
    # Define que .html = text/html, .css = text/css, etc.
    
    default_type application/octet-stream;
    # Tipo padrão se não reconhecer a extensão
    
    # Formato do log de acesso
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time';
    # $remote_addr: IP do cliente
    # $status: código HTTP (200, 404, 500)
    # $request_time: tempo total da requisição
    
    access_log /var/log/nginx/access.log main;
    
    
    # =========================================================================
    # PERFORMANCE
    # =========================================================================
    
    sendfile on;
    # Usa chamada de sistema sendfile() para servir arquivos
    # Mais eficiente que read()+write()
    
    tcp_nopush on;
    # Envia headers HTTP junto com o início do arquivo
    # Reduz número de pacotes TCP
    
    tcp_nodelay on;
    # Desabilita algoritmo Nagle (envia pacotes imediatamente)
    # Bom para conexões keep-alive
    
    keepalive_timeout 65;
    # Mantém conexão aberta por 65 segundos
    # Cliente pode reutilizar para múltiplas requisições
    
    
    # =========================================================================
    # COMPRESSÃO GZIP
    # =========================================================================
    
    gzip on;
    # Habilita compressão gzip
    
    gzip_vary on;
    # Adiciona header "Vary: Accept-Encoding"
    # Importante para caches
    
    gzip_proxied any;
    # Comprime respostas mesmo de backends proxy
    
    gzip_comp_level 6;
    # Nível de compressão (1-9)
    # 6 é bom equilíbrio entre compressão e CPU
    
    gzip_types text/plain text/css text/xml application/json 
               application/javascript application/xml+rss;
    # Quais tipos comprimir
    # Não comprime imagens (já são comprimidas)
    
    
    # =========================================================================
    # UPLOAD
    # =========================================================================
    
    client_max_body_size 20M;
    # Tamanho máximo de upload
    # Currículos PDF geralmente têm < 5MB
    
    
    # =========================================================================
    # UPSTREAM (BACKEND)
    # =========================================================================
    
    upstream app_server {
        server 127.0.0.1:8000 fail_timeout=0;
        # Define o backend (Gunicorn rodando na porta 8000)
        # fail_timeout=0: não marca como "falho" temporariamente
        
        # Se tivesse múltiplos backends:
        # server 127.0.0.1:8000 weight=3;  # 3x mais requisições
        # server 127.0.0.1:8001 weight=1;
        # server 127.0.0.1:8002 backup;    # só se outros falharem
    }
    
    
    # =========================================================================
    # SERVIDOR
    # =========================================================================
    
    server {
        listen 80;
        # Porta que o Nginx escuta
        
        server_name _;
        # _ = qualquer hostname
        # Em produção: server_name exemplo.com www.exemplo.com;
        
        
        # =====================================================================
        # HEADERS DE SEGURANÇA
        # =====================================================================
        
        add_header X-Frame-Options "SAMEORIGIN" always;
        # Previne clickjacking
        # Página não pode ser carregada em iframe de outro site
        
        add_header X-Content-Type-Options "nosniff" always;
        # Previne MIME type sniffing
        # Browser respeita Content-Type declarado
        
        add_header X-XSS-Protection "1; mode=block" always;
        # Ativa proteção XSS do browser
        
        
        # =====================================================================
        # HEALTH CHECK
        # =====================================================================
        
        location /health {
            proxy_pass http://app_server;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        # location: define como tratar URLs específicas
        # /health vai para o backend
        
        
        # =====================================================================
        # ARQUIVOS ESTÁTICOS
        # =====================================================================
        
        location /static/ {
            alias /app/static/;
            # alias: mapeia URL para diretório no disco
            # /static/css/style.css → /app/static/css/style.css
            
            expires 1d;
            # Cache por 1 dia
            
            add_header Cache-Control "public, immutable";
            # public: pode ser cacheado por proxies
            # immutable: arquivo nunca muda (versione com ?v=1.0)
        }
        # Nginx serve arquivos estáticos diretamente
        # Muito mais rápido que passar pelo Python
        
        
        # =====================================================================
        # PROXY PARA APLICAÇÃO
        # =====================================================================
        
        location / {
            proxy_pass http://app_server;
            # Encaminha requisição para o upstream definido acima
            
            proxy_redirect off;
            # Não reescreve headers Location nas respostas
            
            # Headers importantes para o backend saber info do cliente
            proxy_set_header Host $host;
            # Hostname original (exemplo.com)
            
            proxy_set_header X-Real-IP $remote_addr;
            # IP real do cliente
            
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            # Lista de proxies pelos quais passou
            
            proxy_set_header X-Forwarded-Proto $scheme;
            # http ou https
            
            # Timeouts para uploads grandes
            proxy_connect_timeout 300;
            proxy_send_timeout 300;
            proxy_read_timeout 300;
            # 300 segundos = 5 minutos
            # Necessário para análise de PDFs grandes
        }
        
        
        # =====================================================================
        # SEGURANÇA
        # =====================================================================
        
        location ~ /\. {
            deny all;
            # Bloqueia acesso a arquivos ocultos (.env, .git, etc)
            # ~ significa regex
            # /\. = qualquer URL com /. (ponto)
        }
    }
}
```

## 4.3 Comandos Nginx Importantes

```bash
# Testar configuração (SEMPRE faça antes de reiniciar!)
nginx -t

# Recarregar configuração (sem derrubar conexões)
nginx -s reload

# Parar
nginx -s stop

# Ver processos
ps aux | grep nginx

# Ver logs em tempo real
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

# 5. GUNICORN - SERVIDOR WSGI

## 5.1 O que é WSGI?

WSGI = **Web Server Gateway Interface**

É um **padrão** que define como servidores web se comunicam com aplicações Python.

```
HTTP Request → Nginx → Gunicorn (WSGI) → Flask
HTTP Response ← Nginx ← Gunicorn (WSGI) ← Flask
```

### Por que não usar o servidor do Flask em produção?

O servidor embutido do Flask (`app.run()`) é apenas para **desenvolvimento**:
- Single-threaded (uma requisição por vez)
- Não otimizado para performance
- Não gerencia workers/processos

Gunicorn é feito para **produção**:
- Multi-process (múltiplas requisições simultâneas)
- Gerencia workers automaticamente
- Reinicia workers com problemas
- Otimizado para performance

## 5.2 Nosso gunicorn.conf.py Explicado

```python
# =============================================================================
# Gunicorn Configuration
# =============================================================================

import multiprocessing
import os

# =============================================================================
# BIND (ONDE ESCUTAR)
# =============================================================================

bind = "0.0.0.0:8000"
# IP:porta onde Gunicorn escuta
# 0.0.0.0 = aceita conexões de qualquer IP
# 8000 = porta (Nginx encaminha para cá)

# Alternativa: socket Unix (mais rápido se mesmo servidor)
# bind = "unix:/tmp/gunicorn.sock"


# =============================================================================
# WORKERS (PROCESSOS)
# =============================================================================

workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
# Fórmula recomendada: (2 × CPUs) + 1
# 2 CPUs = 5 workers
# 4 CPUs = 9 workers
#
# Cada worker é um processo separado
# Se um travar, outros continuam funcionando
#
# Variável de ambiente permite ajustar sem mudar código

worker_class = "sync"
# Tipo de worker:
# - sync: síncrono (padrão, bom para maioria dos casos)
# - gevent: assíncrono (bom para muitas conexões lentas)
# - uvicorn.workers.UvicornWorker: para ASGI (FastAPI)

worker_connections = 1000
# Máximo de conexões simultâneas por worker
# Só relevante para workers assíncronos (gevent)

max_requests = 1000
# Reinicia worker após N requisições
# Previne memory leaks

max_requests_jitter = 50
# Adiciona variação aleatória (0-50) ao max_requests
# Evita que todos workers reiniciem ao mesmo tempo


# =============================================================================
# TIMEOUTS
# =============================================================================

timeout = 120
# Tempo máximo para processar uma requisição (segundos)
# Se demorar mais, worker é morto e reiniciado
# 120s = 2 minutos (suficiente para PDFs grandes)

graceful_timeout = 30
# Tempo para worker finalizar requisições em andamento
# Após SIGTERM, worker tem 30s para terminar

keepalive = 5
# Mantém conexão com Nginx aberta por 5 segundos
# Para reutilização em próximas requisições


# =============================================================================
# LOGGING
# =============================================================================

accesslog = "-"
# Onde salvar logs de acesso
# "-" = stdout (para Docker capturar)

errorlog = "-"
# Onde salvar logs de erro
# "-" = stderr

loglevel = os.getenv("LOG_LEVEL", "info")
# Nível: debug, info, warning, error, critical

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
# Formato do log:
# %(h)s = host (IP do cliente)
# %(t)s = timestamp
# %(r)s = request line ("GET /health HTTP/1.1")
# %(s)s = status code
# %(D)s = tempo em microsegundos


# =============================================================================
# PROCESSO
# =============================================================================

proc_name = "leitura-ats"
# Nome do processo (aparece no ps aux)

daemon = False
# False = não roda em background
# Importante para Docker e Supervisor gerenciarem

pidfile = None
# Arquivo PID (não precisamos, Supervisor gerencia)

umask = 0
# Permissões de arquivos criados

user = None
group = None
# Usuário/grupo para rodar (None = usuário atual)

tmp_upload_dir = None
# Diretório temporário para uploads
# None = usa padrão do sistema


# =============================================================================
# HOOKS (CALLBACKS)
# =============================================================================

def on_starting(server):
    """Chamado quando Gunicorn está iniciando"""
    print("Gunicorn iniciando...")

def on_reload(server):
    """Chamado quando Gunicorn recarrega configuração"""
    print("Gunicorn recarregando...")

def worker_int(worker):
    """Chamado quando worker recebe SIGINT"""
    print(f"Worker {worker.pid} interrompido")

def worker_abort(worker):
    """Chamado quando worker é abortado (timeout)"""
    print(f"Worker {worker.pid} abortado!")
```

## 5.3 Comandos Gunicorn Importantes

```bash
# Iniciar Gunicorn
gunicorn --config gunicorn_config.py wsgi:app

# Iniciar com configurações inline
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
#        -w: workers
#        -b: bind

# Recarregar (sem derrubar)
kill -HUP $(cat /tmp/gunicorn.pid)

# Ver workers
ps aux | grep gunicorn

# Parar gracefully
kill -TERM $(cat /tmp/gunicorn.pid)
```

---

# 6. SUPERVISOR - GERENCIADOR DE PROCESSOS

## 6.1 O que é Supervisor?

Supervisor é um **gerenciador de processos** que:
- Inicia processos automaticamente
- Reinicia se travarem
- Gerencia múltiplos processos como um grupo
- Fornece interface para controle

### Por que precisamos?

Docker espera **um processo** por container. Mas queremos **Nginx + Gunicorn** no mesmo container:

```
Container
├── Supervisor (PID 1)
│   ├── Nginx (gerenciado)
│   └── Gunicorn (gerenciado)
```

## 6.2 Nosso supervisord.conf Explicado

```ini
; =============================================================================
; SUPERVISOR PRINCIPAL
; =============================================================================
; Linhas com ; são comentários

[supervisord]
nodaemon=true
; nodaemon=true: NÃO roda em background
; Importante! Docker precisa de um processo em foreground

user=root
; Usuário que roda o Supervisor
; Precisa ser root para iniciar Nginx na porta 80

logfile=/var/log/supervisor/supervisord.log
; Onde salvar logs do próprio Supervisor

pidfile=/tmp/supervisord.pid
; Arquivo com PID do Supervisor

loglevel=info
; Nível de log: debug, info, warn, error, critical


; =============================================================================
; INTERFACE DE CONTROLE
; =============================================================================

[unix_http_server]
file=/tmp/supervisor.sock
; Socket Unix para comunicação com supervisorctl
; Permite: supervisorctl status, restart, etc.

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface
; Habilita interface RPC (necessário para supervisorctl)

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock
; Como supervisorctl se conecta ao supervisord


; =============================================================================
; PROGRAMA: NGINX
; =============================================================================

[program:nginx]
; program: define um processo gerenciado
; nginx: nome do programa (usado em: supervisorctl restart nginx)

command=/usr/sbin/nginx -g "daemon off;"
; Comando para iniciar
; -g "daemon off;": NÃO rodar em background
; Supervisor precisa controlar o processo

autostart=true
; Inicia automaticamente quando Supervisor inicia

autorestart=true
; Reinicia automaticamente se morrer

priority=10
; Ordem de inicialização (menor = primeiro)
; Nginx inicia antes do Gunicorn

stdout_logfile=/dev/stdout
; Onde enviar stdout
; /dev/stdout = Docker captura

stdout_logfile_maxbytes=0
; Sem limite de tamanho (0 = infinito)
; Necessário para /dev/stdout

stderr_logfile=/dev/stderr
; Onde enviar stderr

stderr_logfile_maxbytes=0

startsecs=0
; Segundos que processo deve rodar para ser considerado "started"
; 0 = imediato


; =============================================================================
; PROGRAMA: GUNICORN
; =============================================================================

[program:gunicorn]
command=/usr/local/bin/gunicorn -c /app/gunicorn/gunicorn.conf.py wsgi:app
; Inicia Gunicorn com nosso arquivo de configuração

directory=/app
; Diretório de trabalho
; Gunicorn executa A PARTIR deste diretório

user=appuser
; Usuário que executa (NÃO root!)
; Segurança: Gunicorn roda com permissões limitadas

autostart=true
autorestart=true

priority=20
; Inicia DEPOIS do Nginx (10 < 20)

stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

environment=
    PYTHONUNBUFFERED="1",
    PYTHONDONTWRITEBYTECODE="1"
; Variáveis de ambiente para este processo
; Formato: VAR1="valor1",VAR2="valor2"


; =============================================================================
; GRUPOS (OPCIONAL)
; =============================================================================

; [group:app]
; programs=nginx,gunicorn
; priority=999
; 
; Permite controlar múltiplos programas juntos:
; supervisorctl restart app:*
```

## 6.3 Comandos Supervisor Importantes

```bash
# Status de todos os processos
supervisorctl status

# Exemplo de saída:
# nginx                            RUNNING   pid 10, uptime 0:05:23
# gunicorn                         RUNNING   pid 11, uptime 0:05:23

# Reiniciar um processo
supervisorctl restart nginx
supervisorctl restart gunicorn

# Reiniciar todos
supervisorctl restart all

# Parar um processo
supervisorctl stop nginx

# Ver logs de um processo
supervisorctl tail -f nginx
supervisorctl tail -f gunicorn

# Recarregar configuração
supervisorctl reread
supervisorctl update

# Entrar no shell interativo
supervisorctl
# supervisor> status
# supervisor> restart nginx
# supervisor> quit
```

---

# 7. TERRAFORM - INFRAESTRUTURA AWS

## 7.1 O que é Terraform?

Terraform é uma ferramenta de **Infrastructure as Code (IaC)**. Você descreve a infraestrutura que quer em arquivos `.tf`, e o Terraform cria/modifica/destrói recursos na nuvem.

### Benefícios:
- **Versionável**: código no Git, histórico de mudanças
- **Reproduzível**: mesmo código = mesma infraestrutura
- **Documentação**: código É a documentação
- **Automação**: CI/CD pode aplicar mudanças

### Conceitos Básicos:

```
Terraform
├── Provider (AWS, Azure, GCP...)
│   ├── Resource (EC2, S3, VPC...)
│   └── Data Source (busca info existente)
├── Variables (parâmetros)
├── Outputs (resultados)
└── State (estado atual)
```

## 7.2 Nosso main.tf Explicado

```hcl
# =============================================================================
# CONFIGURAÇÃO DO TERRAFORM
# =============================================================================

terraform {
  required_version = ">= 1.0"
  # Versão mínima do Terraform necessária
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
      # ~> 5.0 significa >= 5.0.0 e < 6.0.0
    }
  }
  
  # Backend: onde guardar o state
  # Descomente para usar S3 (recomendado em produção)
  # backend "s3" {
  #   bucket         = "meu-bucket-terraform"
  #   key            = "leitura-ats/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"  # Para locking
  # }
}


# =============================================================================
# PROVIDER AWS
# =============================================================================

provider "aws" {
  region = var.aws_region
  # região AWS (us-east-1, sa-east-1, etc)
  # var.aws_region vem do arquivo variables.tf
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
    # Tags aplicadas a TODOS os recursos
    # Facilita identificação e billing
  }
}


# =============================================================================
# VPC - REDE VIRTUAL
# =============================================================================

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  # Usa módulo pronto da comunidade
  # Muito mais fácil que criar tudo manualmente
  
  name = "${var.project_name}-vpc"
  # Nome da VPC (ex: leitura-ats-vpc)
  # ${} é interpolação de variáveis
  
  cidr = "10.0.0.0/16"
  # Bloco CIDR da VPC
  # /16 = 65.536 IPs disponíveis
  # 10.0.0.0 até 10.0.255.255
  
  azs = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  # Availability Zones (data centers)
  # us-east-1a, us-east-1b, us-east-1c
  # 3 AZs = alta disponibilidade
  
  # Subnets Públicas (têm IP público, acesso direto à internet)
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  # /24 = 256 IPs cada
  # Usadas por: Load Balancer, NAT Gateway
  
  # Subnets Privadas (sem IP público, mais seguras)
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  # Usadas por: EKS nodes, aplicação
  # Acessam internet via NAT Gateway
  
  enable_nat_gateway = true
  # NAT Gateway permite que subnets privadas acessem internet
  # (para updates, downloads, etc)
  
  single_nat_gateway = var.environment == "dev" ? true : false
  # Dev: 1 NAT (mais barato ~$32/mês)
  # Prod: 1 NAT por AZ (mais resiliente)
  # ? : é operador ternário (if/else inline)
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  # Habilita DNS interno da VPC
  
  # Tags para integração com Kubernetes
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
    # Indica que subnets públicas podem ter Load Balancer
  }
  
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
    # Indica que subnets privadas podem ter Load Balancer interno
  }
}


# =============================================================================
# EKS - KUBERNETES
# =============================================================================

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"
  
  cluster_name    = "${var.project_name}-eks-${var.environment}"
  cluster_version = "1.28"
  # Versão do Kubernetes
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  # Coloca EKS nas subnets privadas
  
  # Acesso ao cluster
  cluster_endpoint_public_access = true
  # Permite acessar kubectl de fora da VPC
  # Em produção real, pode ser false e usar VPN
  
  # Node Groups (VMs que rodam os containers)
  eks_managed_node_groups = {
    main = {
      name = "${var.project_name}-nodes"
      
      instance_types = var.eks_instance_types
      # Tipo de instância (t3.medium, t3.large, etc)
      
      min_size     = var.eks_min_size
      max_size     = var.eks_max_size
      desired_size = var.eks_desired_size
      # Auto-scaling: mínimo 2, máximo 4, desejado 2
      
      capacity_type = var.environment == "dev" ? "SPOT" : "ON_DEMAND"
      # SPOT: instâncias com desconto (~70% off) mas podem ser terminadas
      # ON_DEMAND: preço cheio mas garantido
      
      disk_size = 50
      # GB de disco EBS por node
      
      labels = {
        Environment = var.environment
      }
    }
  }
  
  # Add-ons do EKS
  cluster_addons = {
    coredns = {
      most_recent = true
      # DNS interno do cluster
    }
    kube-proxy = {
      most_recent = true
      # Networking do Kubernetes
    }
    vpc-cni = {
      most_recent = true
      # CNI da AWS (cada pod tem IP da VPC)
    }
  }
}


# =============================================================================
# ECR - CONTAINER REGISTRY
# =============================================================================

resource "aws_ecr_repository" "app" {
  name = "${var.project_name}-app"
  # Nome do repositório de imagens Docker
  
  image_tag_mutability = "MUTABLE"
  # MUTABLE: pode sobrescrever tags (ex: latest)
  # IMMUTABLE: cada tag é única
  
  image_scanning_configuration {
    scan_on_push = true
    # Escaneia vulnerabilidades automaticamente
  }
  
  encryption_configuration {
    encryption_type = "AES256"
    # Criptografia em repouso
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Manter últimas 10 imagens"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
  # Remove imagens antigas automaticamente
  # Mantém apenas as 10 mais recentes
}


# =============================================================================
# S3 - ARMAZENAMENTO
# =============================================================================

resource "aws_s3_bucket" "curriculos" {
  bucket = "${var.project_name}-curriculos-${var.environment}-${data.aws_caller_identity.current.account_id}"
  # Nome único global (inclui account_id)
}

resource "aws_s3_bucket_versioning" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id
  versioning_configuration {
    status = "Enabled"
    # Guarda versões anteriores de arquivos
    # Permite recuperar arquivos deletados/modificados
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
      # Criptografa arquivos automaticamente
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id
  
  rule {
    id     = "archive-old-files"
    status = "Enabled"
    
    transition {
      days          = 90
      storage_class = "GLACIER"
      # Após 90 dias: move para Glacier (mais barato)
    }
    
    expiration {
      days = 365
      # Após 365 dias: deleta
    }
  }
}


# =============================================================================
# CLOUDWATCH - LOGS
# =============================================================================

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 30
  # Logs são deletados após 30 dias
  # Reduz custos de armazenamento
}


# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_caller_identity" "current" {}
# Busca informações da conta AWS atual
# Usado para: account_id

data "aws_region" "current" {}
# Busca região atual
```

## 7.3 Nosso variables.tf Explicado

```hcl
# =============================================================================
# VARIÁVEIS
# =============================================================================
# Variáveis tornam o código reutilizável e configurável

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "leitura-ats"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Nome deve conter apenas letras minúsculas, números e hífens."
  }
  # validation: regra de validação
  # can(): retorna true se expressão for válida
  # regex(): testa padrão
}

variable "environment" {
  description = "Ambiente (dev ou prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment deve ser 'dev' ou 'prod'."
  }
}

variable "aws_region" {
  description = "Região AWS"
  type        = string
  default     = "us-east-1"
}

variable "eks_instance_types" {
  description = "Tipos de instância para nodes EKS"
  type        = list(string)
  default     = ["t3.medium"]
  # list(string): lista de strings
}

variable "eks_min_size" {
  description = "Número mínimo de nodes"
  type        = number
  default     = 2
}

variable "eks_max_size" {
  description = "Número máximo de nodes"
  type        = number
  default     = 4
}

variable "eks_desired_size" {
  description = "Número desejado de nodes"
  type        = number
  default     = 2
}
```

## 7.4 Nosso outputs.tf Explicado

```hcl
# =============================================================================
# OUTPUTS
# =============================================================================
# Valores retornados após terraform apply
# Úteis para: scripts, documentação, outros módulos

output "vpc_id" {
  description = "ID da VPC"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "Nome do cluster EKS"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint do cluster EKS"
  value       = module.eks.cluster_endpoint
}

output "ecr_repository_url" {
  description = "URL do repositório ECR"
  value       = aws_ecr_repository.app.repository_url
  # Exemplo: 123456789.dkr.ecr.us-east-1.amazonaws.com/leitura-ats-app
}

output "s3_bucket_curriculos" {
  description = "Nome do bucket S3"
  value       = aws_s3_bucket.curriculos.id
}

output "configure_kubectl" {
  description = "Comando para configurar kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
```

## 7.5 Comandos Terraform Importantes

```bash
# INICIALIZAR (baixa providers e módulos)
terraform init

# PLANEJAR (mostra o que será feito)
terraform plan

# Exemplo de saída:
# + aws_s3_bucket.curriculos will be created
# ~ aws_ecr_repository.app will be updated
# - aws_cloudwatch_log_group.old will be destroyed

# APLICAR (cria/modifica recursos)
terraform apply
# Digite 'yes' para confirmar

# Aplicar sem confirmação (CI/CD)
terraform apply -auto-approve

# DESTRUIR TUDO
terraform destroy
# ⚠️ CUIDADO! Deleta todos os recursos

# VER ESTADO ATUAL
terraform show

# VER OUTPUTS
terraform output
terraform output ecr_repository_url

# FORMATAR CÓDIGO
terraform fmt

# VALIDAR SINTAXE
terraform validate

# WORKSPACES (múltiplos ambientes)
terraform workspace list
terraform workspace new dev
terraform workspace select prod
```

---

# 8. KUBERNETES - ORQUESTRAÇÃO

## 8.1 O que é Kubernetes?

Kubernetes (K8s) é um **orquestrador de containers**. Ele gerencia:
- Deploy de containers
- Escala (mais/menos réplicas)
- Load balancing
- Self-healing (reinicia containers com problema)
- Rolling updates

### Conceitos Principais:

```
Cluster
├── Nodes (VMs)
│   ├── Pods (menor unidade)
│   │   └── Containers
│   └── Pods
└── Nodes

Workloads:
- Pod: 1+ containers rodando juntos
- Deployment: gerencia Pods (replicas, updates)
- Service: expõe Pods (load balancer)
- ConfigMap: configurações
- Secret: senhas/tokens
```

## 8.2 Nosso deployment.yaml Explicado

```yaml
# =============================================================================
# DEPLOYMENT
# =============================================================================
# Deployment gerencia um conjunto de Pods idênticos

apiVersion: apps/v1
# Versão da API do Kubernetes
# apps/v1 é a versão estável para Deployments

kind: Deployment
# Tipo de recurso

metadata:
  name: leitura-ats
  # Nome do Deployment (usado em: kubectl get deployment leitura-ats)
  
  namespace: default
  # Namespace (isolamento lógico)
  # default é o namespace padrão
  
  labels:
    app: leitura-ats
    component: backend
  # Labels: chave-valor para identificar/agrupar recursos

spec:
  replicas: 2
  # Número de Pods para manter rodando
  # 2 = alta disponibilidade básica
  
  selector:
    matchLabels:
      app: leitura-ats
  # Como o Deployment encontra seus Pods
  # Pods com label app=leitura-ats são gerenciados por este Deployment
  
  strategy:
    type: RollingUpdate
    # Estratégia de atualização:
    # - RollingUpdate: atualiza aos poucos (padrão, zero downtime)
    # - Recreate: mata todos, cria novos (tem downtime)
    
    rollingUpdate:
      maxSurge: 1
      # Quantos Pods EXTRAS podem existir durante update
      # 1 = pode ter 3 Pods temporariamente (2 + 1)
      
      maxUnavailable: 0
      # Quantos Pods podem estar INDISPONÍVEIS durante update
      # 0 = sempre ter pelo menos 2 rodando
  
  template:
    # Template do Pod
    metadata:
      labels:
        app: leitura-ats
        version: v1.0.0
      
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "5000"
        # Anotações para Prometheus coletar métricas
    
    spec:
      # Especificação do Pod
      
      serviceAccountName: leitura-ats-sa
      # ServiceAccount para permissões IRSA
      
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      # Segurança a nível de Pod:
      # - Não roda como root
      # - Usa UID/GID 1000
      
      containers:
        - name: app
          # Nome do container
          
          image: 123456789.dkr.ecr.us-east-1.amazonaws.com/leitura-ats-app:latest
          # Imagem Docker a usar
          # Substitua pelo seu ECR URL
          
          imagePullPolicy: Always
          # Sempre baixa a imagem (importante para :latest)
          # IfNotPresent: só baixa se não tiver local
          # Never: nunca baixa (usa local)
          
          ports:
            - name: http
              containerPort: 5000
              protocol: TCP
          # Porta que o container expõe
          
          env:
            - name: FLASK_ENV
              value: "production"
            
            - name: S3_BUCKET_CURRICULOS
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: s3_bucket_name
            # Lê valor do ConfigMap
            
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secret
                  key: flask-secret-key
            # Lê valor do Secret
          
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            # REQUESTS: recursos GARANTIDOS
            # 250m = 0.25 CPU (250 milicores)
            # 256Mi = 256 MiB de memória
            #
            # Kubernetes usa requests para agendar Pod em Node
            # que tenha esses recursos disponíveis
            
            limits:
              cpu: "500m"
              memory: "512Mi"
            # LIMITS: máximo que pode usar
            # Se ultrapassar memória: Pod é morto (OOMKilled)
            # Se ultrapassar CPU: é throttled (desacelerado)
          
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          # LIVENESS PROBE: "O container está vivo?"
          # - Chama GET /health na porta 5000
          # - Espera 10s antes de começar
          # - Verifica a cada 30s
          # - Timeout de 5s
          # - Após 3 falhas: REINICIA o container
          
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          # READINESS PROBE: "O container está pronto para receber tráfego?"
          # - Se falhar: remove do Service (não recebe requisições)
          # - NÃO reinicia o container
          # - Útil durante startup ou quando temporariamente ocupado
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - leitura-ats
                topologyKey: kubernetes.io/hostname
      # ANTI-AFFINITY: prefere colocar Pods em Nodes DIFERENTES
      # Se Node 1 cair, ainda tem Pod no Node 2
      # preferredDuringScheduling: é preferência, não obrigação

---
# =============================================================================
# HORIZONTAL POD AUTOSCALER (HPA)
# =============================================================================
# Escala automaticamente baseado em métricas

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler

metadata:
  name: leitura-ats-hpa

spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: leitura-ats
  # Qual Deployment escalar
  
  minReplicas: 2
  maxReplicas: 10
  # Limites de escala
  
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    # Escala quando uso médio de CPU > 70%
    
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    # Escala quando uso médio de memória > 80%
  
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    # Scale DOWN: espera 5 minutos de estabilidade
    # Remove máximo 50% dos Pods por vez
    
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
    # Scale UP: imediato
    # Pode dobrar número de Pods a cada 15s

---
# =============================================================================
# POD DISRUPTION BUDGET (PDB)
# =============================================================================
# Garante mínimo de Pods durante manutenção

apiVersion: policy/v1
kind: PodDisruptionBudget

metadata:
  name: leitura-ats-pdb

spec:
  minAvailable: 1
  # Sempre manter pelo menos 1 Pod rodando
  # Kubernetes não vai derrubar Pods se ficar abaixo disso
  
  selector:
    matchLabels:
      app: leitura-ats
```

## 8.3 Nosso service.yaml Explicado

```yaml
# =============================================================================
# SERVICE
# =============================================================================
# Service expõe Pods para receber tráfego

apiVersion: v1
kind: Service

metadata:
  name: leitura-ats-service

spec:
  type: LoadBalancer
  # Tipos de Service:
  # - ClusterIP: só acessível dentro do cluster (padrão)
  # - NodePort: expõe em porta do Node
  # - LoadBalancer: cria Load Balancer externo (AWS ELB)
  
  selector:
    app: leitura-ats
  # Quais Pods recebem tráfego
  # Pods com label app=leitura-ats
  
  ports:
    - name: http
      port: 80
      # Porta do Service (externa)
      
      targetPort: 5000
      # Porta do container
      
      protocol: TCP
  
  # Fluxo:
  # Internet → LoadBalancer:80 → Service:80 → Pod:5000
```

## 8.4 Nosso configmap.yaml Explicado

```yaml
# =============================================================================
# CONFIGMAP
# =============================================================================
# Armazena configurações (não sensíveis)

apiVersion: v1
kind: ConfigMap

metadata:
  name: app-config

data:
  # Chave: valor
  flask_env: "production"
  log_level: "INFO"
  s3_bucket_name: "leitura-ats-curriculos-dev"
  aws_region: "us-east-1"

# Uso no Deployment:
# env:
#   - name: S3_BUCKET
#     valueFrom:
#       configMapKeyRef:
#         name: app-config
#         key: s3_bucket_name

---
# =============================================================================
# SECRET
# =============================================================================
# Armazena dados sensíveis (senhas, tokens)

apiVersion: v1
kind: Secret

metadata:
  name: app-secret

type: Opaque
# Tipo genérico

data:
  # Valores em BASE64!
  flask-secret-key: bWluaGEtY2hhdmUtc2VjcmV0YS1zdXBlci1zZWd1cmE=
  # echo -n "minha-chave-secreta" | base64

# Uso no Deployment:
# env:
#   - name: SECRET_KEY
#     valueFrom:
#       secretKeyRef:
#         name: app-secret
#         key: flask-secret-key

---
# =============================================================================
# SERVICE ACCOUNT
# =============================================================================
# Identidade para Pods acessarem AWS via IRSA

apiVersion: v1
kind: ServiceAccount

metadata:
  name: leitura-ats-sa
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/leitura-ats-pod-role
  # IRSA: vincula ServiceAccount a uma IAM Role
  # Pods usando este ServiceAccount têm as permissões da Role
  # Sem precisar de access keys hardcoded!
```

## 8.5 Comandos kubectl Importantes

```bash
# CONFIGURAR acesso ao cluster
aws eks update-kubeconfig --region us-east-1 --name leitura-ats-eks-dev

# VER RECURSOS
kubectl get pods                    # Listar Pods
kubectl get pods -o wide           # Com mais detalhes (IP, Node)
kubectl get deployments            # Listar Deployments
kubectl get services               # Listar Services
kubectl get all                    # Listar tudo

# DESCREVER (detalhes + eventos)
kubectl describe pod <nome>
kubectl describe deployment leitura-ats
kubectl describe service leitura-ats-service

# LOGS
kubectl logs <pod-name>            # Logs do Pod
kubectl logs -f <pod-name>         # Follow (tempo real)
kubectl logs deployment/leitura-ats  # Logs do Deployment

# APLICAR CONFIGURAÇÕES
kubectl apply -f deployment.yaml
kubectl apply -f .                 # Todos os .yaml do diretório

# DELETAR
kubectl delete -f deployment.yaml
kubectl delete pod <nome>

# ENTRAR NO CONTAINER
kubectl exec -it <pod-name> -- bash
kubectl exec -it <pod-name> -- /bin/sh  # Se não tiver bash

# ESCALAR
kubectl scale deployment leitura-ats --replicas=5

# ROLLING UPDATE
kubectl set image deployment/leitura-ats app=novo-image:v2
kubectl rollout status deployment/leitura-ats
kubectl rollout undo deployment/leitura-ats  # Rollback

# MÉTRICAS
kubectl top nodes
kubectl top pods

# PORT FORWARD (acesso local temporário)
kubectl port-forward svc/leitura-ats-service 8080:80
# Acesse http://localhost:8080

# DEBUG
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pod <pod> | grep -A 10 Events
```

---

# 9. FLUXO COMPLETO DE UMA REQUISIÇÃO

## Do Upload do PDF até a Resposta

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLUXO DA REQUISIÇÃO                                │
└─────────────────────────────────────────────────────────────────────────────┘

1. USUÁRIO
   │
   │ POST /analyze (arquivo PDF)
   │
   ▼
2. DNS (Route 53)
   │
   │ leitura-ats.exemplo.com → IP do Load Balancer
   │
   ▼
3. AWS LOAD BALANCER (ALB)
   │
   │ Recebe HTTPS, termina SSL
   │ Distribui entre Nodes disponíveis
   │
   ▼
4. KUBERNETES SERVICE
   │
   │ Distribui entre Pods com label app=leitura-ats
   │ Load balancing round-robin
   │
   ▼
5. POD (Container)
   │
   ├──────────────────────────────────────────────────────────────────┐
   │                                                                   │
   │  ┌────────────┐                                                  │
   │  │ SUPERVISOR │ (gerencia processos)                             │
   │  │    │       │                                                  │
   │  │    ├───────┴────────────┐                                    │
   │  │    │                    │                                    │
   │  │    ▼                    ▼                                    │
   │  │ ┌──────┐          ┌─────────┐                                │
   │  │ │NGINX │   :80    │GUNICORN │  :8000                         │
   │  │ │      │ ───────▶ │         │                                │
   │  │ │      │          │ Workers │                                │
   │  │ └──────┘          └────┬────┘                                │
   │  │                        │                                      │
   │  │                        ▼                                      │
   │  │                   ┌─────────┐                                │
   │  │                   │  FLASK  │                                │
   │  │                   │   APP   │                                │
   │  │                   └────┬────┘                                │
   │  │                        │                                      │
   │  └────────────────────────┼──────────────────────────────────────┘
   │                           │
   └───────────────────────────┘
                               │
                               ▼
6. FLASK - PROCESSAMENTO
   │
   │ a) Recebe arquivo PDF
   │ b) Salva temporariamente
   │ c) Extrai texto com PyMuPDF
   │ d) Analisa com motor ATS (NLTK)
   │ e) Calcula scores
   │ f) Retorna JSON
   │
   ▼
7. RESPOSTA (caminho inverso)
   │
   │ JSON → Gunicorn → Nginx → Service → LoadBalancer → Usuário
   │
   ▼
8. FRONTEND
   │
   │ JavaScript renderiza resultado
   │ Mostra score, keywords, sugestões
   │
   ✓ FIM
```

## Tempos Típicos

| Etapa | Tempo |
|-------|-------|
| DNS lookup | ~50ms |
| TLS handshake | ~100ms |
| Load Balancer → Pod | ~10ms |
| Nginx → Gunicorn | ~1ms |
| Extração PDF | ~500ms-2s |
| Análise ATS | ~100-500ms |
| **Total** | **~1-3 segundos** |

---

# 10. GLOSSÁRIO DE TERMOS

| Termo | Significado |
|-------|-------------|
| **API** | Application Programming Interface - forma de sistemas se comunicarem |
| **ATS** | Applicant Tracking System - sistema que empresas usam para filtrar currículos |
| **AZ** | Availability Zone - data center isolado dentro de uma região AWS |
| **CIDR** | Classless Inter-Domain Routing - notação para blocos de IP (ex: 10.0.0.0/16) |
| **Container** | Ambiente isolado para rodar aplicação (mais leve que VM) |
| **DNS** | Domain Name System - traduz nomes (google.com) para IPs |
| **EKS** | Elastic Kubernetes Service - Kubernetes gerenciado pela AWS |
| **ECR** | Elastic Container Registry - armazena imagens Docker na AWS |
| **FLASK** | Microframework Python para criar aplicações web |
| **Gunicorn** | Green Unicorn - servidor WSGI para Python em produção |
| **HPA** | Horizontal Pod Autoscaler - escala Pods baseado em métricas |
| **IAM** | Identity and Access Management - permissões na AWS |
| **IRSA** | IAM Roles for Service Accounts - forma segura de dar permissões a Pods |
| **Kubernetes** | Orquestrador de containers (gerencia deploy, escala, etc) |
| **NAT Gateway** | Permite recursos em subnet privada acessar internet |
| **Nginx** | Servidor web/proxy de alta performance |
| **NLP** | Natural Language Processing - processamento de linguagem natural |
| **NLTK** | Natural Language Toolkit - biblioteca Python para NLP |
| **Node** | Máquina (VM) que faz parte do cluster Kubernetes |
| **PDB** | Pod Disruption Budget - garante mínimo de Pods disponíveis |
| **Pod** | Menor unidade no Kubernetes - 1 ou mais containers rodando juntos |
| **Proxy Reverso** | Servidor que fica na frente da aplicação (Nginx → Gunicorn) |
| **S3** | Simple Storage Service - armazenamento de objetos da AWS |
| **Service (K8s)** | Abstração que expõe Pods para receber tráfego |
| **SSL/TLS** | Protocolos de criptografia (HTTPS) |
| **Stemming** | Reduzir palavra à raiz (correndo → corr) |
| **Supervisor** | Gerenciador de processos (mantém Nginx e Gunicorn rodando) |
| **Terraform** | Ferramenta de Infrastructure as Code |
| **TF-IDF** | Term Frequency-Inverse Document Frequency - medida de importância de palavras |
| **Tokenização** | Dividir texto em palavras/unidades |
| **VPC** | Virtual Private Cloud - rede virtual isolada na AWS |
| **WSGI** | Web Server Gateway Interface - padrão de comunicação Python ↔ servidor web |

---

# FIM DO GUIA

Este documento cobre todas as tecnologias e configurações do projeto Leitura ATS. 

Para dúvidas específicas ou atualizações, consulte a documentação oficial de cada ferramenta:
- Flask: https://flask.palletsprojects.com/
- Docker: https://docs.docker.com/
- Nginx: https://nginx.org/en/docs/
- Gunicorn: https://docs.gunicorn.org/
- Supervisor: http://supervisord.org/
- Terraform: https://www.terraform.io/docs
- Kubernetes: https://kubernetes.io/docs/

---

**Autor:** Ricardo da Silva Júnior  
**Data:** Abril 2026  
**Versão:** 1.0.0
