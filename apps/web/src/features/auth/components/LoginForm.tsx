"use client";

import Link from "next/link";
import { useActionState } from "react";

import { TextField } from "@/components/ui/TextField";

import type { LoginState, ResendVerificationState } from "../actions";
import { ResendVerificationButton } from "./ResendVerificationButton";

type LoginFormProps = {
  action: (state: LoginState, formData: FormData) => Promise<LoginState>;
  resendAction: (
    state: ResendVerificationState,
    formData: FormData,
  ) => Promise<ResendVerificationState>;
  /** Ruta a la que volver tras iniciar sesión (se valida en el servidor). */
  next?: string;
  notice?: string;
};

export function LoginForm({ action, resendAction, next, notice }: LoginFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const errors = state?.fieldErrors ?? {};

  const email = state?.values?.email;

  return (
    <div className="flex flex-col gap-4">
      <form action={formAction} className="flex flex-col gap-4">
        {notice && !state && (
          <p role="status" className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900">
            {notice}
          </p>
        )}
        {state?.formError && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
            {state.formError}
          </p>
        )}
        {next && <input type="hidden" name="next" value={next} />}
        <TextField
          name="email"
          label="Correo electrónico"
          type="email"
          autoComplete="email"
          required
          defaultValue={email}
          error={errors.email}
        />
        <TextField
          name="password"
          label="Contraseña"
          type="password"
          autoComplete="current-password"
          required
          error={errors.password}
        />
        <button
          type="submit"
          disabled={pending}
          className="rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
        >
          {pending ? "Entrando…" : "Iniciar sesión"}
        </button>
        <p className="text-center text-sm text-gray-700">
          ¿No tienes cuenta?{" "}
          <Link href="/registro" className="font-medium text-emerald-800 underline">
            Regístrate
          </Link>
        </p>
      </form>
      {/* Fuera del formulario: no se pueden anidar formularios. */}
      {state?.emailNotVerified && email && (
        <ResendVerificationButton key={email} email={email} action={resendAction} />
      )}
    </div>
  );
}
