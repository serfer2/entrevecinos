/** Motivos por los que un enlace para restablecer la contraseña no sirve (TK-104). */
export type PasswordResetLinkError = "invalido" | "caducado";

export const PASSWORD_RESET_LINK_MESSAGES: Record<PasswordResetLinkError, string> = {
  invalido:
    "El enlace para restablecer la contraseña no es válido. Puede que ya lo hayas usado o que hayas pedido otro más reciente.",
  caducado: "El enlace para restablecer la contraseña ha caducado.",
};

export function isPasswordResetLinkError(value: unknown): value is PasswordResetLinkError {
  return typeof value === "string" && value in PASSWORD_RESET_LINK_MESSAGES;
}
