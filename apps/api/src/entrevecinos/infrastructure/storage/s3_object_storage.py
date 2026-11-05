import boto3
from botocore.config import Config


class S3ObjectStorage:
    """Almacenamiento compatible con S3 (MinIO en local, S3 gestionado en producción).

    Sube por el endpoint interno y firma con el público: la firma incluye el host que abrirá
    el navegador, así que una URL firmada con `http://storage:9000` no serviría fuera de Docker.

    En AWS no hay endpoints ni claves: boto3 usa el de la región y las credenciales temporales
    del rol de la instancia (cadena de credenciales por defecto).
    """

    def __init__(
        self,
        endpoint: str,
        public_endpoint: str,
        bucket: str,
        access_key: str = "",
        secret_key: str = "",
        region: str = "us-east-1",
        addressing_style: str = "path",
    ) -> None:
        self._bucket = bucket
        options: dict = {
            "region_name": region,
            "config": Config(signature_version="s3v4", s3={"addressing_style": addressing_style}),
        }
        if access_key:
            options |= {"aws_access_key_id": access_key, "aws_secret_access_key": secret_key}
        self._client = boto3.client("s3", endpoint_url=endpoint or None, **options)
        self._signer = (
            boto3.client("s3", endpoint_url=public_endpoint, **options)
            if public_endpoint and public_endpoint != endpoint
            else self._client
        )

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)

    def presigned_get_url(self, key: str, expires_in: int) -> str:
        return self._signer.generate_presigned_url(
            "get_object", Params={"Bucket": self._bucket, "Key": key}, ExpiresIn=expires_in
        )
