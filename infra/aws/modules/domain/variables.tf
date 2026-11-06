variable "domain" {
  description = "Dominio de la web y del correo."
  type        = string
  default     = "entrevecinos.org"
}

variable "dns_ttl" {
  description = "TTL de los registros: 300 durante la puesta en marcha, 3600 cuando esté estable."
  type        = number
  default     = 300
}

variable "wait_for_certificate_validation" {
  description = "Esperar a que ACM emita el certificado; solo cuando el dominio ya esté delegado en Route 53."
  type        = bool
  default     = false
}
