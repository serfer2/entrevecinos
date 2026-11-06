# Registro de imágenes Docker y bucket privado de las fotografías de los anuncios (TK-080).

resource "aws_ecr_repository" "this" {
  for_each = toset(["api", "web"])

  name                 = "entrevecinos/${each.key}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_lifecycle_policy" "this" {
  for_each = aws_ecr_repository.this

  repository = each.value.name
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Borrar imágenes sin etiqueta a los 7 días"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Conservar las 10 últimas imágenes etiquetadas"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = { type = "expire" }
      },
    ]
  })
}

data "aws_caller_identity" "current" {}

# Las fotografías solo se leen con URL prefirmadas que firma la API: ni CORS ni acceso público.
module "media_bucket" {
  source = "../private-bucket"

  name                    = "entrevecinos-media-${data.aws_caller_identity.current.account_id}"
  noncurrent_version_days = 30
}
