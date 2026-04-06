# 🏗️ Arquitetura Atual

Documentação da arquitetura real implementada no projeto.

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
| `app.py` | Rotas HTTP, configuração Flask |
| `wsgi.py` | Entry point para Gunicorn |
| `gunicorn_config.py` | Configuração do servidor WSGI |

**Rotas:**
| Endpoint | Método | Função |
|----------|--------|--------|
| `/` | GET | Página inicial (upload) |
| `/analyze` | POST | Recebe PDF, retorna análise JSON |
| `/health` | GET | Health check para monitoramento |

### 3. Engine ATS

| Módulo | Função |
|--------|--------|
| `leitura_ats/engine.py` | Motor principal de análise |
| `leitura_ats/keywords.py` | Dicionário de palavras-chave técnicas |
| `extracao_pdf/extractor.py` | Extração de texto do PDF |
| `analise_keywords/analyzer.py` | Análise de keywords e scoring |

**Pipeline de Análise:**
```
PDF → Extração (PyMuPDF) → Texto → NLP (NLTK) → Scoring → JSON
```

### 4. Logs

Cada análise gera um arquivo em `logs/` (na raiz do projeto):
```
analise_20260405_143052.txt
```

**Conteúdo:**
- Timestamp da análise
- Nome do arquivo enviado
- Texto extraído (para debug)
- Keywords encontradas
- Scores parciais e final
- Dados estruturados extraídos

---

## Fluxo de Dados

```
┌──────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐
│  Upload  │───▶│  Flask    │───▶│  Extração  │───▶│  NLP     │
│   PDF    │    │  Recebe   │    │  PyMuPDF   │    │  NLTK    │
└──────────┘    └───────────┘    └────────────┘    └──────────┘
                                                        │
┌──────────┐    ┌───────────┐    ┌────────────┐        │
│  Exibe   │◀───│  Flask    │◀───│  Scoring   │◀───────┘
│  Result  │    │  Response │    │  Engine    │
└──────────┘    └───────────┘    └────────────┘
```

**Detalhamento:**

1. **Upload:** Arquivo PDF enviado via multipart/form-data
2. **Recepção:** Flask valida tipo e tamanho do arquivo
3. **Extração:** PyMuPDF converte PDF em texto puro
4. **NLP:** NLTK tokeniza e processa o texto
   - Stemming com RSLPStemmer (português)
   - Identificação de seções
   - Extração de entidades (nome, empresas, datas)
5. **Scoring:** Cálculo do score ATS
   - Keywords: 40% (palavras-chave técnicas encontradas)
   - Estrutura: 35% (seções identificadas)
   - Legibilidade: 25% (clareza do texto)
6. **Resposta:** JSON com análise completa

---

## Estrutura de Diretórios

```
aplicacao/
├── app.py                    # Aplicação Flask principal
├── wsgi.py                   # Entry point Gunicorn
├── gunicorn_config.py        # Configuração Gunicorn
├── __init__.py               # Pacote Python
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

### NLTK Data

| Dataset | Função |
|---------|--------|
| punkt | Tokenização de sentenças |
| punkt_tab | Dados tabulares para tokenização |
| rslp | Stemmer para português |

---

## Configurações

### Flask (app.py)

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
```

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
