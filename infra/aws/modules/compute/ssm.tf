# Session Manager y Patch Manager (TK-085).

resource "aws_cloudwatch_log_group" "sessions" {
  name              = "/entrevecinos/prod/ssm-sessions"
  retention_in_days = 30
}

# Preferencias de Session Manager de la región (no existían): registro de cada sesión en CloudWatch
# Logs y límites de duración.
resource "aws_ssm_document" "session_preferences" {
  #checkov:skip=CKV_AWS_112:el cifrado de la sesión con KMS necesita una clave propia (coste); viaja por TLS
  #checkov:skip=CKV_AWS_113:el registro se cifra con la clave del servicio de CloudWatch Logs, sin KMS propio
  name            = "SSM-SessionManagerRunShell"
  document_type   = "Session"
  document_format = "JSON"

  content = jsonencode({
    schemaVersion = "1.0"
    description   = "Preferencias de Session Manager de EntreVecinos (TK-085)"
    sessionType   = "Standard_Stream"
    inputs = {
      s3BucketName                = ""
      s3KeyPrefix                 = ""
      s3EncryptionEnabled         = true
      cloudWatchLogGroupName      = aws_cloudwatch_log_group.sessions.name
      cloudWatchEncryptionEnabled = false
      cloudWatchStreamingEnabled  = true
      kmsKeyId                    = ""
      idleSessionTimeout          = "20"
      maxSessionDuration          = "60"
      runAsEnabled                = false
      runAsDefaultUser            = ""
      shellProfile                = { linux = "", windows = "" }
    }
  })
}

# Parches semanales los domingos a las 04:00 UTC (fuera de las copias y del snapshot), con reinicio
# si hace falta. También se ejecuta al crear la asociación.
resource "aws_ssm_association" "patch" {
  name                = "AWS-RunPatchBaseline"
  association_name    = "entrevecinos-prod-patch"
  schedule_expression = "cron(0 4 ? * SUN *)"

  parameters = {
    Operation    = "Install"
    RebootOption = "RebootIfNeeded"
  }

  targets {
    key    = "InstanceIds"
    values = [aws_instance.app.id]
  }
}
