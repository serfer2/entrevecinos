"use client";

import { useActionState } from "react";

import { TextAreaField } from "@/components/ui/TextAreaField";
import { TextField } from "@/components/ui/TextField";

import type { CommunityFormState } from "../actions";

type CommunityFormProps = {
  action: (state: CommunityFormState, formData: FormData) => Promise<CommunityFormState>;
};

export function CommunityForm({ action }: CommunityFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const errors = state?.fieldErrors ?? {};
  const values = state?.values;

  return (
    <form action={formAction} className="flex flex-col gap-4">
      {state?.formError && (
        <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.formError}
        </p>
      )}
      <TextField
        name="name"
        label="Nombre de la comunidad"
        required
        maxLength={120}
        hint="Por ejemplo, el nombre de tu urbanización o barrio."
        defaultValue={values?.name}
        error={errors.name}
      />
      <TextAreaField
        name="description"
        label="Descripción (opcional)"
        maxLength={2000}
        defaultValue={values?.description}
        error={errors.description}
      />
      <TextField
        name="city"
        label="Ciudad (opcional)"
        autoComplete="address-level2"
        maxLength={120}
        defaultValue={values?.city}
        error={errors.city}
      />
      <TextField
        name="postal_code"
        label="Código postal (opcional)"
        autoComplete="postal-code"
        inputMode="numeric"
        maxLength={16}
        defaultValue={values?.postal_code}
        error={errors.postal_code}
      />
      <button
        type="submit"
        disabled={pending}
        className="self-start rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? "Creando…" : "Crear comunidad"}
      </button>
    </form>
  );
}
