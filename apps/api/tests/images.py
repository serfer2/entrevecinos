"""Cabeceras mínimas de imágenes para las pruebas (el contenido real no importa)."""

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 64
PDF = b"%PDF-1.7\n" + b"\x00" * 64
GIF = b"GIF89a" + b"\x00" * 64
