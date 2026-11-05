# PostgreSQL en la instancia (TK-082), mientras el proyecto no escale: volumen de datos propio,
# snapshots diarios, bucket de copias que la instancia no puede borrar y contraseñas en
# Parameter Store. El contenedor `db` y los scripts están en infra/prod/ (TK-086).

data "aws_caller_identity" "current" {}

# --- Volumen de datos: separado de la raíz, sobrevive a la instancia ---

resource "aws_ebs_volume" "postgres" {
  availability_zone = var.availability_zone
  size              = var.volume_size_gb
  type              = "gp3"
  encrypted         = true

  tags = {
    Name     = "entrevecinos-prod-postgres"
    Snapshot = "entrevecinos-postgres"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# --- Snapshots diarios del volumen ---

data "aws_iam_policy_document" "dlm_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["dlm.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "dlm" {
  name               = "entrevecinos-prod-dlm"
  assume_role_policy = data.aws_iam_policy_document.dlm_assume.json
}

resource "aws_iam_role_policy_attachment" "dlm" {
  role       = aws_iam_role.dlm.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole"
}

resource "aws_dlm_lifecycle_policy" "postgres" {
  description        = "Snapshots diarios del volumen de PostgreSQL"
  execution_role_arn = aws_iam_role.dlm.arn
  state              = "ENABLED"

  policy_details {
    resource_types = ["VOLUME"]
    target_tags    = { Snapshot = "entrevecinos-postgres" }

    schedule {
      name      = "diario"
      copy_tags = true

      create_rule {
        interval      = 24
        interval_unit = "HOURS"
        times         = ["03:00"]
      }

      retain_rule {
        count = var.snapshot_retention_count
      }

      tags_to_add = { Name = "entrevecinos-prod-postgres" }
    }
  }
}

# --- Bucket de copias de pg_dump ---

# La instancia solo escribe y lee copias (TK-085); borrar queda reservado a los roles de
# administración, así que quien comprometa la instancia no puede eliminarlas. La caducidad por
# ciclo de vida la ejecuta S3 y no le afecta esta denegación.
data "aws_iam_policy_document" "backups_deny_delete" {
  statement {
    sid    = "DenyDeleteExceptAdmins"
    effect = "Deny"
    actions = [
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
    ]
    resources = ["arn:aws:s3:::${local.backups_bucket}/*"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    condition {
      test     = "ArnNotLike"
      variable = "aws:PrincipalArn"
      values   = var.admin_role_arns
    }
  }
}

locals {
  backups_bucket = "entrevecinos-backups-${data.aws_caller_identity.current.account_id}"
}

module "backups_bucket" {
  source = "../private-bucket"

  name                    = local.backups_bucket
  expiration_days         = var.backup_retention_days
  noncurrent_version_days = 7
  extra_policy_documents  = [data.aws_iam_policy_document.backups_deny_delete.json]
}

# --- Contraseñas y parámetros de conexión ---

# Efímeras y de solo escritura: no quedan en el estado. Solo se escriben cuando cambia
# `password_version`, que se sube a mano para rotarlas (procedimiento en infra/aws/README.md).
ephemeral "random_password" "db" {
  for_each = toset(["postgres", "owner", "app"])

  length  = 40
  special = false
}

resource "aws_ssm_parameter" "password" {
  for_each = toset(["postgres", "owner", "app"])

  name             = "/entrevecinos/prod/db/${each.key}-password"
  description      = "Contraseña del rol ${each.key} de PostgreSQL (TK-082)"
  type             = "SecureString"
  tier             = "Standard"
  value_wo         = ephemeral.random_password.db[each.key].result
  value_wo_version = var.password_version
}

resource "aws_ssm_parameter" "connection" {
  #checkov:skip=CKV2_AWS_34:host, puerto y nombre de la base no son secretos
  for_each = {
    host = "db"
    port = "5432"
    name = "entrevecinos"
  }

  name        = "/entrevecinos/prod/db/${each.key}"
  description = "Conexión a PostgreSQL en la red interna de Compose (TK-082)"
  type        = "String"
  tier        = "Standard"
  value       = each.value
}
