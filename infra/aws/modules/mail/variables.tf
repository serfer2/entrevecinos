variable "test_recipients" {
  description = "Direcciones que pueden recibir correo mientras SES esté en sandbox."
  type        = list(string)
  default     = []
}

variable "jwt_secret_version" {
  description = "Versión del secreto de los JWT; subirla genera uno nuevo (invalida las sesiones)."
  type        = number
  default     = 1
}

variable "domain" {
  description = "Dominio del remitente (identidad de SES)."
  type        = string
}

variable "zone_id" {
  description = "Zona de Route 53 donde se publican DKIM y MAIL FROM (TK-084)."
  type        = string
}

variable "dns_ttl" {
  description = "TTL de los registros de correo."
  type        = number
  default     = 300
}

variable "brevo_cnames" {
  description = "CNAME de Brevo (DKIM y marca), nombre relativo al dominio → destino (TK-098)."
  type        = map(string)
  default     = {}
}
