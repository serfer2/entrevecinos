## Context

TK-060 dejó preparados los huecos: `emailNotVerified` en el inicio de sesión y el `email` en la página de enlace caducado.

## Decisions

- **Un solo componente cliente con `useActionState`**, con la acción por *props* como el resto de formularios.
- **Fuera del formulario de registro o de inicio de sesión:** HTML no admite formularios anidados.
- **`key` con el correo:** si el usuario lo cambia y vuelve a enviar, el botón empieza de cero.
- **Tras el envío el botón se oculta** para evitar reenvíos en bucle; el límite real lo pone la API.
