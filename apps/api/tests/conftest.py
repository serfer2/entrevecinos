import os

# `presentation.main` crea la app al importarse; las pruebas necesitan una configuración mínima.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
