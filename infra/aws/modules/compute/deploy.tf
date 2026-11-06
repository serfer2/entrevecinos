# Despliegue de la aplicación (TK-086): documento de SSM, grupos de logs y cabecera de origen.

# Logs de los contenedores (driver awslogs), de las copias (agente de CloudWatch, TK-091) y de cada
# despliegue (salida de Run Command). El rol de la instancia escribe en /entrevecinos/prod/app/*, pero
# no puede crear grupos. Retención corta para recortar costes; los despliegues, 30 días (auditoría).
resource "aws_cloudwatch_log_group" "app" {
  for_each = { proxy = 14, web = 14, api = 14, db = 14, backup = 14, deploy = 30 }

  name              = "/entrevecinos/prod/app/${each.key}"
  retention_in_days = each.value
}

# Cabecera secreta que CloudFront (TK-087) añade y el proxy exige. A diferencia de las contraseñas,
# queda en el estado: la cabecera de origen de CloudFront no admite valores de solo escritura.
resource "random_password" "origin_verify" {
  length  = 48
  special = false

  keepers = {
    version = var.origin_verify_version
  }
}

resource "aws_ssm_parameter" "origin_verify" {
  name        = "/entrevecinos/prod/origin-verify"
  description = "Cabecera X-Origin-Verify entre CloudFront y el proxy de la instancia (TK-086)"
  type        = "SecureString"
  tier        = "Standard"
  value       = random_password.origin_verify.result
}

locals {
  infra_dir = "${path.module}/../../.."

  # Ficheros que el documento escribe en /opt/entrevecinos, con la misma estructura que infra/.
  deploy_files = {
    "docker-compose.prod.yml"          = { mode = "644", source = "docker-compose.prod.yml" }
    "prod/deploy.sh"                   = { mode = "755", source = "prod/deploy.sh" }
    "prod/backup.sh"                   = { mode = "755", source = "prod/backup.sh" }
    "prod/restore.sh"                  = { mode = "755", source = "prod/restore.sh" }
    "prod/initdb/10-roles.sh"          = { mode = "755", source = "prod/initdb/10-roles.sh" }
    "prod/proxy/default.conf.template" = { mode = "644", source = "prod/proxy/default.conf.template" }
    "prod/systemd/entrevecinos-backup.service" = {
      mode = "644", source = "prod/systemd/entrevecinos-backup.service"
    }
    "prod/systemd/entrevecinos-backup.timer" = {
      mode = "644", source = "prod/systemd/entrevecinos-backup.timer"
    }
  }

  write_files = [
    for path, file in local.deploy_files :
    "echo '${filebase64("${local.infra_dir}/${file.source}")}' | base64 -d > \"$app/${path}\" && chmod ${file.mode} \"$app/${path}\""
  ]
}

# Copia la configuración de esta versión del repositorio y ejecuta deploy.sh. Cambiar un fichero
# de infra/prod/ o el Compose exige `make tf-apply` antes de desplegar.
resource "aws_ssm_document" "deploy" {
  name            = "entrevecinos-deploy"
  document_type   = "Command"
  document_format = "JSON"
  target_type     = "/AWS::EC2::Instance"

  content = jsonencode({
    schemaVersion = "2.2"
    description   = "Despliega EntreVecinos en la instancia con los digests de api y web (TK-086)"
    parameters = {
      ApiDigest = {
        type           = "String"
        description    = "Digest de la imagen de la API en ECR (sha256:...)"
        allowedPattern = "^sha256:[a-f0-9]{64}$"
      }
      WebDigest = {
        type           = "String"
        description    = "Digest de la imagen de la web en ECR (sha256:...)"
        allowedPattern = "^sha256:[a-f0-9]{64}$"
      }
    }
    mainSteps = [{
      action = "aws:runShellScript"
      name   = "deploy"
      inputs = {
        timeoutSeconds = "1200"
        runCommand = concat(
          [
            "set -euo pipefail",
            "app=/opt/entrevecinos",
            "install -d -m 750 -o deploy -g deploy \"$app\"",
            "install -d -m 755 \"$app/prod\" \"$app/prod/initdb\" \"$app/prod/proxy\" \"$app/prod/systemd\"",
          ],
          local.write_files,
          ["\"$app/prod/deploy.sh\" '{{ ApiDigest }}' '{{ WebDigest }}'"],
        )
      }
    }]
  })
}
