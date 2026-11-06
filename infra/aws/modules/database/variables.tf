variable "availability_zone" {
  description = "Zona del volumen; debe ser la de la subred de la instancia (TK-079)."
  type        = string
}

variable "admin_role_arns" {
  description = "ARN (admite comodines) de los roles que pueden borrar copias del bucket."
  type        = list(string)
}

variable "volume_size_gb" {
  description = "Tamaño del volumen de datos de PostgreSQL."
  type        = number
  default     = 10
}

variable "snapshot_retention_count" {
  description = "Número de snapshots diarios que se conservan."
  type        = number
  default     = 7
}

variable "backup_retention_days" {
  description = "Días que se conservan las copias de pg_dump."
  type        = number
  default     = 30
}

variable "password_version" {
  description = "Versión de las contraseñas de PostgreSQL; subirla genera y escribe contraseñas nuevas."
  type        = number
  default     = 1
}
