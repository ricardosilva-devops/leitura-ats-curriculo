# 📄 Leitura ATS - Analisador de Currículos

Aplicação web para análise de legibilidade de currículos em PDF, simulando como sistemas ATS (Applicant Tracking System) interpretam documentos.

> **Projeto de Portfólio** — Aplicação Python containerizada com operação documentada e CI básico.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![CI](https://img.shields.io/badge/CI-passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Estado Atual (v0.1.0)

| Status | Componente |
|--------|------------|
| ✅ Funcional | Aplicação Flask + Motor ATS (NLP/NLTK) |
| ✅ Funcional | Interface web (drag-and-drop) |
| ✅ Funcional | Docker (build + run) |
| ✅ Funcional | CI (lint, build, health check) |
| ✅ Funcional | Scripts operacionais (start, stop, health) |

> Projeto focado em demonstrar empacotamento e operação de aplicação local.

---

## 🎯 O que faz?

1. **Upload de PDF** — Arraste ou selecione um currículo
2. **Análise** — Score heurístico (0-100) baseado em keywords, estrutura e legibilidade
3. **Extração** — Nome, experiências, habilidades, certificações
4. **Feedback** — Sugestões para melhorar a estrutura

⚠️ Análise heurística para fins educacionais. Não é validação oficial de ATS.

---

## 🚀 Como Rodar

**Ambiente:** Linux ou WSL. Scripts escritos para bash.

### Via Scripts (recomendado)

```bash
git clone https://github.com/ricardosilva-devops/leitura-ats-curriculo.git
cd leitura-ats-curriculo

./scripts/setup.sh    # Cria venv, instala deps, baixa NLTK
./scripts/start.sh    # Inicia em http://localhost:5000
```

### Via Docker

```bash
./scripts/build-docker.sh
./scripts/run-docker.sh
```

📖 [docs/SETUP.md](docs/SETUP.md) — Instalação manual e troubleshooting

---

## 📁 Estrutura

```
leitura-ats-curriculo/
├── aplicacao/           # Aplicação Python (Flask + motor ATS)
├── scripts/             # setup.sh, start.sh, stop.sh, health-check.sh
├── imagem-aplicacao/    # Dockerfile
├── docs/                # Documentação técnica
├── logs/                # Logs de análise (gitignored)
└── exemplos/            # Exemplo de resposta da API
```

---

## 📊 API

### POST /analyze

```bash
curl -X POST http://localhost:5000/analyze -F "file=@curriculo.pdf"
```

Resposta resumida:
```json
{
  "success": true,
  "extraction": { "page_count": 2, "word_count": 485 },
  "analysis": {
    "final_score": 78,
    "match_level": "BOM",
    "keywords_found": [
      {"keyword": "linux", "found_as": "Linux", "importance": "high"}
    ],
    "extracted_data": {
      "name": "Nome do Candidato",
      "experiences": [...]
    }
  }
}
```

### GET /health

```bash
curl http://localhost:5000/health
# {"status": "healthy", "service": "leitura-ats-curriculo"}
```

Ver estrutura completa: [exemplos/resposta_exemplo.json](exemplos/resposta_exemplo.json)

---

## 📚 Documentação

| Doc | Descrição |
|-----|-----------|
| [SETUP.md](docs/SETUP.md) | Instalação e configuração |
| [RUNBOOK.md](docs/RUNBOOK.md) | Operação (start, stop, logs) |
| [ARQUITETURA.md](docs/ARQUITETURA.md) | Como funciona |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Problemas comuns |

---

## ⚠️ Limitações

- PDF deve ter texto selecionável (sem OCR)
- Apenas formato PDF
- Otimizado para português

---

## 📝 Licença

[MIT License](LICENSE)

---

**Ricardo da Silva Júnior** — [GitHub](https://github.com/ricardosilva-devops) · [LinkedIn](https://linkedin.com/in/ricardosilva-devops)
