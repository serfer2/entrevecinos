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

# Solo para lo que AWS exige en us-east-1: certificado de ACM (TK-084), CloudFront y sus registros
# (TK-087). La política del proyecto deniega SNS allí (TK-091).
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = local.default_tags
  }
}
