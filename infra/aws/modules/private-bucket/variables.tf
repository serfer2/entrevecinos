variable "name" {
  description = "Nombre global del bucket."
  type        = string
}

variable "noncurrent_version_days" {
  description = "Días que se conservan las versiones no actuales de cada objeto."
  type        = number
}

variable "expiration_days" {
  description = "Días tras los que caducan los objetos actuales; null para no caducarlos nunca."
  type        = number
  default     = null
}

variable "extra_policy_documents" {
  description = "Documentos de política adicionales (JSON) que se combinan con la denegación de HTTP."
  type        = list(string)
  default     = []
}
