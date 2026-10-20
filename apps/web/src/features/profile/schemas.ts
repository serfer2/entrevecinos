import { z } from "zod";

export const PROFILE_MESSAGES = {
  full_name: "El nombre es obligatorio.",
  full_name_max: "Máximo 120 caracteres.",
  phone: "Introduce un teléfono válido.",
} as const;

/** Mismas reglas que `UserUpdateRequest` en la API. */
export const profileSchema = z.object({
  full_name: z
    .string()
    .trim()
    .min(1, { error: PROFILE_MESSAGES.full_name })
    .max(120, { error: PROFILE_MESSAGES.full_name_max }),
  phone: z
    .string()
    .trim()
    .refine((value) => value === "" || /^\+?[0-9 ()-]{6,32}$/.test(value), {
      error: PROFILE_MESSAGES.phone,
    })
    .transform((value) => value || null),
});

export type ProfileField = keyof z.input<typeof profileSchema>;
