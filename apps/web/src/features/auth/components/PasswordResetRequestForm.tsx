"use client";

import Link from "next/link";
import { useActionState } from "react";

import { TextField } from "@/components/ui/TextField";

import type { PasswordResetRequestState } from "../actions";
import { LOGIN_PATH } from "../routes";

type PasswordResetRequestFormProps = {
  action: (
    state: PasswordResetRequestState,
    formData: FormData,
  ) => Promise<PasswordResetRequestState>;
  /** Correo con el que rellenar el campo (el del intento de inicio de sesión). */
  defaultEmail?: string;
};

const linkClass = "font-medium text-emerald-800 underline";

export function PasswordResetRequestForm({ action, defaultEmail }: PasswordResetRequestFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);

  if (state?.sent) {
    // El mismo aviso exista o no la cuenta: no revela qué correos están registrados.
    return (
      <div
        role="status"
        className="flex flex-col gap-2 rounded-lg bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
      >
        <p>
          Si hay una cuenta con ese correo, te hemos enviado un enlace para restablecer la
          contraseña. Caduca en 1 hora.
        </p>
        <p>Si no lo ves, revisa la carpeta de correo no deseado.</p>
        <p>
          <Link href={LOGIN_PATH} className={linkClass}>
            Volver a iniciar sesión
          </Link>
        </p>
      </div>
    );
  }

  return (
    <form action={formAction} className="flex flex-col gap-4">
      {state?.formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.formError}
        </p>
      )}
      <TextField
        name="email"
        label="Correo electrónico"
        type="email"
        autoComplete="email"
        required
        maxLength={320}
        defaultValue={state?.values?.email ?? defaultEmail}
        error={state?.fieldErrors?.email}
      />
      <button
        type="submit"
        disabled={pending}
        className="rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? "Enviando…" : "Enviar enlace"}
      </button>
      <p className="text-center text-sm text-gray-700">
        ¿La recuerdas?{" "}
        <Link href={LOGIN_PATH} className={linkClass}>
          Inicia sesión
        </Link>
      </p>
    </form>
  );
}
