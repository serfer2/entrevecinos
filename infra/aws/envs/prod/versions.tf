terraform {
  # use_lockfile (bloqueo nativo del backend S3) desde 1.10; ephemeral y argumentos de solo
  # escritura (contraseñas fuera del estado, TK-082 y TK-083) desde 1.11.
  required_version = ">= 1.11"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.70.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.9"
    }
  }
}
