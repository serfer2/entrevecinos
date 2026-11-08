"use client";

import { useActionState } from "react";

import { TextField } from "@/components/ui/TextField";

import type { PasswordResetState } from "../actions";
import { PasswordResetLinkErrorNotice } from "./PasswordResetLinkError";

type PasswordResetFormProps = {
  action: (state: PasswordResetState, formData: FormData) => Promise<PasswordResetState>;
};

export function PasswordResetForm({ action }: PasswordResetFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const errors = state?.fieldErrors ?? {};

  if (state?.linkError) return <PasswordResetLinkErrorNotice reason={state.linkError} />;

  return (
    <form action={formAction} className="flex flex-col gap-4">
      {state?.formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.formError}
        </p>
      )}
      <TextField
        name="password"
        label="Contraseña nueva"
        type="password"
        autoComplete="new-password"
        required
        minLength={12}
        maxLength={128}
        hint="Mínimo 12 caracteres"
        error={errors.password}
      />
      <TextField
        name="password_confirm"
        label="Repite la contraseña"
        type="password"
        autoComplete="new-password"
        required
        maxLength={128}
        error={errors.password_confirm}
      />
      <button
        type="submit"
        disabled={pending}
        className="rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? "Cambiando…" : "Cambiar contraseña"}
      </button>
    </form>
  );
}
