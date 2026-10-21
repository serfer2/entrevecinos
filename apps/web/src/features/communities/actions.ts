"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { invalidBodyFields } from "@/lib/api/errors";
import { formText, isUuid } from "@/lib/forms";

import { COMMUNITY_FIELD_MESSAGES, type CommunityField, communitySchema } from "./schemas";
import type { ApiCommunity, ApiMembership } from "./types";

export type CommunityFormState =
  | {
      fieldErrors?: Partial<Record<CommunityField, string>>;
      formError?: string;
      values?: Record<CommunityField, string>;
    }
  | undefined;

export async function createCommunity(
  _state: CommunityFormState,
  formData: FormData,
): Promise<CommunityFormState> {
  await requireUser();

  const values = {
    name: formText(formData, "name"),
    description: formText(formData, "description"),
    city: formText(formData, "city"),
    postal_code: formText(formData, "postal_code"),
  };
  const parsed = communitySchema.safeParse(values);
  if (!parsed.success) {
    return { fieldErrors: fieldErrorsOf<CommunityField>(parsed.error), values };
  }

  const result = await userApiFetch<ApiCommunity>("/communities", {
    method: "POST",
    body: parsed.data,
  });

  if (!result.ok) {
    if (result.error.status === 422) {
      const fieldErrors: Partial<Record<CommunityField, string>> = {};
      for (const field of invalidBodyFields(result.error)) {
        if (field in COMMUNITY_FIELD_MESSAGES) {
          fieldErrors[field as CommunityField] = COMMUNITY_FIELD_MESSAGES[field as CommunityField];
        }
      }
      if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
    }
    return { formError: "No se pudo crear la comunidad. Inténtalo de nuevo.", values };
  }

  // Una comunidad nueva queda pendiente hasta que la apruebe un administrador de plataforma.
  if (!result.data.is_active) redirect("/inicio?comunidad-pendiente=1");
  redirect(`/comunidades/${result.data.id}`);
}

export type RequestAccessState = { error?: string } | undefined;

/** Solicita el acceso. Con `201` o `409` la página vuelve a pintar el estado actual. */
export async function requestAccess(
  _state: RequestAccessState,
  formData: FormData,
): Promise<RequestAccessState> {
  await requireUser();

  const communityId = formText(formData, "community_id");
  if (!isUuid(communityId)) return { error: "Esta comunidad ya no está disponible." };

  const result = await userApiFetch<ApiMembership>(`/communities/${communityId}/memberships`, {
    method: "POST",
  });
  if (!result.ok && result.error.status !== 409) {
    if (result.error.status === 404) return { error: "Esta comunidad ya no está disponible." };
    return { error: "No se pudo enviar la solicitud. Inténtalo de nuevo." };
  }

  revalidatePath("/comunidades");
  revalidatePath(`/comunidades/${communityId}`);
  revalidatePath("/inicio");
  return undefined;
}
