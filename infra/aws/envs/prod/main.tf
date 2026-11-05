# Producción de EntreVecinos en AWS (Épica 13). Guía y decisiones: infra/aws/README.md.

module "budget" {
  source = "../../modules/budget"

  monthly_limit_usd = var.monthly_budget_usd
  alert_email       = var.alert_email
}

module "network" {
  source = "../../modules/network"

  availability_zone = var.availability_zone
}

module "storage" {
  source = "../../modules/storage"
}

module "database" {
  source = "../../modules/database"

  availability_zone = module.network.availability_zone
  admin_role_arns   = var.admin_role_arns
  password_version  = var.db_password_version
}

module "domain" {
  source = "../../modules/domain"

  providers = {
    aws           = aws
    aws.us_east_1 = aws.us_east_1
  }

  wait_for_certificate_validation = var.wait_for_certificate_validation
}

module "mail" {
  source = "../../modules/mail"

  domain  = module.domain.domain
  zone_id = module.domain.zone_id

  test_recipients    = var.ses_test_recipients
  jwt_secret_version = var.jwt_secret_version
}
