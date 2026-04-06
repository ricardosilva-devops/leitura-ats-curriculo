# 🚀 Roadmap - Próximas Evoluções

Este documento descreve a evolução planejada do projeto, desde o ambiente local até produção na AWS.

---

## Estado Atual (v0.1.0)

✅ **Implementado:**
- Aplicação Flask funcional
- Análise de PDF com NLP
- Frontend responsivo
- Docker (imagem otimizada)
- Código de infraestrutura Terraform (pronto para uso)
- Manifests Kubernetes (prontos para uso)

---

## Fase 1: Ambiente Local Completo

**Objetivo:** Stack de produção local para testes.

### 1.1 Docker Compose
- [ ] Criar `docker-compose.yml`
- [ ] Orquestrar múltiplos containers localmente
- [ ] Volume para persistência de logs

### 1.2 Nginx (Reverse Proxy)
- [ ] Adicionar Nginx como proxy reverso
- [ ] Configurar upstream para Gunicorn
- [ ] Servir arquivos estáticos diretamente
- [ ] Configurar HTTPS local (self-signed)

### 1.3 Supervisor
- [ ] Gerenciar processos Nginx + Gunicorn
- [ ] Auto-restart em caso de falha
- [ ] Logs centralizados

**Arquitetura Local Completa:**
```
Navegador → Nginx (80/443) → Gunicorn (5000) → Flask
                                    ↓
                               Supervisor (gerencia ambos)
```

---

## Fase 2: Qualidade e CI/CD

**Objetivo:** Pipeline automatizado de qualidade.

### 2.1 Testes
- [ ] Testes unitários (pytest)
- [ ] Testes de integração
- [ ] Cobertura mínima 70%

### 2.2 Linting
- [ ] Flake8 para estilo Python
- [ ] Black para formatação
- [ ] isort para imports

### 2.3 GitHub Actions
- [ ] Workflow de lint em PR
- [ ] Build de imagem Docker
- [ ] Teste de health check
- [ ] Push para ECR (quando aprovado)

**Pipeline:**
```
PR → Lint → Test → Build → Push ECR → (manual) Deploy
```

---

## Fase 3: Kubernetes Local

**Objetivo:** Validar manifests localmente antes da AWS.

### 3.1 Minikube/Kind
- [ ] Cluster Kubernetes local
- [ ] Deploy da aplicação
- [ ] Testar HPA (auto-scaling)
- [ ] Testar probes (liveness/readiness)

### 3.2 Helm Chart (Opcional)
- [ ] Empacotar deployment como Chart
- [ ] Values para dev/staging/prod
- [ ] Facilitar upgrades

---

## Fase 4: AWS - Infraestrutura

**Objetivo:** Provisionar ambiente cloud.

### 4.1 Terraform Apply
Os arquivos já existem em `infra/terraform/`. Executar:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

**Recursos criados:**
| Recurso | Descrição | Custo Estimado |
|---------|-----------|----------------|
| VPC | Rede isolada, 3 AZs | $0 |
| EKS | Kubernetes gerenciado | $72/mês |
| EC2 (workers) | 2x t3.medium | $60/mês |
| NAT Gateway | Saída internet | $32/mês |
| ECR | Registry Docker | ~$5/mês |
| S3 | Storage de currículos | ~$5/mês |
| CloudWatch | Logs e métricas | ~$5/mês |
| **Total** | | **~$180/mês** |

### 4.2 Segurança AWS
- [ ] IRSA (IAM Roles for Service Accounts)
- [ ] Private subnets para pods
- [ ] Security Groups restritivos
- [ ] Secrets no AWS Secrets Manager

---

## Fase 5: AWS - Deploy

**Objetivo:** Aplicação rodando em produção.

### 5.1 Push da Imagem
```bash
# Obter URL do ECR
ECR_URL=$(terraform output -raw ecr_repository_url)

# Login no ECR
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL

# Build e push
docker build -t $ECR_URL:v0.1.0 .
docker push $ECR_URL:v0.1.0
```

