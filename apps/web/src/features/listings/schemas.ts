import { z } from "zod";

import { MAX_LISTING_IMAGES } from "@/lib/media";

import { LISTING_TYPES } from "./labels";

export const LISTING_MESSAGES = {
  title: "El título es obligatorio.",
  title_max: "Máximo 160 caracteres.",
  description: "La descripción es obligatoria.",
  description_max: "Máximo 5000 caracteres.",
  category_id: "Elige una categoría.",
  type: "Elige el tipo de anuncio.",
  price: "Introduce un precio válido.",
  image_asset_ids: "Alguna fotografía no es válida. Vuelve a subirla.",
} as const;

/** «12,50» o «12.5» → «12.50»; vacío → null. Se envía como texto para no perder precisión. */
const price = z
  .string()
  .trim()
  .transform((value) => value.replace(",", "."))
  .refine((value) => value === "" || /^\d{1,8}(\.\d{1,2})?$/.test(value), {
    error: LISTING_MESSAGES.price,
  })
  .transform((value) => (value === "" ? null : Number(value).toFixed(2)));

/** Mismas reglas que `ListingCreateRequest` en la API. */
export const listingSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, { error: LISTING_MESSAGES.title })
    .max(160, { error: LISTING_MESSAGES.title_max }),
  description: z
    .string()
    .trim()
    .min(1, { error: LISTING_MESSAGES.description })
    .max(5000, { error: LISTING_MESSAGES.description_max }),
  category_id: z.uuid({ error: LISTING_MESSAGES.category_id }),
  type: z.enum(LISTING_TYPES, { error: LISTING_MESSAGES.type }),
  price,
  image_asset_ids: z
    .array(z.uuid({ error: LISTING_MESSAGES.image_asset_ids }))
    .max(MAX_LISTING_IMAGES, { error: LISTING_MESSAGES.image_asset_ids }),
});

export type ListingField = keyof z.input<typeof listingSchema>;

/** Cuerpo para la API: `currency` solo si hay precio (el MVP es en euros). */
export function listingBody(data: z.output<typeof listingSchema>) {
  return { ...data, currency: data.price === null ? null : "EUR" };
}
