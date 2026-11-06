# Correo de producción por SMTP con Brevo (TK-098): DKIM del dominio y registros de marca con el
# prefijo send (mail.<dominio> es el MAIL FROM de SES y un CNAME no puede convivir con sus MX y TXT).
# Los valores los da Brevo al autenticar el dominio; la verificación (brevo-code) va en el TXT de la
# raíz (modules/domain).

resource "aws_route53_record" "brevo" {
  for_each = var.brevo_cnames

  zone_id = var.zone_id
  name    = "${each.key}.${var.domain}"
  type    = "CNAME"
  ttl     = 3600
  records = [each.value]
}
