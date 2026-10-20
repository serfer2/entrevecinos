## 1. Categorías

- [x] 1.1 `CategoryRepository` y `GET /v1/categories`

## 2. Publicación

- [x] 2.1 Dominio `listings` (`normalize_price`, errores) y `PublishListing` con pruebas unitarias
- [x] 2.2 `ListingRepository` (anuncio + imágenes en una transacción; lectura sin N+1) y `MediaRepository.owned_unattached`
- [x] 2.3 Esquemas, `ListingResponse` y `POST /v1/communities/{id}/listings`

## 3. Contrato, pruebas y verificación

- [x] 3.1 `ListingCreate`/`ListingUpdate`: `maxLength: 5000` y `EUR` por defecto; lint
- [x] 3.2 Integración AC1–AC5 y verificación TK-022 §6
