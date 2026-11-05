# Red mínima de producción (TK-079): una subred pública para la instancia, sin NAT. La base de
# datos vive en la red interna de Compose (TK-082), así que no hay subredes privadas.

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "entrevecinos-prod" }
}

# Sin reglas: nada usa el grupo por defecto y así no permite ningún tráfico.
resource "aws_default_security_group" "this" {
  vpc_id = aws_vpc.this.id

  tags = { Name = "entrevecinos-prod-default" }
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.public_subnet_cidr
  availability_zone = var.availability_zone
  # La IP pública se pide al crear la instancia (TK-085), no por defecto en la subred.
  map_public_ip_on_launch = false

  tags = { Name = "entrevecinos-prod-public-${substr(var.availability_zone, -1, 1)}" }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = { Name = "entrevecinos-prod" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = { Name = "entrevecinos-prod-public" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Endpoint gateway (gratuito): el tráfico a S3, incluidas las copias de TK-082, no sale a Internet.
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${data.aws_region.current.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.public.id]

  tags = { Name = "entrevecinos-prod-s3" }
}

data "aws_region" "current" {}

# Rangos de CloudFront hacia los orígenes. Cuenta como ~55 reglas del grupo de seguridad.
data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

resource "aws_security_group" "app" {
  #checkov:skip=CKV2_AWS_5:se adjunta a la instancia en TK-085
  name        = "entrevecinos-prod-app"
  description = "Instancia de aplicacion: HTTP solo desde CloudFront, salida HTTPS"
  vpc_id      = aws_vpc.this.id

  tags = { Name = "entrevecinos-prod-app" }
}

resource "aws_vpc_security_group_ingress_rule" "http_from_cloudfront" {
  #checkov:skip=CKV_AWS_260:el origen es la prefix list de CloudFront, no 0.0.0.0/0
  security_group_id = aws_security_group.app.id
  description       = "HTTP desde CloudFront"
  prefix_list_id    = data.aws_ec2_managed_prefix_list.cloudfront.id
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}

# ECR, SSM y Parameter Store, SES, CloudWatch y S3. La hora (169.254.169.123) y el DNS de la VPC
# no pasan por el grupo de seguridad.
resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.app.id
  description       = "HTTPS hacia los servicios de AWS"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/entrevecinos/prod/vpc-flow-logs"
  retention_in_days = 7
}

data "aws_iam_policy_document" "flow_logs_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

data "aws_caller_identity" "current" {}

resource "aws_iam_role" "flow_logs" {
  name               = "entrevecinos-prod-vpc-flow-logs"
  assume_role_policy = data.aws_iam_policy_document.flow_logs_assume.json
}

data "aws_iam_policy_document" "flow_logs" {
  statement {
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
    ]
    resources = ["${aws_cloudwatch_log_group.flow_logs.arn}:*"]
  }
}

resource "aws_iam_role_policy" "flow_logs" {
  name   = "write-flow-logs"
  role   = aws_iam_role.flow_logs.id
  policy = data.aws_iam_policy_document.flow_logs.json
}

# Solo tráfico rechazado: basta para detectar intentos de acceso y cuesta céntimos.
resource "aws_flow_log" "this" {
  vpc_id          = aws_vpc.this.id
  traffic_type    = "REJECT"
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  iam_role_arn    = aws_iam_role.flow_logs.arn

  tags = { Name = "entrevecinos-prod" }
}
