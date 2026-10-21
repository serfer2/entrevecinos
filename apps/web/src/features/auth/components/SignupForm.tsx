"use client";

import Link from "next/link";
import { useActionState } from "react";

import { TextField } from "@/components/ui/TextField";

import type { ResendVerificationState, SignupState } from "../actions";
import { ResendVerificationButton } from "./ResendVerificationButton";

type SignupFormProps = {
  action: (state: SignupState, formData: FormData) => Promise<SignupState>;
  resendAction: (
    state: ResendVerificationState,
    formData: FormData,
  ) => Promise<ResendVerificationState>;
};

export function SignupForm({ action, resendAction }: SignupFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const errors = state?.fieldErrors ?? {};
  const values = state?.values;

  if (state?.verificationSentTo) {
    return (
      <div
        role="status"
        className="flex flex-col gap-2 rounded-md bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
      >
        <p>
          Te hemos enviado un correo a <strong>{state.verificationSentTo}</strong>. Abre el enlace
          que contiene para activar tu cuenta. El enlace caduca en 24 horas.
        </p>
        <p>Si no lo ves, revisa la carpeta de correo no deseado.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <form action={formAction} className="flex flex-col gap-4">
        {state?.formError && (
          <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
            {state.formError}
          </p>
        )}
        <TextField
          name="full_name"
          label="Nombre"
          autoComplete="name"
          required
          maxLength={120}
          defaultValue={values?.full_name}
          error={errors.full_name}
        />
        <TextField
          name="email"
          label="Correo electrónico"
          type="email"
          autoComplete="email"
          required
          defaultValue={values?.email}
          error={errors.email}
        />
        <TextField
          name="password"
          label="Contraseña"
          type="password"
          autoComplete="new-password"
          required
          minLength={12}
          maxLength={128}
          hint="Mínimo 12 caracteres"
          error={errors.password}
        />
        <TextField
          name="phone"
          label="Teléfono (opcional)"
          type="tel"
          autoComplete="tel"
          maxLength={32}
          defaultValue={values?.phone}
          error={errors.phone}
        />
        <button
          type="submit"
          disabled={pending}
          className="rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
        >
          {pending ? "Creando cuenta…" : "Crear cuenta"}
        </button>
        <p className="text-center text-sm text-gray-700">
          ¿Ya tienes cuenta?{" "}
          <Link href="/iniciar-sesion" className="font-medium text-emerald-800 underline">
            Inicia sesión
          </Link>
        </p>
      </form>
      {/* Fuera del formulario: no se pueden anidar formularios. */}
      {state?.pendingVerification && values?.email && (
        <ResendVerificationButton key={values.email} email={values.email} action={resendAction} />
      )}
    </div>
  );
}
