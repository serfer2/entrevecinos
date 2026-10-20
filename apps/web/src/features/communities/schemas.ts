import { z } from "zod";

export const COMMUNITY_MESSAGES = {
  name: "El nombre de la comunidad es obligatorio.",
  name_max: "Máximo 120 caracteres.",
  description_max: "Máximo 2000 caracteres.",
  city_max: "Máximo 120 caracteres.",
  postal_code_max: "Máximo 16 caracteres.",
} as const;

const optional = (max: number, message: string) =>
  z
    .string()
    .trim()
    .max(max, { error: message })
    .transform((value) => value || null);

/** Mismas reglas que `CommunityCreateRequest` en la API. */
export const communitySchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, { error: COMMUNITY_MESSAGES.name })
    .max(120, { error: COMMUNITY_MESSAGES.name_max }),
  description: optional(2000, COMMUNITY_MESSAGES.description_max),
  city: optional(120, COMMUNITY_MESSAGES.city_max),
  postal_code: optional(16, COMMUNITY_MESSAGES.postal_code_max),
});

export type CommunityField = keyof z.input<typeof communitySchema>;

/** Mensaje mostrado cuando la API rechaza un campo con 422. */
export const COMMUNITY_FIELD_MESSAGES: Record<CommunityField, string> = {
  name: COMMUNITY_MESSAGES.name,
  description: COMMUNITY_MESSAGES.description_max,
  city: COMMUNITY_MESSAGES.city_max,
  postal_code: COMMUNITY_MESSAGES.postal_code_max,
};
