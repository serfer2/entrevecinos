# Agente de CloudWatch de la instancia (instalado en TK-085): memoria, swap, discos y el registro de
# las copias. La configuración vive en Parameter Store, bajo el prefijo que la instancia ya puede
# leer, y State Manager la aplica; se vuelve a aplicar cuando cambia.

locals {
  agent_config = {
    metrics = {
      namespace         = "CWAgent"
      append_dimensions = { InstanceId = "$${aws:InstanceId}" }
      metrics_collected = {
        mem  = { measurement = ["used_percent"], metrics_collection_interval = 60 }
        swap = { measurement = ["used_percent"], metrics_collection_interval = 60 }
        disk = {
          measurement                 = ["used_percent"]
          resources                   = ["/", var.postgres_mount]
          drop_device                 = true
          metrics_collection_interval = 300
        }
      }
    }
    logs = {
      logs_collected = {
        files = {
          collect_list = [{
            file_path       = "/var/log/entrevecinos/backup.log"
            log_group_name  = "${var.log_group_prefix}/backup"
            log_stream_name = "{instance_id}"
          }]
        }
      }
    }
  }
}

resource "aws_ssm_parameter" "agent_config" {
  #checkov:skip=CKV2_AWS_34:configuración del agente, sin secretos
  name        = "/entrevecinos/prod/cloudwatch-agent"
  description = "Configuración del agente de CloudWatch de la instancia (TK-091)"
  type        = "String"
  value       = jsonencode(local.agent_config)
}

resource "aws_ssm_association" "agent" {
  association_name = "entrevecinos-cloudwatch-agent"
  name             = "AmazonCloudWatch-ManageAgent"

  targets {
    key    = "InstanceIds"
    values = [var.instance_id]
  }

  parameters = {
    action                        = "configure"
    mode                          = "ec2"
    optionalConfigurationSource   = "ssm"
    optionalConfigurationLocation = aws_ssm_parameter.agent_config.name
    optionalRestart               = "yes"
  }

  lifecycle {
    replace_triggered_by = [aws_ssm_parameter.agent_config]
  }
}
