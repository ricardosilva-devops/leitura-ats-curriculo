# 🔍 Troubleshooting

> **Ambiente:** Linux/WSL. Comandos assumem bash.

---

## Instalação

### Python não encontrado

```bash
# Instalar Python 3.10+
sudo apt update && sudo apt install python3 python3-venv python3-pip
```

### Erro ao criar venv

```bash
# Instalar venv separadamente
sudo apt install python3-venv
python3 -m venv venv
```

### Erro de permissão no pip

```bash
# Verificar se venv está ativo (prompt mostra "(venv)")
source venv/bin/activate
pip install -r requirements.txt  # Nunca use sudo
```

---

## NLTK

### Dados não encontrados

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"
```

### Download falha

```bash
# Verificar conexão
ping google.com

# Download manual: baixar de https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/index.xml
# Extrair em ~/nltk_data/
```

---

## Aplicação

### Porta 5000 em uso

```bash
lsof -i :5000
kill -9 <PID>
# ou usar outra porta:
FLASK_RUN_PORT=5001 python app.py
```

### Import error

```bash
# Verificar venv ativo
which python  # Deve mostrar caminho do venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executar de pasta errada

```bash
# Sempre executar de dentro de aplicacao/
cd aplicacao && python app.py
```

---

## PDF

### Texto não extraído

**Causas:**
- PDF é imagem escaneada (sem OCR)
- PDF protegido/criptografado
- PDF corrompido

**Verificação:** Tentar selecionar texto no PDF com um leitor.

### Arquivo maior que 16MB

Comprimir o PDF ou ajustar limite em `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

---

## Docker

### Build falha

```bash
docker builder prune
docker build --no-cache -t leitura-ats -f imagem-aplicacao/Dockerfile .
```

### Container não responde

```bash
docker logs leitura-ats
docker exec leitura-ats ps aux
```

---

## Checklist de Verificação

```bash
python3 --version                                    # Python OK?
which python                                         # venv ativo?
pip list | grep -E "Flask|pymupdf|nltk"             # Deps instaladas?
python -c "import nltk; nltk.data.find('tokenizers/punkt')"  # NLTK data?
cd aplicacao && python -c "from app import app"     # App importa?
lsof -i :5000 || echo "Porta livre"                 # Porta livre?
curl -s localhost:5000/health                       # Health OK?
```
