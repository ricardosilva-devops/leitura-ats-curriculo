# 📄 Leitura ATS - Analisador de Currículos

Aplicação web para análise de currículos em PDF, simulando a leitura de sistemas ATS (Applicant Tracking System).

**Projeto de Portfólio** demonstrando: Python/Flask, Docker, Terraform e Kubernetes.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![Terraform](https://img.shields.io/badge/Terraform-AWS-purple?logo=terraform)
![Kubernetes](https://img.shields.io/badge/Kubernetes-EKS-blue?logo=kubernetes)

---

## 🎯 O que faz?

1. **Upload de PDF** - Arraste ou selecione um currículo
2. **Análise ATS** - Score de 0-100 baseado em:
   - Keywords técnicas encontradas (40%)
   - Estrutura do documento (35%)
   - Legibilidade (25%)
3. **Extração de Dados** - Nome, experiências, habilidades, certificações
4. **Feedback** - Sugestões para melhorar o currículo

---

## 🚀 Como Rodar

### Opção 1: Local (Desenvolvimento)

```bash
# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Baixar dados NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('rslp')"

# Rodar
cd aplicacao
python app.py

# Acessar: http://localhost:5000
```

### Opção 2: Docker

```bash
# Build da imagem
docker build -t leitura-ats -f imagem-aplicacao/Dockerfile .

# Rodar container
docker run -p 5000:5000 leitura-ats

# Acessar: http://localhost:5000
```

### Opção 3: AWS (Kubernetes)

Ver [DEPLOY.md](DEPLOY.md) para instruções completas de deploy na AWS.

```bash
# Resumo:
cd infra/terraform && terraform apply  # Cria VPC, EKS, ECR, S3
kubectl apply -f infra/kubernetes/     # Deploy da aplicação
```

---

## 📁 Estrutura

```
leitura-ats-curriculo/
├── aplicacao/               # 🐍 Código Python
│   ├── app.py               # Flask (API)
│   ├── leitura_ats/         # Motor ATS (NLP)
│   ├── extracao_pdf/        # Extração de PDF
│   ├── templates/           # HTML
│   └── static/              # CSS + JS
│
├── imagem-aplicacao/        # 🐳 Docker
│   └── Dockerfile
│
├── infra/                   # ☁️ Infraestrutura
│   ├── terraform/           # AWS (VPC, EKS, ECR, S3)
│   └── kubernetes/          # Manifests K8s
│
├── requirements.txt
└── README.md
```

---

## 🏗️ Infraestrutura AWS

O projeto inclui infraestrutura completa como código:

| Recurso | Descrição |
|---------|-----------|
| **VPC** | Rede isolada com 3 AZs, subnets públicas/privadas |
| **EKS** | Kubernetes gerenciado com auto-scaling |
| **ECR** | Registry privado para imagens Docker |
| **S3** | Armazenamento de currículos |
| **CloudWatch** | Logs e métricas |

**Custo estimado:** ~$170/mês (ambiente dev)

Ver [ARQUITETURA.md](ARQUITETURA.md) para detalhes.

---

## 🛠️ Tecnologias

**Backend:**
- Python 3.12
- Flask 3.0
- Gunicorn (WSGI)
- NLTK (NLP em Português)
- PyMuPDF (extração de PDF)

**Infraestrutura:**
- Docker (multi-stage build)
- Terraform (IaC)
- Kubernetes (EKS)
- AWS (VPC, ECR, S3, CloudWatch)

**Frontend:**
- HTML5 / CSS3
- JavaScript (vanilla)

---

## 📊 API

### POST /analyze

Analisa um currículo PDF.

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@curriculo.pdf"
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "final_score": 72,
    "keyword_score": 68,
    "structure_score": 78,
    "readability_score": 70,
    "keywords_found": ["python", "aws", "docker", "linux"],
    "sections_detected": ["experiência", "formação", "habilidades"]
  },
  "extracted_data": {
    "name": "Nome do Candidato",
    "experiences": [...],
    "skills": [...]
  }
}
```

### GET /health

Health check.

```bash
curl http://localhost:5000/health
# {"status": "healthy"}
```

---

## 📝 Licença

MIT License

---

**Desenvolvido por Ricardo da Silva Júnior**
