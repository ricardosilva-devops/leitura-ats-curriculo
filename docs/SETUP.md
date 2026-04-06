# 🔧 Manual de Instalação Local

Guia completo para configurar o ambiente de desenvolvimento.

---

## Pré-requisitos

| Requisito | Versão Mínima | Verificar |
|-----------|---------------|-----------|
| Python | 3.10+ (recomendado 3.12) | `python --version` |
| pip | 21.0+ | `pip --version` |
| Git | 2.0+ | `git --version` |

**Opcional (para Docker):**
| Requisito | Versão Mínima | Verificar |
|-----------|---------------|-----------|
| Docker | 20.0+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |

---

## Instalação Passo a Passo

### 1. Clonar o Repositório

```bash
git clone https://github.com/ricardosilva-devops/leitura-ats-curriculo.git
cd leitura-ats-curriculo
```

### 2. Criar Ambiente Virtual

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

> 💡 O prompt deve mudar para `(venv)` indicando que o ambiente está ativo.

### 3. Instalar Dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Dependências instaladas:**
- Flask 3.0 (framework web)
- PyMuPDF 1.24 (extração de PDF)
- NLTK 3.8 (processamento de linguagem natural)
- Gunicorn 21.0 (servidor WSGI)

### 4. Baixar Dados do NLTK

O NLTK precisa de dados para processamento de português:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"
```

**O que cada dado faz:**
- `punkt` - Tokenização de sentenças
- `punkt_tab` - Dados tabulares para tokenização
- `rslp` - Stemmer para português (Removedor de Sufixos da Língua Portuguesa)

### 5. Verificar Instalação

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

Você deve ver a página de upload de currículos.

### 3. Testar Análise

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@exemplos/curriculo_exemplo.pdf"
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

## Erros Comuns no Setup

### "No module named 'flask'"

**Causa:** Ambiente virtual não está ativo ou dependências não instaladas.

**Solução:**
```bash
source venv/bin/activate  # ou .\venv\Scripts\Activate.ps1 no Windows
pip install -r requirements.txt
```

### "NLTK punkt not found"

**Causa:** Dados do NLTK não foram baixados.

**Solução:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"
```

### "Address already in use" (porta 5000)

**Causa:** Outro processo usando a porta 5000.

**Solução Linux/macOS:**
```bash
lsof -i :5000
kill -9 <PID>
```

**Solução Windows:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "Permission denied" ao criar logs

**Causa:** Falta permissão na pasta de logs.

**Solução:**
```bash
mkdir -p aplicacao/logs
chmod 755 aplicacao/logs
```

---

## Próximos Passos

- [RUNBOOK.md](RUNBOOK.md) - Como operar a aplicação
- [README.md](../README.md) - Voltar para visão geral
