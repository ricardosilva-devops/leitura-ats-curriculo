# =============================================================================
# IAM ROLES - Para IRSA (IAM Roles for Service Accounts)
# =============================================================================

# Data source para OIDC provider do EKS
data "aws_iam_policy_document" "pod_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [module.eks.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:sub"
      values   = ["system:serviceaccount:default:leitura-ats-sa"]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(module.eks.oidc_provider, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

# IAM Role para pods da aplicação
resource "aws_iam_role" "pod_role" {
  name               = "${var.project_name}-pod-role"
  assume_role_policy = data.aws_iam_policy_document.pod_assume_role.json

  tags = {
    Component = "iam"
  }
}

# Policy para acesso ao S3
resource "aws_iam_policy" "s3_access" {
  name        = "${var.project_name}-s3-access"
  description = "Permite acesso ao bucket S3 de currículos"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.curriculos.arn,
          "${aws_s3_bucket.curriculos.arn}/*"
        ]
      }
    ]
  })

  tags = {
    Component = "iam"
  }
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "pod_s3_access" {
  role       = aws_iam_role.pod_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Policy para CloudWatch Logs
resource "aws_iam_policy" "cloudwatch_logs" {
  name        = "${var.project_name}-cloudwatch-logs"
  description = "Permite escrever logs no CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "${aws_cloudwatch_log_group.app.arn}:*"
      }
    ]
  })

  tags = {
    Component = "iam"
  }
}

resource "aws_iam_role_policy_attachment" "pod_cloudwatch" {
  role       = aws_iam_role.pod_role.name
  policy_arn = aws_iam_policy.cloudwatch_logs.arn
}

# Output do ARN da role (para usar no ServiceAccount)
output "pod_role_arn" {
  description = "ARN da IAM Role para Service Account"
  value       = aws_iam_role.pod_role.arn
}
