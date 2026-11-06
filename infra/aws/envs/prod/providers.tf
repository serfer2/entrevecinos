locals {
  default_tags = {
    Project     = "entrevecinos"
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}

# Región del proyecto: todos los recursos regionales van aquí.
provider "aws" {
  region = "eu-north-1"

  default_tags {
    tags = local.default_tags
  }
}

# Solo para recursos globales de CloudFront que AWS exige en us-east-1: certificado de ACM
# (TK-084) y plan de tarifa plana con su WAF (TK-087).
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = local.default_tags
  }
}
