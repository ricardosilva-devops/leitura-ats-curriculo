# =============================================================================
# TERRAFORM - Infraestrutura AWS para Leitura ATS
# =============================================================================
#
# Este arquivo define a infraestrutura completa para deploy da aplicação
# de análise ATS de currículos na AWS, incluindo:
#
# - VPC com subnets públicas e privadas
# - EKS (Kubernetes gerenciado)
# - ECR (Registry de containers)
# - RDS PostgreSQL (opcional para persistência)
# - S3 para armazenamento de currículos
# - CloudWatch para logs e monitoramento
#
# Autor: Ricardo da Silva Júnior
# Versão: 1.0.0
# =============================================================================

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  # Backend S3 para estado remoto (recomendado em produção)
  # backend "s3" {
  #   bucket         = "leitura-ats-terraform-state"
  #   key            = "terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-locks"
  # }
}

# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "leitura-ats"
      Environment = var.environment
      ManagedBy   = "terraform"
      Owner       = "ricardo-silva-jr"
    }
  }
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# =============================================================================
# VPC - REDE VIRTUAL
# =============================================================================

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  # NAT Gateway para acesso à internet das subnets privadas
  enable_nat_gateway     = true
  single_nat_gateway     = var.environment == "dev" ? true : false
  one_nat_gateway_per_az = var.environment == "prod" ? true : false

  # DNS
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags para integração com EKS
  public_subnet_tags = {
    "kubernetes.io/role/elb"                              = 1
    "kubernetes.io/cluster/${var.project_name}-eks"       = "shared"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"                     = 1
    "kubernetes.io/cluster/${var.project_name}-eks"       = "shared"
  }

  tags = {
    Component = "networking"
  }
}

# =============================================================================
# SECURITY GROUPS
# =============================================================================

resource "aws_security_group" "app" {
  name        = "${var.project_name}-app-sg"
  description = "Security group para aplicacao Leitura ATS"
  vpc_id      = module.vpc.vpc_id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # Flask (interno)
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    self        = true
    description = "Flask interno"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Saida irrestrita"
  }

  tags = {
    Name      = "${var.project_name}-app-sg"
    Component = "security"
  }
}

# =============================================================================
# ECR - CONTAINER REGISTRY
# =============================================================================

resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Component = "container-registry"
  }
}

# Lifecycle policy para limpeza de imagens antigas
resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Manter apenas as ultimas 10 imagens"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# =============================================================================
# EKS - KUBERNETES
# =============================================================================

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project_name}-eks"
  cluster_version = var.eks_cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Endpoint público para desenvolvimento
  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  # Addons do EKS
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  # Node Groups
  eks_managed_node_groups = {
    main = {
      name           = "${var.project_name}-node-group"
      instance_types = var.eks_node_instance_types
      
      min_size     = var.eks_min_nodes
      max_size     = var.eks_max_nodes
      desired_size = var.eks_desired_nodes

      # Usar Spot instances para economia (dev)
      capacity_type = var.environment == "dev" ? "SPOT" : "ON_DEMAND"

      labels = {
        Environment = var.environment
        Project     = var.project_name
      }

      tags = {
        Component = "compute"
      }
    }
  }

  # IRSA (IAM Roles for Service Accounts)
  enable_irsa = true

  tags = {
    Component = "kubernetes"
  }
}

# =============================================================================
# S3 - ARMAZENAMENTO DE CURRÍCULOS
# =============================================================================

resource "aws_s3_bucket" "curriculos" {
  bucket = "${var.project_name}-curriculos-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Component = "storage"
  }
}

resource "aws_s3_bucket_versioning" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle para mover currículos antigos para Glacier
resource "aws_s3_bucket_lifecycle_configuration" "curriculos" {
  bucket = aws_s3_bucket.curriculos.id

  rule {
    id     = "archive-old-curriculos"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}

# =============================================================================
# CLOUDWATCH - LOGS E MONITORAMENTO
# =============================================================================

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = var.log_retention_days

  tags = {
    Component = "observability"
  }
}

# Alarme de alta utilização de CPU
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU acima de 80%"

  dimensions = {
    ClusterName = module.eks.cluster_name
  }

  tags = {
    Component = "observability"
  }
}
