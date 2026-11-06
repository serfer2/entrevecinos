# Acceso de GitHub Actions a AWS (TK-088). La política de control de servicios del proyecto deniega
# los proveedores OIDC (iam:CreateOpenIDConnectProvider), así que GitHub usa la clave de un usuario
# IAM que solo puede asumir el rol de despliegue. La clave se crea fuera de Terraform (no queda en
# el estado) y vive como secreto del entorno `production` de GitHub; ver infra/aws/README.md.
# Pasar a OIDC solo cambia la confianza del rol.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id   = data.aws_caller_identity.current.account_id
  region       = data.aws_region.current.region
  instance_arn = "arn:aws:ec2:${local.region}:${local.account_id}:instance/${var.instance_id}"
  document_arn = "arn:aws:ssm:${local.region}:${local.account_id}:document/${var.deploy_document_name}"
}

resource "aws_iam_user" "github" {
  #checkov:skip=CKV_AWS_273:la política de control de servicios del proyecto no admite OIDC ni SSO para CI
  name = "entrevecinos-github-actions"
  path = "/ci/"
}

data "aws_iam_policy_document" "user" {
  statement {
    sid       = "AssumeDeployRole"
    actions   = ["sts:AssumeRole"]
    resources = [aws_iam_role.deploy.arn]
  }
}

resource "aws_iam_user_policy" "github" {
  #checkov:skip=CKV_AWS_40:una sola política propia; el usuario no está en ningún grupo
  name   = "assume-deploy-role"
  user   = aws_iam_user.github.name
  policy = data.aws_iam_policy_document.user.json
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = [aws_iam_user.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "sts:ExternalId"
      values   = [var.external_id]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name                 = "entrevecinos-github-deploy"
  description          = "Despliegue continuo desde GitHub Actions (TK-088)"
  assume_role_policy   = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "deploy" {
  # El token de ECR no admite recursos concretos.
  statement {
    sid       = "EcrLogin"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  # Publicar imágenes de api y web; nunca borrarlas.
  statement {
    sid = "EcrPush"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
      "ecr:BatchGetImage",
    ]
    resources = var.ecr_repository_arns
  }

  # Solo el documento de despliegue y solo en la instancia de producción.
  statement {
    sid       = "Deploy"
    actions   = ["ssm:SendCommand"]
    resources = [local.document_arn, local.instance_arn]
  }

  # Seguir el resultado del despliegue: estas acciones no admiten recursos concretos.
  statement {
    sid       = "DeployStatus"
    actions   = ["ssm:GetCommandInvocation", "ssm:ListCommandInvocations"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "deploy"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}
