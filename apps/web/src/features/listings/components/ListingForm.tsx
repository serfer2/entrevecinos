"use client";

import { useActionState, useState } from "react";

import { SelectField } from "@/components/ui/SelectField";
import { TextAreaField } from "@/components/ui/TextAreaField";
import { TextField } from "@/components/ui/TextField";
import { uploadImage } from "@/features/media/actions";
import { ImagePicker } from "@/features/media/components/ImagePicker";

import type { ListingFormAction, ListingFormValues } from "../form";
import { LISTING_TYPE_LABELS, LISTING_TYPES } from "../labels";
import type { ApiCategory } from "../types";

type ListingFormProps = {
  action: ListingFormAction;
  categories: ApiCategory[];
  initialValues?: ListingFormValues;
  submitLabel: string;
  pendingLabel: string;
  /** Al editar, las fotografías se gestionan aparte (TK-025): se puede ocultar el selector. */
  withImages?: boolean;
};

const EMPTY: ListingFormValues = {
  title: "",
  description: "",
  category_id: "",
  type: "",
  price: "",
  image_asset_ids: [],
};

export function ListingForm({
  action,
  categories,
  initialValues = EMPTY,
  submitLabel,
  pendingLabel,
  withImages = true,
}: ListingFormProps) {
  const [state, formAction, pending] = useActionState(action, undefined);
  const [uploading, setUploading] = useState(false);
  const values = state?.values ?? initialValues;
  const errors = state?.fieldErrors ?? {};
  const [type, setType] = useState(values.type);

  return (
    // La clave fuerza a recrear los campos no controlados con los valores devueltos por la acción.
    <form key={JSON.stringify(state?.values ?? null)} action={formAction} className="flex flex-col gap-5">
      {state?.formError && (
        <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
          {state.formError}
        </p>
      )}
      <TextField
        name="title"
        label="Título"
        required
        maxLength={160}
        defaultValue={values.title}
        error={errors.title}
      />
      <TextAreaField
        name="description"
        label="Descripción"
        required
        maxLength={5000}
        rows={6}
        defaultValue={values.description}
        error={errors.description}
      />
      <SelectField
        name="category_id"
        label="Categoría"
        required
        placeholder="Elige una categoría"
        options={categories.map((c) => ({ value: c.id, label: c.name }))}
        defaultValue={values.category_id}
        error={errors.category_id}
      />

      <fieldset
        className="flex flex-col gap-2"
        aria-invalid={errors.type ? true : undefined}
        aria-describedby={errors.type ? "field-type-error" : undefined}
      >
        <legend className="text-sm font-medium text-gray-900">Tipo de anuncio</legend>
        <div className="flex flex-wrap gap-2">
          {LISTING_TYPES.map((value) => (
            <label
              key={value}
              className="flex cursor-pointer items-center gap-2 rounded-md border border-gray-300 px-3 py-1.5 text-sm has-[:checked]:border-emerald-700 has-[:checked]:bg-emerald-50"
            >
              <input
                type="radio"
                name="type"
                value={value}
                required
                defaultChecked={values.type === value}
                onChange={() => setType(value)}
              />
              {LISTING_TYPE_LABELS[value]}
            </label>
          ))}
        </div>
        {errors.type && (
          <p id="field-type-error" className="text-sm text-red-700">
            {errors.type}
          </p>
        )}
      </fieldset>

      <div className="flex items-end gap-2">
        <div className="flex-1">
          <TextField
            name="price"
            label="Precio (opcional)"
            inputMode="decimal"
            maxLength={12}
            hint={type === "free" ? "Normalmente sin precio." : "En euros. Déjalo vacío si no tiene precio."}
            defaultValue={values.price}
            error={errors.price}
          />
        </div>
        <span aria-hidden className="pb-2 text-gray-700">
          €
        </span>
      </div>

      {withImages && (
        <ImagePicker
          upload={uploadImage}
          initialIds={values.image_asset_ids}
          error={errors.image_asset_ids}
          onBusyChange={setUploading}
        />
      )}

      <button
        type="submit"
        disabled={pending || uploading}
        className="self-start rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? pendingLabel : submitLabel}
      </button>
    </form>
  );
}
