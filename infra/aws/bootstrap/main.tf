# Bucket del estado de Terraform de infra/aws/envs/prod (TK-078). Se aplica una sola vez,
# con estado local (bootstrap/terraform.tfstate, fuera del repositorio).

terraform {
  required_version = ">= 1.11"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.71.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"

  default_tags {
    tags = {
      Project     = "entrevecinos"
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

module "state_bucket" {
  source = "../modules/private-bucket"

  name                    = "entrevecinos-tfstate-${data.aws_caller_identity.current.account_id}"
  noncurrent_version_days = 90
}

output "state_bucket" {
  description = "Bucket del estado; coincide con envs/prod/backend.tf."
  value       = module.state_bucket.id
}
