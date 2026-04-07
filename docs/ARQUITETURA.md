# 🏗️ Arquitetura Atual

Documentação da arquitetura do projeto de análise heurística de currículos técnicos em PDF, voltado para a área de TI.

---

## Visão Geral

```
┌──────────────────────────────────────────────────────────────────┐
│                         AMBIENTE LOCAL                            │
│                                                                   │
│  ┌─────────────┐       ┌─────────────────────────────────────┐   │
│  │  Navegador  │       │           Aplicação Python           │   │
│  │             │       │                                      │   │
│  │  ┌───────┐  │  HTTP │  ┌─────────┐    ┌────────────────┐  │   │
│  │  │ HTML  │──┼───────┼─▶│ Flask   │───▶│ Engine ATS     │  │   │
│  │  │ CSS   │  │  :5000│  │  (app)  │    │                │  │   │
│  │  │ JS    │◀─┼───────┼──│         │◀───│ - Extração PDF │  │   │
│  │  └───────┘  │ JSON  │  └─────────┘    │ - NLP/NLTK     │  │   │
│  │             │       │       │         │ - Scoring      │  │   │
│  └─────────────┘       │       │         └────────────────┘  │   │
│                        │       ▼                              │   │
│                        │  ┌─────────┐                         │   │
│                        │  │  Logs   │  logs/                  │   │
│                        │  └─────────┘                         │   │
│                        └─────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Componentes

### 1. Frontend (Navegador)

| Arquivo | Função |
|---------|--------|
| `templates/index.html` | Página única com upload drag-and-drop |
| `static/css/style.css` | Estilos visuais |
| `static/js/main.js` | Lógica de upload e exibição de resultados |

**Fluxo:**
1. Usuário arrasta PDF para área de upload
2. JavaScript envia arquivo via `fetch()` para `/analyze`
3. Resposta JSON é renderizada na página

### 2. Backend (Flask)

| Arquivo | Função |
|---------|--------|
| `app.py` | Factory function, rotas, handlers de erro, headers de segurança |
| `config.py` | Configuração centralizada (Dev/Prod/Test) |
| `validators/` | Validação robusta de uploads (extensão, MIME, magic bytes) |
| `utils/` | Respostas padronizadas e logging com privacidade |
| `wsgi.py` | Entry point para Gunicorn |
| `gunicorn_config.py` | Configuração do servidor WSGI |

**Rotas:**
| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Página inicial (upload) |
| `/analyze` | POST | Recebe PDF, retorna análise JSON |
| `/health` | GET | Health check para monitoramento |

**Segurança:**
- Validação de PDF em 3 camadas (extensão + MIME + magic bytes)
- Headers de segurança HTTP (XSS, clickjacking, nosniff)
- Sanitização de nomes de arquivo
- Logging com controle de privacidade (dados pessoais não logados por padrão)

### 3. Engine ATS

| Módulo | Função |
|--------|--------|
| `leitura_ats/engine.py` | Motor principal de análise |
| `leitura_ats/keywords.py` | Dicionário de palavras-chave técnicas |
| `extracao_pdf/extractor.py` | Extração de texto do PDF |
| `analise_keywords/analyzer.py` | Análise de keywords e scoring |

**Pipeline de Análise:**
```
Currículo técnico (PDF) → Validação → Extração (PyMuPDF) → Texto → NLP (NLTK) → Scoring heurístico → JSON
```

### 4. Logs

Cada análise gera um arquivo em `logs/` (na raiz do projeto):
```
analise_20260405_143052.txt
```

**Conteúdo (modo padrão - respeita privacidade):**
- Timestamp da análise
- Scores e classificação
- Keywords encontradas
- Feedback (alertas, sugestões, positivos)

**Conteúdo (modo detalhado - `LOG_DETAILED=true`):**
- Todo o acima, mais:
- Texto completo extraído
- Dados pessoais identificados

---

## Fluxo de Dados

```
┌──────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐
│  Upload  │───▶│  Validar  │───▶│  Extração  │───▶│  NLP     │
│   PDF    │    │  (3 cam.) │    │  PyMuPDF   │    │  NLTK    │
└──────────┘    └───────────┘    └────────────┘    └──────────┘
                                                        │
