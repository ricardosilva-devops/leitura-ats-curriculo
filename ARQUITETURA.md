# 🏗️ Arquitetura - Leitura ATS

Documentação da infraestrutura AWS provisionada via Terraform.

---

## Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS CLOUD                            │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    VPC (10.0.0.0/16)                   │ │
│  │                                                        │ │
│  │  ┌─────────────────┐         ┌─────────────────┐      │ │
│  │  │  Public Subnet  │         │  Public Subnet  │      │ │
│  │  │   AZ-1a         │         │   AZ-1b         │      │ │
│  │  │  [NAT Gateway]  │         │  [NAT Gateway]  │      │ │
│  │  └────────┬────────┘         └────────┬────────┘      │ │
│  │           │                           │                │ │
│  │           └─────────┬─────────────────┘                │ │
│  │                     │                                  │ │
│  │             [Load Balancer]                            │ │
│  │                     │                                  │ │
│  │  ┌──────────────────┴──────────────────┐              │ │
│  │  │          EKS Cluster                 │              │ │
│  │  │                                      │              │ │
│  │  │  ┌────────────┐    ┌────────────┐   │              │ │
│  │  │  │  Worker 1  │    │  Worker 2  │   │              │ │
│  │  │  │  [Pod]     │    │  [Pod]     │   │              │ │
│  │  │  │  Flask+    │    │  Flask+    │   │              │ │
│  │  │  │  Gunicorn  │    │  Gunicorn  │   │              │ │
│  │  │  └────────────┘    └────────────┘   │              │ │
│  │  │                                      │              │ │
│  │  │  Private Subnets (10.0.11-13.0/24)  │              │ │
│  │  └──────────────────────────────────────┘              │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   ECR    │  │    S3    │  │CloudWatch│  │   IAM    │   │
│  │ Registry │  │ Storage  │  │   Logs   │  │  Roles   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Componentes

### VPC (Networking)

| Componente | Configuração | Motivo |
|------------|--------------|--------|
| CIDR | 10.0.0.0/16 | 65k IPs disponíveis |
| AZs | 3 (us-east-1a, 1b, 1c) | Alta disponibilidade |
| Public Subnets | 3 x /24 | Load Balancer, NAT |
| Private Subnets | 3 x /24 | Worker nodes (seguros) |
| NAT Gateway | 1 por AZ | Saída de internet para pods |

### EKS (Kubernetes)

| Componente | Configuração | Motivo |
|------------|--------------|--------|
| Versão | 1.28 | Estável, suporte AWS |
| Node Group | Managed | AWS gerencia updates |
| Instance Type | t3.medium | Balanço custo/performance |
| Min Nodes | 2 | Alta disponibilidade |
| Max Nodes | 4 | Auto-scaling |

### ECR (Container Registry)

- Registry privado para imagens Docker
- Lifecycle policy: mantém últimas 10 imagens
- Scan de vulnerabilidades automático

### S3 (Storage)

- Bucket para armazenar currículos analisados
- Encryption at rest (AES-256)
- Lifecycle: 90 dias → Glacier, 365 dias → Delete

### CloudWatch

- Logs da aplicação centralizados
- Métricas de CPU/Memory
- Alarme: CPU > 80% por 5 minutos

---

## Kubernetes Manifests

### Deployment

```yaml
replicas: 2                    # Alta disponibilidade
strategy: RollingUpdate        # Zero downtime
resources:
  requests: 250m CPU, 256Mi    # Garantido
  limits: 500m CPU, 512Mi      # Máximo
```

### HPA (Auto-Scaling)

```yaml
minReplicas: 2
maxReplicas: 10
targetCPU: 70%     # Escala quando CPU > 70%
```

### Service

```yaml
type: LoadBalancer   # Expõe via AWS ELB
port: 80 → 5000      # HTTP externo → Flask interno
```

---

## Segurança

| Prática | Implementação |
|---------|---------------|
| Pods em rede privada | Private subnets, sem IP público |
| IRSA | IAM Role via ServiceAccount (sem credenciais) |
| Non-root container | User 1000, não executa como root |
| Secrets | Kubernetes Secrets (não ConfigMap) |
| Security Groups | Tráfego mínimo necessário |

---

## Custos Estimados

| Recurso | Dev (~) | Prod (~) |
|---------|---------|----------|
| EKS Control Plane | $72/mês | $72/mês |
| EC2 (2x t3.medium) | $60/mês | $120/mês |
| NAT Gateway | $32/mês | $32/mês |
| S3 + ECR | $5/mês | $10/mês |
| **Total** | **~$170/mês** | **~$235/mês** |

**Dica:** Use `terraform destroy` quando não estiver usando!

---

## Deploy Rápido

```bash
# 1. Provisionar infraestrutura
cd infra/terraform
terraform init
terraform apply

# 2. Configurar kubectl
aws eks update-kubeconfig --name leitura-ats-eks-dev

# 3. Build e push da imagem
ECR_URL=$(terraform output -raw ecr_repository_url)
docker build -t leitura-ats -f ../../imagem-aplicacao/Dockerfile ../..
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URL
docker tag leitura-ats $ECR_URL:latest
docker push $ECR_URL:latest

# 4. Deploy no Kubernetes
cd ../kubernetes
kubectl apply -f .

# 5. Pegar URL
kubectl get svc leitura-ats-service
```

---

## Arquivos Terraform

| Arquivo | Conteúdo |
|---------|----------|
| `main.tf` | VPC, EKS, ECR, S3, CloudWatch |
| `variables.tf` | Variáveis configuráveis |
| `outputs.tf` | URLs e IDs importantes |
| `iam.tf` | Roles para IRSA |

---

## Arquivos Kubernetes

| Arquivo | Conteúdo |
|---------|----------|
| `deployment.yaml` | Deployment + HPA |
| `service.yaml` | LoadBalancer Service |
| `configmap.yaml` | ConfigMap + Secrets + ServiceAccount |
