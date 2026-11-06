# Correo con SES y secreto de los JWT (TK-083), e identidad del dominio con DKIM y MAIL FROM
# (TK-084), cuyos registros se publican en la zona de Route 53 de modules/domain.

resource "aws_sesv2_configuration_set" "this" {
  configuration_set_name = "entrevecinos-prod"

  delivery_options {
    tls_policy = "REQUIRE"
  }

  reputation_options {
    reputation_metrics_enabled = true
  }

  suppression_options {
    suppressed_reasons = ["BOUNCE", "COMPLAINT"]
  }
}

# Métricas de envío en CloudWatch para las alarmas de rebotes y quejas (TK-091).
resource "aws_sesv2_configuration_set_event_destination" "cloudwatch" {
  configuration_set_name = aws_sesv2_configuration_set.this.configuration_set_name
  event_destination_name = "cloudwatch"

  event_destination {
    enabled              = true
    matching_event_types = ["SEND", "REJECT", "BOUNCE", "COMPLAINT", "DELIVERY"]

    cloud_watch_destination {
      dimension_configuration {
        dimension_name          = "app"
        dimension_value_source  = "MESSAGE_TAG"
        default_dimension_value = "entrevecinos"
      }
    }
  }
}

# Lista de supresión de la cuenta: no se reintenta el envío a direcciones con rebotes o quejas.
resource "aws_sesv2_account_suppression_attributes" "this" {
  suppressed_reasons = ["BOUNCE", "COMPLAINT"]
}

# Destinatarios de prueba mientras SES esté en sandbox: AWS les envía un correo de verificación.
resource "aws_sesv2_email_identity" "test_recipient" {
  for_each = toset(var.test_recipients)

  email_identity = each.value
}

# Efímero y de solo escritura: no queda en el estado. Solo se escribe cuando cambia
# `jwt_secret_version`; rotarlo invalida todas las sesiones.
ephemeral "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "aws_ssm_parameter" "jwt_secret" {
  name             = "/entrevecinos/prod/jwt-secret"
  description      = "Clave de firma de los JWT de la API (TK-083)"
  type             = "SecureString"
  tier             = "Standard"
  value_wo         = ephemeral.random_password.jwt_secret.result
  value_wo_version = var.jwt_secret_version
}

# --- Dominio (TK-084) ---

data "aws_region" "current" {}

# Identidad del dominio: SES firma con DKIM como entrevecinos.org y usa el configuration set.
resource "aws_sesv2_email_identity" "domain" {
  email_identity         = var.domain
  configuration_set_name = aws_sesv2_configuration_set.this.configuration_set_name

  dkim_signing_attributes {
    next_signing_key_length = "RSA_2048_BIT"
  }
}

# SES siempre da 3 tokens de DKIM; se conocen tras crear la identidad, así que se cuentan.
resource "aws_route53_record" "dkim" {
  count = 3

  zone_id = var.zone_id
  name    = "${aws_sesv2_email_identity.domain.dkim_signing_attributes[0].tokens[count.index]}._domainkey.${var.domain}"
  type    = "CNAME"
  ttl     = var.dns_ttl
  records = ["${aws_sesv2_email_identity.domain.dkim_signing_attributes[0].tokens[count.index]}.dkim.amazonses.com"]
}

# MAIL FROM propio: los rebotes vuelven a mail.<dominio> y el SPF se alinea con DMARC (aspf=r).
resource "aws_sesv2_email_identity_mail_from_attributes" "domain" {
  email_identity         = aws_sesv2_email_identity.domain.email_identity
  mail_from_domain       = "mail.${var.domain}"
  behavior_on_mx_failure = "USE_DEFAULT_VALUE"
}

resource "aws_route53_record" "mail_from_mx" {
  zone_id = var.zone_id
  name    = aws_sesv2_email_identity_mail_from_attributes.domain.mail_from_domain
  type    = "MX"
  ttl     = var.dns_ttl
  records = ["10 feedback-smtp.${data.aws_region.current.region}.amazonses.com"]
}

resource "aws_route53_record" "mail_from_spf" {
  zone_id = var.zone_id
  name    = aws_sesv2_email_identity_mail_from_attributes.domain.mail_from_domain
  type    = "TXT"
  ttl     = var.dns_ttl
  records = ["v=spf1 include:amazonses.com -all"]
}
