"use client";

import { useActionState } from "react";

import type { ResendVerificationState } from "../actions";

type ResendVerificationButtonProps = {
  email: string;
  action: (state: ResendVerificationState, formData: FormData) => Promise<ResendVerificationState>;
};

export function ResendVerificationButton({ email, action }: ResendVerificationButtonProps) {
  const [state, formAction, pending] = useActionState(action, undefined);

  // Tras el envío se oculta el botón para no reenviar en bucle (la API también lo limita).
  if (state?.sent) {
    return (
      <p role="status" className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
        Si tu cuenta está pendiente de validación, te hemos enviado un correo nuevo. Revisa tu
        bandeja de entrada.
      </p>
    );
  }

  return (
    <form action={formAction} className="flex flex-col items-start gap-1">
      <input type="hidden" name="email" value={email} />
      <button
        type="submit"
        disabled={pending}
        className="rounded-md border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50 disabled:opacity-60"
      >
        {pending ? "Enviando…" : "Reenviar el correo de validación"}
      </button>
      {state?.error && (
        <p role="alert" className="text-sm text-red-700">
          {state.error}
        </p>
      )}
    </form>
  );
}
