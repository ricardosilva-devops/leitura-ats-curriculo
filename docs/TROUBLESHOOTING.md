# 🔍 Troubleshooting

Guia de resolução de problemas comuns.

---

## Problemas de Instalação

### Python não encontrado

**Sintoma:**
```
'python' is not recognized as an internal or external command
```

**Solução:**
1. Verificar se Python está instalado: baixar de https://python.org
2. Windows: marcar "Add Python to PATH" durante instalação
3. Reiniciar terminal após instalar

### Erro ao criar ambiente virtual

**Sintoma:**
```
Error: Command '['python', '-m', 'venv', 'venv']' returned non-zero exit status
```

**Solução:**
```bash
# Linux - instalar venv separadamente
sudo apt install python3-venv

# Tentar novamente
python3 -m venv venv
```

### Erro de permissão no pip install

**Sintoma:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solução:**
```bash
# Verificar se ambiente virtual está ativo
# O prompt deve mostrar (venv)
source venv/bin/activate

# Nunca use sudo com pip em venv
pip install -r requirements.txt
```

---

## Problemas do NLTK

### Dados do NLTK não encontrados

**Sintoma:**
```
LookupError: Resource punkt not found
```

**Solução:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"
```

### Download do NLTK falha

**Sintoma:**
```
[nltk_data] Error loading punkt: <urlopen error [Errno -2] Name or
[nltk_data]     service not known>
```

**Solução:**
```bash
# Verificar conexão com internet
ping google.com

# Download manual (alternativa)
# Baixar de: https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/index.xml
# Extrair em ~/nltk_data/
```

---

## Problemas da Aplicação

### Porta 5000 em uso

**Sintoma:**
```
OSError: [Errno 98] Address already in use
```

**Solução Linux/macOS:**
```bash
# Encontrar processo
lsof -i :5000

# Matar processo
kill -9 <PID>
```

**Solução Windows:**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Alternativa - usar outra porta:**
```bash
# Flask
FLASK_RUN_PORT=5001 python app.py

# Gunicorn
gunicorn -b 0.0.0.0:5001 wsgi:app
```

### Import error ao iniciar

**Sintoma:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solução:**
```bash
# Verificar ambiente virtual ativo
which python  # Deve mostrar caminho do venv

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro ao executar fora da pasta correta

**Sintoma:**
```
FileNotFoundError: templates/index.html
```

**Solução:**
```bash
# Sempre executar de dentro da pasta aplicacao/
cd aplicacao
python app.py
```

---

## Problemas de PDF

### PDF sem texto extraível

**Sintoma:**
```json
{
  "success": true,
  "extracted_text": "",
  "analysis": { "final_score": 0 }
}
```

**Causas possíveis:**
1. PDF é uma imagem escaneada (sem OCR)
2. PDF protegido/criptografado
3. PDF corrompido

**Verificação:**
```bash
# Tentar selecionar texto no PDF com um leitor
# Se não conseguir selecionar, o PDF não tem texto extraível
```

**Solução:**
- Usar PDF com texto selecionável (não escaneado)
- Ou implementar OCR com Tesseract (não incluído nesta versão)

### Arquivo maior que 16 MB

**Sintoma:**
```
413 Request Entity Too Large
```

**Solução:**
- Comprimir o PDF antes de enviar
- Ou ajustar limite em `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB
```

### Tipo de arquivo não suportado

**Sintoma:**
```json
{"error": "Formato não suportado. Envie um arquivo PDF."}
```

**Solução:**
- Converter documento para PDF antes de enviar
- A aplicação aceita apenas arquivos `.pdf`

---

## Problemas do Docker

### Build falha com erro de rede

**Sintoma:**
```
E: Unable to fetch some archives, maybe run apt-get update
```

**Solução:**
```bash
# Limpar cache Docker e rebuildar
docker builder prune
docker build --no-cache -t leitura-ats .
```

### Container sobe mas /health falha

**Sintoma:**
```
curl: (7) Failed to connect to localhost port 5000
```

**Verificação:**
```bash
# Ver logs do container
docker logs leitura-ats

# Verificar se processo está rodando dentro do container
docker exec leitura-ats ps aux
```

**Causas comuns:**
1. Gunicorn não encontrou `wsgi.py`
2. Erro de importação na aplicação
3. Porta mapeada errada

### Gunicorn não encontra wsgi.py

**Sintoma:**
```
ModuleNotFoundError: No module named 'wsgi'
```

**Solução:**
Verificar que o WORKDIR está correto no Dockerfile:
```dockerfile
WORKDIR /app
COPY aplicacao/ /app/
```

### Container sem permissão para criar logs

**Sintoma:**
```
PermissionError: [Errno 13] Permission denied: '/app/logs/analise.txt'
```

**Solução:**
Garantir que usuário não-root tem permissão:
```dockerfile
RUN mkdir -p /app/logs && chown -R appuser:appgroup /app
USER appuser
```

---

## Problemas de Logs

### Logs não são criados

**Verificação:**
```bash
ls -la aplicacao/logs/
```

**Solução:**
```bash
mkdir -p aplicacao/logs
chmod 755 aplicacao/logs
```

### Pasta de logs cheia

**Sintoma:**
```
OSError: [Errno 28] No space left on device
```

**Solução:**
```bash
# Remover logs antigos
find aplicacao/logs -name "*.txt" -mtime +7 -delete

# Verificar espaço em disco
df -h
```

---

## Verificação de Saúde Completa

Execute este checklist quando algo não funcionar:

```bash
# 1. Python OK?
python --version

# 2. Venv ativo?
which python

# 3. Dependências instaladas?
pip list | grep -E "Flask|pymupdf|nltk"

# 4. NLTK data OK?
python -c "import nltk; nltk.data.find('tokenizers/punkt')"

# 5. App importa sem erro?
cd aplicacao && python -c "from app import app; print('OK')"

# 6. Porta livre?
lsof -i :5000 || echo "Porta livre"

# 7. Health responde?
curl -s localhost:5000/health
```

---

## Obter Ajuda

Se o problema persistir:

1. **Verificar logs completos:**
   ```bash
   cat aplicacao/logs/*.txt
   ```

2. **Coletar informações do ambiente:**
   ```bash
   python --version
   pip freeze
   uname -a  # ou ver cmd
   ```

3. **Abrir issue no GitHub** com:
   - Descrição do problema
   - Passos para reproduzir
   - Logs de erro
   - Ambiente (OS, Python version)
