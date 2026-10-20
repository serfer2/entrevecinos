"use server";

import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { invalidBodyFields } from "@/lib/api/errors";
import { formText } from "@/lib/forms";

import { COMMUNITY_FIELD_MESSAGES, type CommunityField, communitySchema } from "./schemas";
import type { ApiCommunity } from "./types";

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

  redirect(`/comunidades/${result.data.id}`);
}
