"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { requireUser } from "@/features/auth/dal";
import { SESSION_EXPIRED_PATH } from "@/features/auth/routes";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { getSessionToken } from "@/features/auth/session";
import type { ApiUser } from "@/features/auth/types";
import { invalidBodyFields } from "@/lib/api/errors";
import { apiFetch } from "@/lib/api/server";

import { PROFILE_MESSAGES, type ProfileField, profileSchema } from "./schemas";

export type ProfileState =
  | {
      fieldErrors?: Partial<Record<ProfileField, string>>;
      formError?: string;
      success?: string;
      /** Lo que escribió el usuario, para conservarlo en el formulario. */
      values?: { full_name: string; phone: string };
    }
  | undefined;

function text(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

export async function updateProfile(
  _state: ProfileState,
  formData: FormData,
): Promise<ProfileState> {
  // La acción comprueba la sesión por sí misma: no basta con que la página esté protegida.
  await requireUser();
  const token = await getSessionToken();

  const values = { full_name: text(formData, "full_name"), phone: text(formData, "phone") };
  const parsed = profileSchema.safeParse(values);
  if (!parsed.success) {
    return { fieldErrors: fieldErrorsOf<ProfileField>(parsed.error), values };
  }

  const result = await apiFetch<ApiUser>("/users/me", {
    method: "PATCH",
    body: parsed.data,
    token,
  });

  if (!result.ok) {
    if (result.error.status === 401) redirect(SESSION_EXPIRED_PATH);
    if (result.error.status === 422) {
      const fieldErrors: Partial<Record<ProfileField, string>> = {};
      for (const field of invalidBodyFields(result.error)) {
        if (field === "full_name") fieldErrors.full_name = PROFILE_MESSAGES.full_name;
        if (field === "phone") fieldErrors.phone = PROFILE_MESSAGES.phone;
      }
      if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
    }
    return { formError: "No se pudieron guardar los cambios. Inténtalo de nuevo.", values };
  }

  revalidatePath("/perfil");
  return {
    success: "Perfil actualizado.",
    values: { full_name: result.data.full_name, phone: result.data.phone ?? "" },
  };
}
