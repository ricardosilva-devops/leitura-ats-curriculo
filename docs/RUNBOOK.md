# 📋 Manual Operacional (Runbook)

> **Ambiente:** Linux/WSL. Comandos assumem bash.

---

## 1. Iniciar/Parar

### Via Scripts (recomendado)

```bash
./scripts/start.sh       # Modo dev (Flask)
./scripts/start.sh prod  # Modo prod (Gunicorn)
./scripts/start.sh bg    # Background (Gunicorn + PID)
./scripts/stop.sh        # Para a aplicação
./scripts/health-check.sh
```

### Manual

```bash
# Ativar venv
source venv/bin/activate

# Desenvolvimento
cd aplicacao && python app.py

# Produção
cd aplicacao && gunicorn --config gunicorn_config.py wsgi:app

# Background
cd aplicacao
nohup gunicorn --config gunicorn_config.py wsgi:app > ../logs/gunicorn.log 2>&1 &
echo $! > ../app.pid
```

### Parar

```bash
# Se em foreground: Ctrl+C

# Se em background:
kill $(cat app.pid)
# ou
./scripts/stop.sh
```

---

## 2. Docker

```bash
# Build
./scripts/build-docker.sh
# ou: docker build -t leitura-ats -f imagem-aplicacao/Dockerfile .

# Executar (foreground)
./scripts/run-docker.sh
# ou: docker run -p 5000:5000 leitura-ats

# Executar (background)
docker run -d -p 5000:5000 --name leitura-ats leitura-ats

# Verificar
docker ps | grep leitura-ats
docker logs leitura-ats

# Parar
docker stop leitura-ats && docker rm leitura-ats
```

---

## 3. Logs

### Localização

| Tipo | Caminho |
|------|---------|
| Logs de análise | `logs/analise_YYYYMMDD_HHMMSS.txt` |
| Gunicorn (background) | `logs/gunicorn.log` |
| Docker | `docker logs leitura-ats` |

### Comandos úteis

```bash
# Ver últimos logs de análise
tail -50 logs/analise_*.txt

# Acompanhar em tempo real
tail -f logs/gunicorn.log

# Buscar erros
grep -i "error\|exception" logs/*.txt

# Limpar logs antigos (>7 dias)
find logs -name "*.txt" -mtime +7 -delete
# ou: ./scripts/cleanup.sh
```

---

## 4. Verificação de Saúde

```bash
# Via script
./scripts/health-check.sh

# Manual
curl -s http://localhost:5000/health
# {"status": "healthy", "service": "leitura-ats-curriculo"}

# Testar upload
curl -X POST http://localhost:5000/analyze -F "file=@curriculo.pdf" | jq .
```

---

## 5. Manutenção

```bash
# Atualizar dependências
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Verificar espaço em disco
du -sh logs/ venv/

# Graceful reload (Gunicorn)
kill -HUP $(cat app.pid)
```

---

## Troubleshooting Rápido

| Problema | Verificar | Solução |
|----------|-----------|---------|
| App não inicia | `python -c "from app import app"` | Ver erros de import |
| Porta ocupada | `lsof -i :5000` | `kill <PID>` |
| Health falha | `curl localhost:5000/health` | Ver logs |
| Container não sobe | `docker logs leitura-ats` | Ver erro no log |

Mais detalhes: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
