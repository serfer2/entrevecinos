# Bucket creado por infra/aws/bootstrap (TK-078).
terraform {
  backend "s3" {
    bucket       = "entrevecinos-tfstate-995006761619"
    key          = "prod/terraform.tfstate"
    region       = "eu-north-1"
    encrypt      = true
    use_lockfile = true
  }
}
