# 🔧 Manual de Instalação

> **Ambiente:** Linux ou WSL (Windows Subsystem for Linux).  
> Os scripts usam bash. Em Windows nativo, siga a instalação manual.

---

## Instalação Rápida

```bash
git clone https://github.com/ricardosilva-devops/leitura-ats-curriculo.git
cd leitura-ats-curriculo
./scripts/setup.sh
./scripts/start.sh
# Acessar: http://localhost:5000
```

O `setup.sh` faz automaticamente:
1. Cria ambiente virtual (`venv/`)
2. Instala dependências Python
3. Baixa dados NLTK
4. Cria pasta de logs

---

## Pré-requisitos

| Requisito | Versão | Verificar |
|-----------|--------|-----------|
| Python | 3.10+ | `python3 --version` |
| pip | 21.0+ | `pip --version` |
| Git | 2.0+ | `git --version` |
| Docker | 20.0+ (opcional) | `docker --version` |

---

## Instalação Manual

Se preferir não usar os scripts:

### 1. Clonar e criar ambiente

```bash
git clone https://github.com/ricardosilva-devops/leitura-ats-curriculo.git
cd leitura-ats-curriculo
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências instaladas:**
- Flask 3.0 (framework web)
- PyMuPDF 1.24 (extração de PDF)
- NLTK 3.8 (processamento de linguagem natural)
- Gunicorn 21.0 (servidor WSGI)

### 3. Baixar Dados NLTK

O NLTK precisa de dados para processamento de português:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"
```

**O que cada dado faz:**
- `punkt` - Tokenização de sentenças
- `punkt_tab` - Dados tabulares para tokenização
- `rslp` - Stemmer para português (Removedor de Sufixos da Língua Portuguesa)

### 4. Verificar Instalação

```bash
cd aplicacao
python -c "from app import app; print('✅ Aplicação carregada com sucesso!')"
```

---

## Executar a Aplicação

### Modo Desenvolvimento (Flask)

```bash
cd aplicacao
python app.py
```

**Output esperado:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Modo Produção (Gunicorn)

```bash
cd aplicacao
gunicorn --config gunicorn_config.py wsgi:app
```

---

## Validar Funcionamento

### 1. Health Check

```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{"status": "healthy", "service": "leitura-ats-curriculo"}
```

### 2. Interface Web

Abrir no navegador: http://localhost:5000

### 3. Testar Análise

Faça upload de um currículo em PDF pela interface ou via cURL:

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@seu-curriculo.pdf"
```

---

## Estrutura de Diretórios Após Instalação

```
leitura-ats-curriculo/
├── venv/                  # Ambiente virtual (criado por você)
├── aplicacao/
│   ├── app.py             # Aplicação Flask
│   ├── leitura_ats/       # Motor de análise ATS
│   ├── extracao_pdf/      # Extração de texto
│   ├── templates/         # HTML
│   └── static/            # CSS/JS
├── docs/                  # Documentação
├── scripts/               # Scripts operacionais
└── requirements.txt       # Dependências
```

---

## Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `No module named 'flask'` | venv não ativo | `source venv/bin/activate` |
| `NLTK punkt not found` | Dados não baixados | `python -c "import nltk; nltk.download('punkt')"` |
| `Address already in use` | Porta 5000 ocupada | `lsof -i :5000` e `kill <PID>` |
| `Permission denied` logs | Sem permissão | `mkdir -p logs && chmod 755 logs` |

---

## Próximos Passos

- [RUNBOOK.md](RUNBOOK.md) — Operação (start, stop, logs)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Mais problemas
