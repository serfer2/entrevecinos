variable "alert_email" {
  description = "Correo que recibe los avisos de gasto (TK-078) y de las alarmas (TK-091)."
  type        = string
}

variable "monthly_budget_usd" {
  description = "Presupuesto mensual en USD, equivalente al límite de gasto de 40 € (TK-078)."
  type        = number
  default     = 44
}

variable "availability_zone" {
  description = "Zona de la subred y del volumen de datos de PostgreSQL."
  type        = string
  default     = "eu-north-1a"
}

variable "admin_role_arns" {
  description = "Roles de administración que pueden borrar copias de la base de datos."
  type        = list(string)
}

variable "ses_test_recipients" {
  description = "Destinatarios de prueba mientras SES esté en sandbox (TK-083)."
  type        = list(string)
  default     = []
}

variable "db_password_version" {
  description = "Versión de las contraseñas de PostgreSQL; subirla las rota (TK-082)."
  type        = number
  default     = 1
}

variable "jwt_secret_version" {
  description = "Versión del secreto de los JWT; subirla lo rota e invalida las sesiones (TK-083)."
  type        = number
  default     = 1
}

variable "origin_verify_version" {
  description = "Súbela para rotar la cabecera secreta entre CloudFront y la instancia (TK-086)."
  type        = number
  default     = 1
}

variable "wait_for_certificate_validation" {
  description = "Esperar a que ACM emita el certificado; true solo cuando el dominio ya esté delegado en Route 53 (TK-084)."
  type        = bool
  default     = false
}
