## 1. Esquema

- [x] 1.1 Modelos `CommunityModel` y `CommunityMembershipModel` registrados en `models/__init__.py`
- [x] 1.2 Migración `0002_create_community` con `downgrade()`

## 2. Pruebas y verificación

- [x] 2.1 Pruebas `db`: valores por defecto, PK compuesta, `CHECK` de nombre y de `approved`
- [x] 2.2 `alembic check`, `downgrade 0001`/`upgrade head` y verificación TK-012 §6
