# 📋 Manual Operacional (Runbook)

Guia para operar a aplicação Leitura ATS no dia a dia.

---

## Índice

1. [Iniciar/Parar Aplicação](#1-iniciarparar-aplicação)
2. [Operação com Docker](#2-operação-com-docker)
3. [Verificação de Logs](#3-verificação-de-logs)
4. [Testes de Funcionamento](#4-testes-de-funcionamento)
5. [Manutenção](#5-manutenção)

---

## 1. Iniciar/Parar Aplicação

### Iniciar (Modo Desenvolvimento)

```bash
cd aplicacao
source ../venv/bin/activate  # Linux/macOS
# ou: ..\venv\Scripts\Activate.ps1  # Windows

python app.py
```

### Iniciar (Modo Produção com Gunicorn)

```bash
cd aplicacao
gunicorn --config gunicorn_config.py wsgi:app
```

### Iniciar em Background

**Linux/macOS:**
```bash
cd aplicacao
nohup gunicorn --config gunicorn_config.py wsgi:app > ../logs/app.log 2>&1 &
echo $! > ../app.pid
echo "Aplicação iniciada. PID: $(cat ../app.pid)"
```

**Windows (PowerShell):**
```powershell
Start-Process -NoNewWindow -FilePath "gunicorn" -ArgumentList "--config gunicorn_config.py wsgi:app"
```

### Parar Aplicação

**Se rodando em foreground:** `Ctrl+C`

**Se rodando em background:**
```bash
# Linux/macOS
kill $(cat app.pid)

# Windows
Get-Process -Name python | Stop-Process
```

### Usar Scripts de Controle

```bash
# Iniciar
./scripts/start.sh

# Parar
./scripts/stop.sh

# Health check
./scripts/health-check.sh
```

---

## 2. Operação com Docker

### Build da Imagem

```bash
docker build -t leitura-ats:latest -f imagem-aplicacao/Dockerfile .
```

### Executar Container

```bash
# Foreground (ver logs)
docker run -p 5000:5000 leitura-ats:latest

# Background (detached)
docker run -d -p 5000:5000 --name leitura-ats leitura-ats:latest
```

### Verificar Container

```bash
# Status
docker ps -a | grep leitura-ats

# Logs
docker logs leitura-ats

# Logs em tempo real
docker logs -f leitura-ats
```

### Parar/Remover Container

```bash
# Parar
docker stop leitura-ats

# Remover
docker rm leitura-ats

# Parar e remover
docker rm -f leitura-ats
```

### Entrar no Container (debug)

```bash
docker exec -it leitura-ats /bin/bash
```

---

## 3. Verificação de Logs

### Localização dos Logs

| Ambiente | Caminho |
|----------|---------|
| Local | `aplicacao/logs/` |
| Docker | `/app/logs/` (dentro do container) |

### Visualizar Logs

```bash
# Últimas 50 linhas
tail -50 aplicacao/logs/analise_*.txt

# Acompanhar em tempo real
tail -f aplicacao/logs/analise_*.txt

# Buscar erros
grep -i "error\|exception" aplicacao/logs/*.txt
```

### Estrutura do Log de Análise

Cada análise gera um arquivo `analise_YYYYMMDD_HHMMSS.txt` contendo:
- Timestamp
- Nome do arquivo enviado
- Texto extraído do PDF
- Keywords encontradas
- Score final
- Dados estruturados extraídos

### Logs do Gunicorn

```bash
# Se configurado para arquivo
tail -f logs/gunicorn.log

# Se usando stdout
# Os logs aparecem no terminal onde o gunicorn foi iniciado
```

---

## 4. Testes de Funcionamento

### Health Check

```bash
curl -s http://localhost:5000/health | jq .
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "service": "leitura-ats-curriculo"
}
```

### Teste de Upload via cURL

Faça upload de um currículo em PDF:

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@seu-curriculo.pdf" \
  | jq .
```
```

### Teste Rápido com Script

```bash
./scripts/health-check.sh
```

### Verificar API Disponível

```bash
# Deve retornar página HTML
curl -s http://localhost:5000 | head -20
```

---

## 5. Manutenção

### Limpar Logs Antigos

```bash
# Remover logs com mais de 7 dias
find aplicacao/logs -name "*.txt" -mtime +7 -delete

# Ou usar script
./scripts/cleanup.sh
```

### Limpar Cache Python

```bash
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

### Atualizar Dependências

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Verificar Uso de Disco

```bash
du -sh aplicacao/logs/
du -sh venv/
```

### Reiniciar Após Mudança de Código

```bash
# Se usando Flask development server
# O reload é automático (debug=True)

# Se usando Gunicorn
kill -HUP $(cat app.pid)  # Graceful reload
```

---

## Troubleshooting Rápido

| Problema | Verificar | Solução |
|----------|-----------|---------|
| App não inicia | `python -c "from app import app"` | Ver erros de import |
| Porta ocupada | `lsof -i :5000` | Matar processo ou mudar porta |
| Health falha | `curl localhost:5000/health` | Verificar logs da aplicação |
| Upload falha | Logs de erro | Verificar tamanho do arquivo |
| Container não sobe | `docker logs leitura-ats` | Verificar erro no log |

Para problemas mais detalhados, consulte [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## Comandos Úteis Resumidos

```bash
# Status rápido
curl -s localhost:5000/health && echo " ✅ OK" || echo " ❌ FALHOU"

# Ver processos Python
ps aux | grep python

# Ver containers Docker
docker ps -a

# Uso de memória do processo
ps -o pid,rss,command -p $(pgrep -f "gunicorn")
```
