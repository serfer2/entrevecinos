"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { invalidBodyFields, membershipStatusOf } from "@/lib/api/errors";
import { isUuid } from "@/lib/forms";

import { ACCESS_MESSAGES, type ListingFormState, listingFieldErrors, listingFormValues } from "./form";
import { LISTING_MESSAGES, type ListingField, listingBody, listingSchema } from "./schemas";
import type { ApiListing } from "./types";

/** Publica un anuncio en `communityId` (se enlaza con `bind`) y vuelve a la comunidad. */
export async function publishListing(
  communityId: string,
  _state: ListingFormState,
  formData: FormData,
): Promise<ListingFormState> {
  await requireUser();
  if (!isUuid(communityId)) return { formError: ACCESS_MESSAGES.denied };

  const values = listingFormValues(formData);
  const parsed = listingSchema.safeParse(values);
  if (!parsed.success) return { fieldErrors: fieldErrorsOf<ListingField>(parsed.error), values };

  const result = await userApiFetch<ApiListing>(`/communities/${communityId}/listings`, {
    method: "POST",
    body: listingBody(parsed.data),
  });

  if (!result.ok) {
    const { status } = result.error;
    if (status === 403) {
      const pending = membershipStatusOf(result.error) === "pending";
      return { formError: pending ? ACCESS_MESSAGES.pending : ACCESS_MESSAGES.denied, values };
    }
    if (status === 400) {
      return { fieldErrors: { image_asset_ids: LISTING_MESSAGES.image_asset_ids }, values };
    }
    if (status === 422) {
      const fieldErrors = listingFieldErrors(invalidBodyFields(result.error));
      if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
    }
    return { formError: "No se pudo publicar el anuncio. Inténtalo de nuevo.", values };
  }

  revalidatePath(`/comunidades/${communityId}`);
  redirect(`/comunidades/${communityId}?publicado=1`);
}