### 5.2 Deploy no EKS
```bash
# Configurar kubectl
aws eks update-kubeconfig --name leitura-ats-eks-dev

# Deploy
kubectl apply -f infra/kubernetes/
```

### 5.3 Validação
```bash
# Verificar pods
kubectl get pods

# Verificar service (pegar URL do LoadBalancer)
kubectl get svc

# Health check
curl http://<LOAD_BALANCER_URL>/health
```

---

## Fase 6: Observabilidade

**Objetivo:** Visibilidade total da aplicação em produção.

### 6.1 Logs
- [ ] Logs estruturados (JSON)
- [ ] Centralizados no CloudWatch
- [ ] Filtros e alertas

### 6.2 Métricas
- [ ] Métricas de aplicação (latência, erros)
- [ ] Métricas de infra (CPU, memória)
- [ ] Dashboard CloudWatch ou Grafana

### 6.3 Alertas
- [ ] CPU > 80% por 5 minutos
- [ ] Error rate > 5%
- [ ] Pods unhealthy

### 6.4 Tracing (Futuro)
- [ ] AWS X-Ray ou Jaeger
- [ ] Trace de requests end-to-end

---

## Fase 7: Melhorias Futuras

**Ideias para evolução contínua:**

### Funcionalidades
- [ ] OCR para PDFs escaneados (Tesseract)
- [ ] Múltiplos idiomas (inglês, espanhol)
- [ ] Comparação de currículo vs vaga
- [ ] Sugestões de melhoria automáticas
- [ ] Export de análise em PDF

### Infraestrutura
- [ ] Multi-região (DR)
- [ ] CDN para assets estáticos
- [ ] Banco de dados para persistência
- [ ] Cache (Redis) para análises frequentes
- [ ] Rate limiting

### DevOps
- [ ] GitOps (ArgoCD/Flux)
- [ ] Terraform Cloud
- [ ] Feature flags
- [ ] Canary deployments

---

## Diagrama de Arquitetura AWS (Futuro)

```
                    Internet
                        │
                        ▼
               ┌────────────────┐
               │  Route 53      │  DNS
               └───────┬────────┘
                       │
                       ▼
               ┌────────────────┐
               │  CloudFront    │  CDN (futuro)
               └───────┬────────┘
                       │
         ┌─────────────┴─────────────┐
         │           VPC             │
         │  ┌─────────────────────┐  │
         │  │   Public Subnets    │  │
         │  │  ┌───────────────┐  │  │
         │  │  │  ALB/NLB      │  │  │
         │  │  └───────┬───────┘  │  │
         │  └──────────┼──────────┘  │
         │             │             │
         │  ┌──────────┼──────────┐  │
         │  │  Private Subnets    │  │
         │  │  ┌───────┴───────┐  │  │
         │  │  │   EKS Pods    │  │  │
         │  │  │  Flask+Gunicorn│  │  │
         │  │  └───────────────┘  │  │
         │  └─────────────────────┘  │
         │                           │
         │  ┌─────┐ ┌─────┐ ┌─────┐  │
         │  │ ECR │ │ S3  │ │ CW  │  │
         │  └─────┘ └─────┘ └─────┘  │
         └───────────────────────────┘
```

---

## Priorização

| Fase | Prioridade | Esforço | Impacto |
|------|------------|---------|---------|
| 1. Local Completo | Alta | Médio | Alto |
| 2. CI/CD | Alta | Médio | Alto |
| 3. K8s Local | Média | Baixo | Médio |
| 4. AWS Infra | Média | Alto | Alto |
| 5. AWS Deploy | Média | Médio | Alto |
| 6. Observabilidade | Baixa | Médio | Médio |
| 7. Melhorias | Baixa | Alto | Variável |

---

## Notas

- Custos AWS são estimativas e podem variar
- Sempre use `terraform destroy` quando não estiver usando o ambiente
- Comece validando localmente antes de ir para cloud
- Documente tudo que implementar
