output "volume_id" {
  description = "Volumen de datos de PostgreSQL; lo adjunta la instancia (TK-085)."
  value       = aws_ebs_volume.postgres.id
}

output "volume_arn" {
  description = "ARN del volumen de datos."
  value       = aws_ebs_volume.postgres.arn
}

output "backups_bucket" {
  description = "Bucket de las copias de pg_dump (BACKUP_BUCKET de backup.sh)."
  value       = module.backups_bucket.id
}

output "backups_bucket_arn" {
  description = "ARN del bucket de copias."
  value       = module.backups_bucket.arn
}

output "parameter_prefix" {
  description = "Prefijo de los parámetros de PostgreSQL en Parameter Store."
  value       = "/entrevecinos/prod/db/"
}
