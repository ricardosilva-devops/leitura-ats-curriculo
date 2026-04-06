# 📄 Leitura ATS - Analisador de Currículos

Aplicação web para análise de legibilidade de currículos em PDF, simulando como sistemas ATS (Applicant Tracking System) interpretam documentos.

> **Projeto de Portfólio** focado em infraestrutura: demonstra empacotamento, operação e automação com Python, Docker e CI, com roadmap para orquestração em cloud (Terraform, Kubernetes).

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Estado Atual (v0.1.0)

**✅ Implementado:**
- Aplicação Flask para análise de PDF
- Motor ATS com NLP (NLTK) em português
- Interface web responsiva (drag-and-drop)
- Docker com imagem otimizada
- Scripts operacionais (setup, start, stop, health-check)
- CI básico com GitHub Actions (lint, build, health check)

**📝 Código pronto, não deployado:**
- Terraform para AWS (VPC, EKS, ECR, S3)
- Kubernetes manifests (Deployment, Service, Ingress)
- Configuração de Nginx e Supervisor

---

## 🎯 O que faz?

1. **Upload de PDF** - Arraste ou selecione um currículo
2. **Análise de Legibilidade** - Score heurístico de 0-100:
   - Keywords técnicas encontradas (40%)
   - Estrutura do documento (35%)
   - Clareza do texto (25%)
3. **Extração de Dados** - Nome, experiências, habilidades, certificações
4. **Feedback** - Sugestões para melhorar a estrutura

> ⚠️ **Nota:** Esta é uma análise heurística para fins educacionais. Não é uma validação oficial de ATS do mercado.

---

## 🚀 Como Rodar

### Opção 1: Local (Recomendado)

```bash
# Clonar repositório
git clone https://github.com/ricardosilva-devops/leitura-ats-curriculo.git
cd leitura-ats-curriculo

# Setup automático
./scripts/setup.sh

# Iniciar aplicação
./scripts/start.sh

# Acessar: http://localhost:5000
```

**Ou manualmente:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# .\venv\Scripts\Activate.ps1  # Windows

pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"

cd aplicacao && python app.py
```

### Opção 2: Docker

```bash
# Build
./scripts/build-docker.sh

# Executar
./scripts/run-docker.sh

# Ou manualmente:
docker build -t leitura-ats -f imagem-aplicacao/Dockerfile .
docker run -p 5000:5000 leitura-ats
```

📖 **Manual completo:** [docs/SETUP.md](docs/SETUP.md)

---

## 📁 Estrutura do Projeto

```
leitura-ats-curriculo/
├── aplicacao/               # 🐍 Aplicação Python
│   ├── app.py               # Flask (API + rotas)
│   ├── leitura_ats/         # Motor de análise ATS
│   ├── extracao_pdf/        # Extração de texto (PyMuPDF)
│   ├── templates/           # HTML (Jinja2)
│   └── static/              # CSS + JavaScript
│
├── docs/                    # 📚 Documentação
│   ├── SETUP.md             # Instalação
│   ├── RUNBOOK.md           # Operação
│   ├── ARQUITETURA.md       # Arquitetura atual
│   ├── ROADMAP.md           # Próximos passos
│   └── ...
│
├── scripts/                 # 🔧 Scripts operacionais
│   ├── setup.sh             # Configuração inicial
│   ├── start.sh             # Iniciar aplicação
│   ├── build-docker.sh      # Build da imagem
│   └── ...
│
├── imagem-aplicacao/        # 🐳 Docker
│   └── Dockerfile           # Multi-stage build
│
├── infra/                   # ☁️ Infraestrutura (roadmap)
│   ├── terraform/           # AWS (VPC, EKS, ECR, S3)
│   └── kubernetes/          # Manifests K8s
│
└── exemplos/                # 📋 Exemplos de uso
```

---

## 🛠️ Tecnologias

### Stack Atual (v0.1.0)

| Camada | Tecnologia | Função |
|--------|------------|--------|
| **Backend** | Python 3.12 | Linguagem principal |
| | Flask 3.0 | Framework web |
| | Gunicorn | Servidor WSGI |
| | PyMuPDF | Extração de PDF |
| | NLTK | NLP em português |
| **Frontend** | HTML5/CSS3 | Interface |
| | JavaScript | Interatividade |
| **Container** | Docker | Empacotamento |

### Roadmap de Infraestrutura

| Tecnologia | Status | Descrição |
|------------|--------|-----------|
| Docker | ✅ Implementado | Build e execução funcionais |
| GitHub Actions | ✅ Implementado | CI: lint, build, health check |
| Docker Compose | 📋 Planejado | Orquestração local multi-container |
| Nginx + Supervisor | 📝 Código pronto | Reverse proxy e gestão de processos |
| Terraform | 📝 Código pronto | IaC para AWS (não validado em deploy) |
| Kubernetes | 📝 Código pronto | Manifests para EKS (não validado em deploy) |

Ver [docs/ROADMAP.md](docs/ROADMAP.md) para detalhes.

---

## 📊 API

### POST /analyze

Analisa um currículo PDF.

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@curriculo.pdf"
```

**Resposta:**
```json
{
  "success": true,
  "extraction": {
    "page_count": 2,
    "word_count": 450
  },
  "analysis": {
    "final_score": 78,
    "keyword_score": 82,
    "structure_score": 75,
    "readability_score": 76,
    "match_level": "BOM",
    "keywords_found": [
      {"keyword": "linux", "found_as": "Linux", "match_type": "exact", "importance": "high"},
      {"keyword": "aws", "found_as": "AWS", "match_type": "exact", "importance": "high"}
    ],
    "sections_detected": [
      {"name": "experiência", "detected": true},
      {"name": "formação", "detected": true}
    ],
    "extracted_data": {
      "name": "Nome do Candidato",
      "experiences": [...],
      "skills": [...]
    }
  }
}
```

### GET /health

Health check para monitoramento.

```bash
curl http://localhost:5000/health
# {"status": "healthy", "service": "leitura-ats-curriculo"}
```

Ver exemplo completo: [exemplos/resposta_exemplo.json](exemplos/resposta_exemplo.json)

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [docs/SETUP.md](docs/SETUP.md) | Instalação completa |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Manual operacional |
| [docs/ARQUITETURA.md](docs/ARQUITETURA.md) | Arquitetura atual |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Resolução de problemas |
| [docs/DECISOES_TECNICAS.md](docs/DECISOES_TECNICAS.md) | Justificativas técnicas |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Próximas evoluções |
| [docs/LIMITACOES.md](docs/LIMITACOES.md) | Limitações conhecidas |
| [docs/SEGURANCA.md](docs/SEGURANCA.md) | Política de privacidade |

---

## ⚠️ Limitações

- **Sem OCR:** PDF deve ter texto selecionável (não funciona com escaneados)
- **Apenas PDF:** Não aceita .docx, .doc ou outros formatos
- **Análise heurística:** Não é validação oficial de ATS
- **Português apenas:** Otimizado para currículos em português

Ver [docs/LIMITACOES.md](docs/LIMITACOES.md) para lista completa.

---

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👤 Autor

**Ricardo da Silva Júnior**

- GitHub: [@ricardosilva-devops](https://github.com/ricardosilva-devops)
- LinkedIn: [Ricardo da Silva Júnior](https://linkedin.com/in/ricardosilva-devops)

---

*Projeto de portfólio demonstrando habilidades em Python, Docker e infraestrutura.*
