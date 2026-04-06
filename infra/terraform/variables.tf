# =============================================================================
# TERRAFORM VARIABLES
# =============================================================================
#
# Variáveis de configuração para a infraestrutura AWS.
# Valores padrão definidos para ambiente de desenvolvimento.
#
# =============================================================================

# -----------------------------------------------------------------------------
# GERAIS
# -----------------------------------------------------------------------------

variable "project_name" {
  description = "Nome do projeto (usado em tags e nomes de recursos)"
  type        = string
  default     = "leitura-ats"
}

variable "environment" {
  description = "Ambiente de deploy (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment deve ser: dev, staging ou prod."
  }
}

variable "aws_region" {
  description = "Região AWS para deploy"
  type        = string
  default     = "us-east-1"
}

# -----------------------------------------------------------------------------
# VPC E NETWORKING
# -----------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block da VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs das subnets públicas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDRs das subnets privadas"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

# -----------------------------------------------------------------------------
# EKS / KUBERNETES
# -----------------------------------------------------------------------------

variable "eks_cluster_version" {
  description = "Versão do Kubernetes no EKS"
  type        = string
  default     = "1.28"
}

variable "eks_node_instance_types" {
  description = "Tipos de instância para os worker nodes"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "eks_min_nodes" {
  description = "Número mínimo de nodes no cluster"
  type        = number
  default     = 1
}

variable "eks_max_nodes" {
  description = "Número máximo de nodes no cluster"
  type        = number
  default     = 3
}

variable "eks_desired_nodes" {
  description = "Número desejado de nodes no cluster"
  type        = number
  default     = 2
}

# -----------------------------------------------------------------------------
# APLICAÇÃO
# -----------------------------------------------------------------------------

variable "app_port" {
  description = "Porta da aplicação Flask"
  type        = number
  default     = 5000
}

variable "app_replicas" {
  description = "Número de réplicas da aplicação"
  type        = number
  default     = 2
}

variable "app_cpu_request" {
  description = "CPU request para a aplicação"
  type        = string
  default     = "250m"
}

variable "app_cpu_limit" {
  description = "CPU limit para a aplicação"
  type        = string
  default     = "500m"
}

variable "app_memory_request" {
  description = "Memory request para a aplicação"
  type        = string
  default     = "256Mi"
}

variable "app_memory_limit" {
  description = "Memory limit para a aplicação"
  type        = string
  default     = "512Mi"
}

# -----------------------------------------------------------------------------
# OBSERVABILIDADE
# -----------------------------------------------------------------------------

variable "log_retention_days" {
  description = "Dias de retenção de logs no CloudWatch"
  type        = number
  default     = 30
}

variable "enable_monitoring" {
  description = "Habilitar monitoramento com Prometheus/Grafana"
  type        = bool
  default     = true
}
