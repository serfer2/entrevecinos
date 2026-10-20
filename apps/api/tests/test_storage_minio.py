"""Prueba de extremo a extremo contra el MinIO del entorno (`pytest -m storage`)."""

import os
import urllib.request
import uuid

import pytest

from entrevecinos.infrastructure.storage.s3_object_storage import S3ObjectStorage
from tests.images import PNG

pytestmark = pytest.mark.storage


def test_upload_and_download_with_presigned_url() -> None:
    endpoint = os.environ["STORAGE_ENDPOINT"]
    # Dentro de Docker el host público (localhost) no es accesible: se firma con el interno.
    storage = S3ObjectStorage(
        endpoint,
        endpoint,
        os.environ["STORAGE_BUCKET"],
        os.environ["STORAGE_ACCESS_KEY"],
        os.environ["STORAGE_SECRET_KEY"],
    )
    key = f"tests/{uuid.uuid4()}.png"
    storage.put(key, PNG, "image/png")

    with urllib.request.urlopen(storage.presigned_get_url(key, 60)) as response:  # noqa: S310
        assert response.read() == PNG
        assert response.headers["Content-Type"] == "image/png"

    storage._client.delete_object(Bucket=os.environ["STORAGE_BUCKET"], Key=key)


def test_public_endpoint_is_used_for_signing() -> None:
    storage = S3ObjectStorage("http://storage:9000", "http://localhost:9000", "b", "k", "s")

    assert storage.presigned_get_url("media/x.png", 300).startswith("http://localhost:9000/b/")
