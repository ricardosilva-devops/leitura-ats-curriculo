# 🎯 Decisões Técnicas

Justificativas das escolhas tecnológicas do projeto.

---

## Backend

### Por que Flask e não Django?

| Aspecto | Flask | Django |
|---------|-------|--------|
| Complexidade | Micro-framework, mínimo | Full-stack, muitos recursos |
| ORM | Não inclui | Inclui (necessário configurar) |
| Admin | Não inclui | Inclui |
| Curva de aprendizado | Baixa | Média |

**Decisão:** Flask

**Motivo:** Projeto tem apenas 3 rotas, não precisa de ORM (sem banco de dados), nem painel admin. Flask é suficiente e mais leve.

---

### Por que Gunicorn?

| Aspecto | Flask Dev Server | Gunicorn |
|---------|-----------------|----------|
| Produção | ❌ Não recomendado | ✅ Pronto para produção |
| Concorrência | Single-threaded | Multi-worker |
| Performance | Baixa | Alta |
| Configurabilidade | Mínima | Completa |

**Decisão:** Gunicorn para produção

**Motivo:** O servidor de desenvolvimento do Flask não é thread-safe nem otimizado para produção. Gunicorn permite múltiplos workers e é padrão da indústria para Python web.

---

### Por que PyMuPDF e não pdfplumber?

| Aspecto | PyMuPDF | pdfplumber |
|---------|---------|------------|
| Velocidade | Muito rápida | Moderada |
| Qualidade de extração | Excelente | Boa |
| Dependências | Mínimas | Várias |
| Tamanho | ~15MB | ~50MB |
| Tabelas | Suporte básico | Suporte avançado |

**Decisão:** PyMuPDF (fitz)

**Motivo:** Mais rápido, menor footprint, qualidade de extração suficiente para currículos (que raramente têm tabelas complexas).

---

### Por que NLTK e não spaCy?

| Aspecto | NLTK | spaCy |
|---------|------|-------|
| Tamanho | ~10MB | ~500MB+ (com modelo PT) |
| Velocidade | Moderada | Muito rápida |
| Recursos PT | Stemmer (RSLP) | NER, POS, etc. |
| Complexidade | Baixa | Média |

**Decisão:** NLTK

**Motivo:** Projeto precisa apenas de stemming para português. NLTK tem o RSLPStemmer nativo, é leve e suficiente. spaCy seria over-engineering.

---

## Frontend

### Por que HTML/CSS/JS vanilla?

| Aspecto | Vanilla | React/Vue |
|---------|---------|-----------|
| Complexidade | Mínima | Média |
| Build step | Nenhum | Necessário |
| Bundle size | ~5KB | ~50KB+ |
| Curva de aprendizado | Baixa | Média |

**Decisão:** Vanilla JavaScript

**Motivo:** Interface tem apenas 1 página com upload e exibição de resultado. Não precisa de SPA, roteamento, ou estado complexo. Framework seria over-engineering.

---

## Infraestrutura

### Por que Docker multi-stage build?

| Aspecto | Single-stage | Multi-stage |
|---------|--------------|-------------|
| Tamanho da imagem | ~800MB | ~200MB |
| Segurança | Inclui build tools | Apenas runtime |
| Build time | Rápido | Moderado |

**Decisão:** Multi-stage build

**Motivo:** Imagem final 4x menor, sem compiladores ou ferramentas de build expostas. Melhor para segurança e deploy.

---

### Por que começar local antes de AWS?

| Aspecto | Motivo |
|---------|--------|
| Custo | AWS custa ~$170/mês mesmo parado |
| Feedback | Iteração local é instantânea |
| Debug | Mais fácil debugar localmente |
| Validação | Garantir que funciona antes de gastar |

**Decisão:** Desenvolvimento local primeiro

**Motivo:** Validar toda a lógica localmente antes de incorrer custos de cloud. Terraform e K8s manifests estão prontos para quando for necessário.

---

### Por que EKS e não ECS?

| Aspecto | EKS | ECS |
|---------|-----|-----|
| Portabilidade | Alta (K8s padrão) | Baixa (AWS-specific) |
| Complexidade | Alta | Média |
| Ecossistema | Enorme | AWS-only |
| Custo | $72/mês control plane | $0 control plane |
| Mercado | Mais demandado | Menos demandado |

**Decisão:** EKS

**Motivo:** Projeto é portfólio para demonstrar skills de Kubernetes. EKS é mais relevante para o mercado e conhecimento é transferível para GKE/AKS.

---

## Análise ATS

### Por que análise heurística e não ML?

| Aspecto | Heurística | Machine Learning |
|---------|------------|------------------|
| Dados necessários | Nenhum | Milhares de exemplos |
| Interpretabilidade | Alta | Baixa |
| Manutenção | Simples | Complexa |
| Precisão | Boa (para o propósito) | Potencialmente melhor |
| Complexidade | Baixa | Alta |

**Decisão:** Análise heurística com NLP básico

**Motivo:** 
1. Não temos dataset de currículos para treinar
2. Regras são interpretáveis (podemos explicar o score)
3. Suficiente para demonstrar conceito
4. ML seria over-engineering sem benefício claro

---

### Por que scoring em 3 dimensões?

| Dimensão | Peso | Justificativa |
|----------|------|---------------|
| Keywords | 40% | ATS reais priorizam palavras-chave |
| Estrutura | 35% | Seções claras facilitam parsing |
| Legibilidade | 25% | Texto limpo é melhor processado |

**Decisão:** Score composto

**Motivo:** Simular comportamento de ATS reais que avaliam múltiplos aspectos. Um currículo pode ter boas keywords mas estrutura ruim, ou vice-versa.

---

## Logging

### Por que logs em arquivo e não banco/serviço?

| Aspecto | Arquivo | Banco/CloudWatch |
|---------|---------|------------------|
| Setup | Zero | Configuração necessária |
| Custo | Zero | Variável |
| Debug local | Fácil | Complexo |
| Produção | Não escalável | Escalável |

**Decisão:** Logs em arquivo (ambiente local)

**Motivo:** Projeto roda localmente. Logs em arquivo são simples e suficientes. Para produção, migrar para CloudWatch (já previsto no roadmap).

---

## Resumo das Decisões

| Escolha | Alternativa Descartada | Motivo Principal |
|---------|------------------------|------------------|
| Flask | Django | Simplicidade |
| Gunicorn | uWSGI | Popularidade, docs |
| PyMuPDF | pdfplumber | Performance |
| NLTK | spaCy | Tamanho, suficiente |
| Vanilla JS | React | Complexidade desnecessária |
| Docker multi-stage | Single-stage | Tamanho da imagem |
| EKS | ECS | Portabilidade, mercado |
| Heurística | ML | Interpretabilidade, dados |
| Logs arquivo | CloudWatch | Custo, simplicidade local |

---

## Trade-offs Conhecidos

| Decisão | Benefício | Custo |
|---------|-----------|-------|
| Sem OCR | Imagem menor, mais rápido | Não processa PDFs escaneados |
| Sem banco | Menos complexidade | Não persiste análises |
| Sem auth | Setup zero | Não tem controle de acesso |
| Sem cache | Menos código | Reprocessa PDFs iguais |

Essas limitações são aceitáveis para um projeto de demonstração e podem ser endereçadas em versões futuras (ver [ROADMAP.md](ROADMAP.md)).
