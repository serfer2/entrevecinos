# DNS de entrevecinos.org en Route 53 y certificado HTTPS (TK-084). El dominio sigue registrado en
# Dinahosting; allí solo se cambian los servidores de nombres por los de `name_servers`, una vez.
# Los registros de la web (alias a CloudFront) se crean en TK-087 y los de SES en modules/mail.

resource "aws_route53_zone" "this" {
  #checkov:skip=CKV2_AWS_38:DNSSEC necesita una clave KMS en us-east-1; se deja para la evolución
  #checkov:skip=CKV2_AWS_39:el registro de consultas añade coste sin necesidad actual
  name    = var.domain
  comment = "EntreVecinos (gestionada por Terraform; no editar a mano)"

  lifecycle {
    prevent_destroy = true
  }
}

# Route 53 admite un solo conjunto TXT por nombre: el SPF de la raíz y los códigos de verificación
# de otros servicios (Brevo, TK-098) van en el mismo registro. La raíz no envía correo con su propio
# sobre: SES usa el MAIL FROM mail.<dominio> (modules/mail) y Brevo, send.<dominio>.
resource "aws_route53_record" "spf" {
  zone_id = aws_route53_zone.this.zone_id
  name    = var.domain
  type    = "TXT"
  ttl     = var.dns_ttl
  records = concat(["v=spf1 -all"], var.root_txt_records)
}

# DMARC en observación (p=none); endurecer a quarantine y reject tras unas semanas sin fallos.
resource "aws_route53_record" "dmarc" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "_dmarc.${var.domain}"
  type    = "TXT"
  ttl     = var.dns_ttl
  records = [join("; ", concat(["v=DMARC1", "p=none", "adkim=s", "aspf=r"], [for a in var.dmarc_rua : "rua=mailto:${a}"]))]
}

# Solo Amazon emite certificados del dominio, y ninguno comodín.
resource "aws_route53_record" "caa" {
  zone_id = aws_route53_zone.this.zone_id
  name    = var.domain
  type    = "CAA"
  ttl     = var.dns_ttl
  records = [
    "0 issue \"amazon.com\"",
    "0 issue \"amazontrust.com\"",
    "0 issue \"awstrust.com\"",
    "0 issue \"amazonaws.com\"",
    "0 issuewild \";\"",
  ]
}

# CloudFront exige el certificado en us-east-1.
resource "aws_acm_certificate" "this" {
  provider = aws.us_east_1

  domain_name               = var.domain
  subject_alternative_names = ["www.${var.domain}"]
  validation_method         = "DNS"
  key_algorithm             = "RSA_2048"

  lifecycle {
    create_before_destroy = true
  }
}

# Registros de validación; mientras existan, ACM renueva el certificado solo.
resource "aws_route53_record" "certificate_validation" {
  for_each = {
    for option in aws_acm_certificate.this.domain_validation_options :
    option.domain_name => option
  }

  zone_id         = aws_route53_zone.this.zone_id
  name            = each.value.resource_record_name
  type            = each.value.resource_record_type
  ttl             = var.dns_ttl
  records         = [each.value.resource_record_value]
  allow_overwrite = true
}

# Solo tras delegar el dominio: espera a que ACM vea los registros y emita el certificado.
resource "aws_acm_certificate_validation" "this" {
  count    = var.wait_for_certificate_validation ? 1 : 0
  provider = aws.us_east_1

  certificate_arn         = aws_acm_certificate.this.arn
  validation_record_fqdns = [for record in aws_route53_record.certificate_validation : record.fqdn]

  timeouts {
    create = "2h"
  }
}
