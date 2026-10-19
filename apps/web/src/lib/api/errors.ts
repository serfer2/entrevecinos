export type ValidationIssue = {
  loc: (string | number)[];
  msg: string;
  type: string;
};

/** Error devuelto por la API (`status: 0` si no hubo respuesta). */
export type ApiError = {
  status: number;
  detail: string | ValidationIssue[] | null;
};

/** Campos del cuerpo señalados por un 422 de FastAPI (`loc: ["body", "<campo>"]`). */
export function invalidBodyFields(error: ApiError): string[] {
  if (!Array.isArray(error.detail)) return [];
  return error.detail
    .filter((issue) => issue.loc[0] === "body" && typeof issue.loc[1] === "string")
    .map((issue) => issue.loc[1] as string);
}
