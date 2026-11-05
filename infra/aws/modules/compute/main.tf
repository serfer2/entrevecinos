# Instancia de aplicación endurecida (TK-085): Docker Compose con proxy, web, API y PostgreSQL
# (TK-086). Sin SSH: se administra con Session Manager.

data "aws_ssm_parameter" "al2023_arm64" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"
}

locals {
  postgres_mount = "/srv/entrevecinos/postgres"
}

resource "aws_instance" "app" {
  #checkov:skip=CKV_AWS_88:sin NAT, la IP pública es la única salida; la entrada solo llega desde CloudFront (grupo de seguridad)
  #checkov:skip=CKV_AWS_126:la monitorización detallada cuesta; bastan las métricas de 5 minutos
  ami                         = data.aws_ssm_parameter.al2023_arm64.insecure_value
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.app.name
  ebs_optimized               = true
  disable_api_termination     = true
  monitoring                  = false

  # Sin cargos por exceso de CPU: con unlimited (el de T4g) un pico sostenido sale de los créditos.
  credit_specification {
    cpu_credits = "standard"
  }

  # IMDSv2 obligatorio; hop limit 2 para que los contenedores obtengan las credenciales del rol.
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
    instance_metadata_tags      = "disabled"
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_gb
    encrypted             = true
    delete_on_termination = true

    tags = { Name = "entrevecinos-prod-app-root" }
  }

  user_data = templatefile("${path.module}/user-data.sh.tftpl", {
    postgres_device = "/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_${replace(var.postgres_volume_id, "-", "")}"
    postgres_mount  = local.postgres_mount
    compose_version = var.compose_version
    compose_sha256  = var.compose_sha256
  })
  user_data_replace_on_change = false

  tags = { Name = "entrevecinos-prod-app" }

  # El user data solo actúa en el primer arranque y la AMI se actualiza con Patch Manager:
  # cambiarlos no debe parar ni recrear la instancia (reemplazarla es un procedimiento, TK-093).
  lifecycle {
    ignore_changes = [ami, user_data]
  }
}

resource "aws_volume_attachment" "postgres" {
  device_name                    = "/dev/sdf"
  volume_id                      = var.postgres_volume_id
  instance_id                    = aws_instance.app.id
  stop_instance_before_detaching = true
}

# Recuperación automática si falla el hardware de AWS (la instancia conserva ID, IP y volúmenes).
resource "aws_cloudwatch_metric_alarm" "recover" {
  alarm_name          = "entrevecinos-prod-app-recover"
  alarm_description   = "Recupera la instancia si falla el status check del sistema (TK-085)"
  namespace           = "AWS/EC2"
  metric_name         = "StatusCheckFailed_System"
  dimensions          = { InstanceId = aws_instance.app.id }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 2
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  alarm_actions       = ["arn:aws:automate:${local.region}:ec2:recover"]
}
