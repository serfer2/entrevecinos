variable "availability_zone" {
  description = "Zona de la subred; el volumen de datos de PostgreSQL (TK-082) debe estar en la misma."
  type        = string
}

variable "vpc_cidr" {
  description = "Rango de la VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Rango de la subred pública. 10.20.1.0/24 queda reservado para una segunda zona."
  type        = string
  default     = "10.20.0.0/24"
}
