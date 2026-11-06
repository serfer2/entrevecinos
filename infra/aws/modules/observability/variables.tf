variable "alert_email" {
  description = "Correo que recibe los avisos de las alarmas."
  type        = string
}

variable "instance_id" {
  description = "Instancia de aplicación (TK-085)."
  type        = string
}

variable "distribution_id" {
  description = "Distribución de CloudFront (TK-087)."
  type        = string
}

variable "postgres_mount" {
  description = "Punto de montaje del volumen de datos de PostgreSQL (TK-082)."
  type        = string
  default     = "/srv/entrevecinos/postgres"
}

variable "log_group_prefix" {
  description = "Prefijo de los grupos de registros de la aplicación (TK-086)."
  type        = string
  default     = "/entrevecinos/prod/app"
}
