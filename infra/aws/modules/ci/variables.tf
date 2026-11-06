variable "ecr_repository_arns" {
  description = "Repositorios ECR en los que GitHub Actions publica imágenes (TK-080)."
  type        = list(string)
}

variable "instance_id" {
  description = "Instancia de producción en la que se despliega (TK-085)."
  type        = string
}

variable "deploy_document_name" {
  description = "Documento de SSM que despliega la aplicación (TK-086)."
  type        = string
}

variable "external_id" {
  description = "ExternalId que exige la confianza del rol (no es secreto; evita asumirlo por error)."
  type        = string
  default     = "entrevecinos-github-actions"
}
