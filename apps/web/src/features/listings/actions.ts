"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { invalidBodyFields, membershipStatusOf } from "@/lib/api/errors";
import { isUuid } from "@/lib/forms";

import { imagesChanged, listingChanges } from "./changes";
import {
  ACCESS_MESSAGES,
  EDIT_MESSAGES,
  type ListingFormState,
  listingFieldErrors,
  listingFormValues,
  lockedMessage,
} from "./form";
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

/** Guarda los cambios de un anuncio propio (`listingId` se enlaza con `bind`). */
export async function updateListing(
  listingId: string,
  _state: ListingFormState,
  formData: FormData,
): Promise<ListingFormState> {
  await requireUser();
  if (!isUuid(listingId)) return { formError: EDIT_MESSAGES.forbidden };

  const values = listingFormValues(formData);
  const parsed = listingSchema.safeParse(values);
  if (!parsed.success) return { fieldErrors: fieldErrorsOf<ListingField>(parsed.error), values };

  // Se compara con el anuncio guardado, no con valores que envíe el navegador.
  const current = await userApiFetch<ApiListing>(`/listings/${listingId}`);
  if (!current.ok) return { formError: EDIT_MESSAGES.forbidden, values };

  const changes = listingChanges(current.data, parsed.data);
  if (Object.keys(changes).length > 0) {
    const result = await userApiFetch<ApiListing>(`/listings/${listingId}`, { method: "PATCH", body: changes });
    if (!result.ok) {
      const { status } = result.error;
      if (status === 403) return { formError: lockedMessage(result.error) ?? EDIT_MESSAGES.forbidden, values };
      if (status === 422) {
        const fieldErrors = listingFieldErrors(invalidBodyFields(result.error));
        if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
      }
      return { formError: EDIT_MESSAGES.error, values };
    }
  }

  if (imagesChanged(current.data, parsed.data.image_asset_ids)) {
    const images = parsed.data.image_asset_ids.map((asset_id, index) => ({ asset_id, is_cover: index === 0 }));
    const result = await userApiFetch<ApiListing>(`/listings/${listingId}/images`, {
      method: "PUT",
      body: { images },
    });
    if (!result.ok) {
      const saved = Object.keys(changes).length > 0;
      if (result.error.status === 400 && !saved) {
        return { fieldErrors: { image_asset_ids: LISTING_MESSAGES.image_asset_ids }, values };
      }
      return { formError: saved ? EDIT_MESSAGES.partial : EDIT_MESSAGES.error, values };
    }
  }

  revalidatePath(`/anuncios/${listingId}`);
  revalidatePath(`/comunidades/${current.data.community_id}`);
  redirect(`/anuncios/${listingId}?actualizado=1`);
}
