# Rol de la instancia (TK-085): mínimo privilegio. Lo usan el agente de SSM, deploy.sh y los
# contenedores (hop limit 2), así que solo permite lo que necesita la aplicación.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id    = data.aws_caller_identity.current.account_id
  region        = data.aws_region.current.region
  parameter_arn = "arn:aws:ssm:${local.region}:${local.account_id}:parameter/entrevecinos/prod"
  log_group_arn = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/entrevecinos/prod"
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  name               = "entrevecinos-prod-app"
  description        = "Instancia de aplicacion de EntreVecinos (TK-085)"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

# Agente de SSM: Session Manager, Run Command (deploy.sh) y Patch Manager.
resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_iam_policy_document" "app" {
  # Imágenes de los anuncios: la API sube y las lee con URL prefirmadas. Nunca borra.
  statement {
    sid       = "MediaReadWrite"
    actions   = ["s3:PutObject", "s3:GetObject"]
    resources = ["${var.media_bucket_arn}/*"]
  }

  # Copias de PostgreSQL: backup.sh sube y comprueba; restore.sh (TK-092) lee. El borrado lo deniega
  # además la política del bucket.
  statement {
    sid       = "BackupsWriteRead"
    actions   = ["s3:PutObject", "s3:GetObject"]
    resources = ["${var.backups_bucket_arn}/postgres/*"]
  }

  statement {
    sid       = "SendMailAsNoReply"
    actions   = ["ses:SendEmail"]
    resources = concat(var.ses_identity_arns, [var.ses_configuration_set_arn])

    condition {
      test     = "StringEquals"
      variable = "ses:FromAddress"
      values   = [var.mail_from_address]
    }
  }

  # Secretos (SecureString, clave gestionada aws/ssm) y configuración de producción.
  statement {
    sid       = "ReadProdParameters"
    actions   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = [local.parameter_arn, "${local.parameter_arn}/*"]
  }

  # AmazonSSMManagedInstanceCore concede ssm:GetParameter(s) sobre "*": sin esta denegación, la
  # instancia leería cualquier parámetro de la cuenta. Quedan los de producción y los públicos de AWS.
  statement {
    sid    = "DenyOtherParameters"
    effect = "Deny"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParametersByPath",
      "ssm:GetParameterHistory",
    ]
    not_resources = [
      local.parameter_arn,
      "${local.parameter_arn}/*",
      "arn:aws:ssm:${local.region}::parameter/aws/*",
    ]
  }

  statement {
    sid       = "EcrLogin"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"] # La acción no admite recursos.
  }

  statement {
    sid       = "EcrPull"
    actions   = ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer", "ecr:BatchCheckLayerAvailability"]
    resources = var.ecr_repository_arns
  }

  # Logs de los contenedores (TK-086) y de las sesiones de Session Manager.
  statement {
    sid     = "WriteOwnLogs"
    actions = ["logs:CreateLogStream", "logs:PutLogEvents", "logs:DescribeLogStreams"]
    resources = [
      "${local.log_group_arn}/app/*",
      aws_cloudwatch_log_group.sessions.arn,
      "${aws_cloudwatch_log_group.sessions.arn}:log-stream:*",
    ]
  }

  # Session Manager comprueba el grupo antes de enviar la sesión; la acción no admite recursos.
  statement {
    sid       = "DescribeLogGroups"
    actions   = ["logs:DescribeLogGroups"]
    resources = ["*"]
  }

  # Métrica de copias (TK-082) y del agente de CloudWatch (TK-091); la acción no admite recursos.
  statement {
    sid       = "PutOwnMetrics"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = ["Entrevecinos/Backup", "CWAgent"]
    }
  }
}

resource "aws_iam_role_policy" "app" {
  name   = "entrevecinos-app"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app.json
}

resource "aws_iam_instance_profile" "app" {
  name = "entrevecinos-prod-app"
  role = aws_iam_role.app.name
}