┌──────────┐    ┌───────────┐    ┌────────────┐        │
│  Exibe   │◀───│  Flask    │◀───│  Scoring   │◀───────┘
│  Result  │    │  Response │    │  Engine    │
└──────────┘    └───────────┘    └────────────┘
```

**Detalhamento:**

1. **Upload:** Arquivo PDF enviado via multipart/form-data
2. **Validação:** 3 camadas (extensão .pdf + MIME type + magic bytes)
3. **Extração:** PyMuPDF converte PDF em texto puro
4. **NLP:** NLTK tokeniza e processa o texto
   - Stemming com RSLPStemmer (português)
   - Identificação de seções
   - Extração de entidades (nome, empresas, datas)
5. **Scoring:** Cálculo do score heurístico
   - Keywords: 40% (palavras-chave técnicas encontradas)
   - Estrutura: 35% (seções identificadas)
   - Legibilidade: 25% (clareza do texto)
6. **Resposta:** JSON padronizado com análise completa do currículo técnico

---

## Estrutura de Diretórios

```
aplicacao/
├── app.py                    # Factory function e rotas
├── config.py                 # Configuração centralizada
├── wsgi.py                   # Entry point Gunicorn
├── gunicorn_config.py        # Configuração Gunicorn
├── __init__.py               # Pacote Python
│
├── validators/               # Validação de entrada
│   ├── __init__.py
│   └── upload.py             # Validação de PDF (3 camadas)
│
├── utils/                    # Utilitários
│   ├── __init__.py
│   ├── responses.py          # Respostas JSON padronizadas
│   └── logging.py            # Logger com privacidade
│
├── leitura_ats/              # Motor de análise ATS
│   ├── __init__.py
│   ├── engine.py             # Lógica principal
│   └── keywords.py           # Dicionário de termos
│
├── extracao_pdf/             # Extração de PDF
│   ├── __init__.py
│   └── extractor.py          # PyMuPDF wrapper
│
├── analise_keywords/         # Análise de keywords
│   ├── __init__.py
│   └── analyzer.py           # Matching e scoring
│
├── templates/                # HTML (Jinja2)
│   └── index.html            # Página única
│
├── static/                   # Arquivos estáticos
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js

# Na raiz do projeto:
tests/                        # Testes automatizados (pytest)
logs/                         # Logs de análise (gitignored)
```

---

## Dependências

### Python (requirements.txt)

| Pacote | Versão | Função |
|--------|--------|--------|
| Flask | 3.0.x | Framework web |
| Gunicorn | 21.x | Servidor WSGI produção |
| PyMuPDF | 1.24.x | Extração de PDF |
| NLTK | 3.8.x | Processamento de linguagem natural |
| pytest | 7.x | Testes automatizados |
| pytest-cov | 4.x | Coverage de testes |

### NLTK Data

| Dataset | Função |
|---------|--------|
| punkt | Tokenização de sentenças |
| punkt_tab | Dados tabulares para tokenização |
| rslp | Stemmer para português |

---

## Configurações

### Ambientes (config.py)

| Ambiente | `FLASK_ENV` | DEBUG | LOG_DETAILED |
|----------|-------------|-------|--------------|
| Development | development | True | True |
| Production | production | False | False |
| Testing | testing | True | False |

> **LOG_DETAILED** é `True` em Development para facilitar debugging, mas `False` em Production e Testing para proteger privacidade.

### Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `FLASK_ENV` ou `APP_ENV` | Ambiente de execução | development |
| `SECRET_KEY` | Chave secreta Flask | dev-key (mude em prod!) |
| `LOG_DETAILED` | Sobrescreve config para logar texto completo | (usa config do ambiente) |
| `LOG_LEVEL` | Nível de log | INFO |
| `GUNICORN_WORKERS` | Número de workers | auto (CPUs * 2 + 1) |

> **Nota:** `LOG_DETAILED` é definido no `config.py` por ambiente, mas pode ser sobrescrito via variável de ambiente se necessário.

### Gunicorn (gunicorn_config.py)

```python
bind = "0.0.0.0:5000"
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
timeout = 120
graceful_timeout = 30
loglevel = os.getenv("LOG_LEVEL", "info")
```

> Configuração dinâmica: o número de workers é calculado automaticamente com base nos CPUs disponíveis, mas pode ser sobrescrito via variável de ambiente `GUNICORN_WORKERS`.

---

## Decisões de Arquitetura

| Decisão | Justificativa |
|---------|---------------|
| Flask (não Django) | Projeto simples, não precisa ORM/admin |
| PyMuPDF (não pdfplumber) | Mais rápido, melhor extração |
| NLTK (não spaCy) | Leve, suficiente para stemming PT |
| Single-page | UX simples, sem navegação |
| Logs em arquivo | Debug local, sem infraestrutura externa |
| Factory pattern | Facilita testes e configuração por ambiente |
| Validação em 3 camadas | Segurança sem dependências externas |
| Logging com privacidade | LGPD compliance, opt-in para dados pessoais |

---

## Limitações Conhecidas

Ver [LIMITACOES.md](LIMITACOES.md) para lista completa.

**Resumo:**
- Sem OCR (PDF deve ter texto selecionável)
- Sem autenticação de usuários
- Sem persistência de análises em banco
- Logs locais (não centralizados)

---

## Evolução Planejada

Ver [ROADMAP.md](ROADMAP.md) para próximos passos.
