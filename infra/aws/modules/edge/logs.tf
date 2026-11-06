# Registros estándar de acceso (v2) de CloudFront en CloudWatch Logs. La fuente de una distribución
# solo existe en us-east-1, así que el grupo también está allí.

resource "aws_cloudwatch_log_group" "access" {
  name              = "/entrevecinos/prod/cloudfront"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_delivery_source" "access" {
  name         = "entrevecinos-cloudfront"
  log_type     = "ACCESS_LOGS"
  resource_arn = aws_cloudfront_distribution.this.arn
}

resource "aws_cloudwatch_log_delivery_destination" "access" {
  name          = "entrevecinos-cloudfront"
  output_format = "json"

  delivery_destination_configuration {
    destination_resource_arn = aws_cloudwatch_log_group.access.arn
  }
}

# Campos elegidos, sin cs-uri-query (el enlace de validación del correo lleva el token en ?token=),
# cs(Cookie) (sesión) ni cs(Referer) (repetiría la URL anterior con su consulta) (TK-091).
resource "aws_cloudwatch_log_delivery" "access" {
  delivery_source_name     = aws_cloudwatch_log_delivery_source.access.name
  delivery_destination_arn = aws_cloudwatch_log_delivery_destination.access.arn

  record_fields = [
    "date", "time", "x-edge-location", "sc-bytes", "c-ip", "cs-method", "cs(Host)", "cs-uri-stem",
    "sc-status", "cs(User-Agent)", "x-edge-result-type", "x-edge-request-id", "x-host-header",
    "cs-protocol", "cs-bytes", "time-taken", "ssl-protocol", "x-edge-response-result-type",
    "cs-protocol-version", "time-to-first-byte", "x-edge-detailed-result-type", "sc-content-type",
    "c-country", "cache-behavior-path-pattern",
  ]
}
