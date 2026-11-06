"use client";

import { useActionState } from "react";

import { TextField } from "@/components/ui/TextField";

import type { ProfileState } from "../actions";

type ProfileFormProps = {
  action: (state: ProfileState, formData: FormData) => Promise<ProfileState>;
  initialValues: { full_name: string; phone: string | null };
};

export function ProfileForm({ action, initialValues }: ProfileFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const errors = state?.fieldErrors ?? {};
  const values = state?.values ?? {
    full_name: initialValues.full_name,
    phone: initialValues.phone ?? "",
  };

  return (
    <form action={formAction} className="flex flex-col gap-4 rounded-2xl border border-gray-200 bg-white p-5 sm:p-6">
      {state?.success && (
        <p role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {state.success}
        </p>
      )}
      {state?.formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.formError}
        </p>
      )}
      <TextField
        name="full_name"
        label="Nombre"
        autoComplete="name"
        required
        maxLength={120}
        defaultValue={values.full_name}
        error={errors.full_name}
      />
      <TextField
        name="phone"
        label="Teléfono"
        type="tel"
        autoComplete="tel"
        maxLength={32}
        hint="Opcional. Tu teléfono y tu correo los verán los vecinos de tus comunidades interesados en tus anuncios."
        defaultValue={values.phone}
        error={errors.phone}
      />
      <button
        type="submit"
        disabled={pending}
        className="self-start rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? "Guardando…" : "Guardar cambios"}
      </button>
    </form>
  );
}
