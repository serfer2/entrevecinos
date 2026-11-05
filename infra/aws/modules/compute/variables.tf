variable "instance_type" {
  description = "Tipo de la instancia (arm64). t4g.small entra en la capa gratuita del plan."
  type        = string
  default     = "t4g.small"
}

variable "root_volume_gb" {
  description = "Tamaño del volumen raíz (sistema, imágenes de Docker y swap)."
  type        = number
  default     = 20
}

variable "subnet_id" {
  description = "Subred pública de la instancia (TK-079)."
  type        = string
}

variable "security_group_id" {
  description = "Grupo de seguridad de la aplicación (TK-079)."
  type        = string
}

variable "postgres_volume_id" {
  description = "Volumen EBS de datos de PostgreSQL (TK-082)."
  type        = string
}

variable "media_bucket_arn" {
  description = "Bucket de imágenes (TK-080)."
  type        = string
}

variable "backups_bucket_arn" {
  description = "Bucket de copias de PostgreSQL (TK-082)."
  type        = string
}

variable "ecr_repository_arns" {
  description = "Repositorios de ECR de los que la instancia descarga imágenes (TK-080)."
  type        = list(string)
}

variable "ses_identity_arns" {
  description = "Identidades de SES con las que puede enviar: el dominio y, en sandbox, los destinatarios de prueba."
  type        = list(string)
}

variable "ses_configuration_set_arn" {
  description = "Configuration set de SES (TK-083)."
  type        = string
}

variable "mail_from_address" {
  description = "Único remitente permitido."
  type        = string
  default     = "no-reply@entrevecinos.org"
}

variable "compose_version" {
  description = "Versión del plugin Docker Compose (Amazon Linux 2023 no lo empaqueta)."
  type        = string
  default     = "5.6.1"
}

variable "compose_sha256" {
  description = "SHA-256 de docker-compose-linux-aarch64 de esa versión (checksums.txt de la release)."
  type        = string
  default     = "42cfa75f51ad0ccf290bad37899e0038a8c10a0069e85233ecc1d53e3ff1347d"
}
