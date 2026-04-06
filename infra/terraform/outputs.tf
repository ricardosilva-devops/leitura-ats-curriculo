# =============================================================================
# TERRAFORM OUTPUTS
# =============================================================================
#
# Valores de saída após o deploy da infraestrutura.
# Usados para configurar kubectl, CI/CD e outras integrações.
#
# =============================================================================

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------

output "vpc_id" {
  description = "ID da VPC criada"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "CIDR block da VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnets" {
  description = "IDs das subnets públicas"
  value       = module.vpc.public_subnets
}

output "private_subnets" {
  description = "IDs das subnets privadas"
  value       = module.vpc.private_subnets
}

# -----------------------------------------------------------------------------
# EKS
# -----------------------------------------------------------------------------

output "eks_cluster_name" {
  description = "Nome do cluster EKS"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "Endpoint da API do Kubernetes"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_version" {
  description = "Versão do Kubernetes"
  value       = module.eks.cluster_version
}

output "eks_cluster_certificate_authority_data" {
  description = "CA certificate do cluster (base64)"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_oidc_provider_arn" {
  description = "ARN do OIDC provider para IRSA"
  value       = module.eks.oidc_provider_arn
}

# Comando para configurar kubectl
output "configure_kubectl" {
  description = "Comando para configurar kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

# -----------------------------------------------------------------------------
# ECR
# -----------------------------------------------------------------------------

output "ecr_repository_url" {
  description = "URL do repositório ECR"
  value       = aws_ecr_repository.app.repository_url
}

output "ecr_repository_name" {
  description = "Nome do repositório ECR"
  value       = aws_ecr_repository.app.name
}

# Comando para login no ECR
output "ecr_login_command" {
  description = "Comando para login no ECR"
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}"
}

# -----------------------------------------------------------------------------
# S3
# -----------------------------------------------------------------------------

output "s3_bucket_curriculos" {
  description = "Nome do bucket S3 para currículos"
  value       = aws_s3_bucket.curriculos.bucket
}

output "s3_bucket_arn" {
  description = "ARN do bucket S3"
  value       = aws_s3_bucket.curriculos.arn
}

# -----------------------------------------------------------------------------
# CLOUDWATCH
# -----------------------------------------------------------------------------

output "cloudwatch_log_group" {
  description = "Nome do log group no CloudWatch"
  value       = aws_cloudwatch_log_group.app.name
}

# -----------------------------------------------------------------------------
# SEGURANÇA
# -----------------------------------------------------------------------------

output "app_security_group_id" {
  description = "ID do security group da aplicação"
  value       = aws_security_group.app.id
}

# -----------------------------------------------------------------------------
# RESUMO DO DEPLOY
# -----------------------------------------------------------------------------

output "deployment_summary" {
  description = "Resumo do deploy"
  value = <<-EOT
    
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    DEPLOY CONCLUÍDO COM SUCESSO                  ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                                                                  ║
    ║  🏗️  INFRAESTRUTURA                                              ║
    ║  ├── VPC: ${module.vpc.vpc_id}
    ║  ├── Subnets Públicas: ${length(module.vpc.public_subnets)}
    ║  └── Subnets Privadas: ${length(module.vpc.private_subnets)}
    ║                                                                  ║
    ║  ☸️  KUBERNETES (EKS)                                            ║
    ║  ├── Cluster: ${module.eks.cluster_name}
    ║  ├── Versão: ${module.eks.cluster_version}
    ║  └── Nodes: ${var.eks_desired_nodes}
    ║                                                                  ║
    ║  📦 CONTAINER REGISTRY                                           ║
    ║  └── ECR: ${aws_ecr_repository.app.repository_url}
    ║                                                                  ║
    ║  🗄️  STORAGE                                                      ║
    ║  └── S3: ${aws_s3_bucket.curriculos.bucket}
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    📋 PRÓXIMOS PASSOS:
    
    1. Configurar kubectl:
       $ aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}
    
    2. Fazer login no ECR:
       $ aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}
    
    3. Build e push da imagem:
       $ docker build -t leitura-ats .
       $ docker tag leitura-ats:latest ${aws_ecr_repository.app.repository_url}:latest
       $ docker push ${aws_ecr_repository.app.repository_url}:latest
    
    4. Deploy no Kubernetes:
       $ kubectl apply -f infra/kubernetes/
    
  EOT
}
