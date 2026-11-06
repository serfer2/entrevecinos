variable "monthly_limit_usd" {
  description = "Importe mensual en USD, equivalente al límite de gasto de 40 € del proyecto."
  type        = number
}

variable "alert_email" {
  description = "Correo que recibe los avisos de gasto."
  type        = string
}
