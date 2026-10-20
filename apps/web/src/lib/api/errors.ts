export type ValidationIssue = {
  loc: (string | number)[];
  msg: string;
  type: string;
};

/** Error devuelto por la API (`status: 0` si no hubo respuesta). */
export type ApiError = {
  status: number;
  detail: string | ValidationIssue[] | null;
  /** Cuerpo completo del error (p. ej. `status` de los 403/409 de membresía). */
  payload?: Record<string, unknown> | null;
};

/** Campos del cuerpo señalados por un 422 de FastAPI (`loc: ["body", "<campo>"]`). */
export function invalidBodyFields(error: ApiError): string[] {
  if (!Array.isArray(error.detail)) return [];
  return error.detail
    .filter((issue) => issue.loc[0] === "body" && typeof issue.loc[1] === "string")
    .map((issue) => issue.loc[1] as string);
}

/** `status` de la membresía en un error 403/409 (`MembershipError`), si viene. */
export function membershipStatusOf(error: ApiError): string | null {
  const status = error.payload?.status;
  return typeof status === "string" ? status : null;
}
