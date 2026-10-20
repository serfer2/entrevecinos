## MODIFIED Requirements

### Requirement: Sin solicitudes duplicadas
Si el usuario ya tiene una membresía en la comunidad, en cualquier estado, la solicitud MUST responder `409 {"detail": "Ya tienes una membresía en esta comunidad.", "status": "<estado>"}` sin crear otra. El contrato documenta este cuerpo como `MembershipConflict` (`MembershipError`).

#### Scenario: Ya pendiente
- **WHEN** el usuario vuelve a solicitar el acceso
- **THEN** recibe `409` con `status: "pending"`
