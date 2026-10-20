import { formText } from "@/lib/forms";

import { LISTING_MESSAGES, type ListingField } from "./schemas";

export type ListingFormValues = {
  title: string;
  description: string;
  category_id: string;
  type: string;
  price: string;
  image_asset_ids: string[];
};

export type ListingFormState =
  | {
      fieldErrors?: Partial<Record<ListingField, string>>;
      formError?: string;
      values?: ListingFormValues;
    }
  | undefined;

export type ListingFormAction = (
  state: ListingFormState,
  formData: FormData,
) => Promise<ListingFormState>;

/** Valores enviados por `ListingForm` (las imágenes, en el orden mostrado). */
export function listingFormValues(formData: FormData): ListingFormValues {
  return {
    title: formText(formData, "title"),
    description: formText(formData, "description"),
    category_id: formText(formData, "category_id"),
    type: formText(formData, "type"),
    price: formText(formData, "price"),
    image_asset_ids: formData.getAll("image_asset_ids").filter((v): v is string => typeof v === "string"),
  };
}

const FIELD_MESSAGES: Partial<Record<string, string>> = {
  title: LISTING_MESSAGES.title,
  description: LISTING_MESSAGES.description,
  category_id: LISTING_MESSAGES.category_id,
  type: LISTING_MESSAGES.type,
  price: LISTING_MESSAGES.price,
  currency: LISTING_MESSAGES.price,
  image_asset_ids: LISTING_MESSAGES.image_asset_ids,
};

/** Errores por campo de un 422 de la API. */
export function listingFieldErrors(fields: string[]): Partial<Record<ListingField, string>> {
  const errors: Partial<Record<ListingField, string>> = {};
  for (const field of fields) {
    const key = (field === "currency" ? "price" : field) as ListingField;
    if (FIELD_MESSAGES[field]) errors[key] = FIELD_MESSAGES[field];
  }
  return errors;
}

export const ACCESS_MESSAGES = {
  pending:
    "Tu solicitud está pendiente de aprobación. Podrás publicar cuando un administrador la apruebe.",
  denied: "No tienes acceso para publicar en esta comunidad.",
} as const;
