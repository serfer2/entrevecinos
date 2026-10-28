"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { fieldErrorsOf } from "@/features/auth/schemas";
import { invalidBodyFields, membershipStatusOf } from "@/lib/api/errors";
import { formText, isUuid } from "@/lib/forms";

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

const AUTHOR_STATUS_RESULTS = { reserved: "reservado", active: "disponible", completed: "finalizado" } as const;

/** El autor reserva, quita la reserva o finaliza su anuncio, y vuelve al detalle con el resultado. */
export async function changeListingStatus(formData: FormData): Promise<void> {
  await requireUser();
  const listingId = formText(formData, "listing_id");
  const status = formText(formData, "status");
  if (!isUuid(listingId)) redirect("/inicio");
  if (!(status in AUTHOR_STATUS_RESULTS)) redirect(`/anuncios/${listingId}?error=estado`);

  const result = await userApiFetch<ApiListing>(`/listings/${listingId}/status`, {
    method: "PATCH",
    body: { status },
  });
  if (result.ok) {
    revalidatePath(`/anuncios/${listingId}`);
    revalidatePath(`/comunidades/${result.data.community_id}`);
    redirect(`/anuncios/${listingId}?cambio=${AUTHOR_STATUS_RESULTS[status as keyof typeof AUTHOR_STATUS_RESULTS]}`);
  }
  const code = result.error.status;
  if (code === 404) redirect("/inicio?no-disponible=1");
  if (code === 403) redirect(`/anuncios/${listingId}?error=estado-permiso`);
  if (code === 409) redirect(`/anuncios/${listingId}?error=estado-conflicto`);
  redirect(`/anuncios/${listingId}?error=estado`);
}

/**
 * Retira (`hidden`) o restaura (`active`) un anuncio por moderación. Al retirar vuelve a la
 * comunidad; al restaurar se queda en el detalle. Los errores llegan por la URL.
 */
export async function moderateListing(formData: FormData): Promise<void> {
  await requireUser();
  const listingId = formText(formData, "listing_id");
  const status = formText(formData, "status");
  if (!isUuid(listingId)) redirect("/inicio");
  if (status !== "hidden" && status !== "active") redirect(`/anuncios/${listingId}?error=moderar`);

  const result = await userApiFetch<ApiListing>(`/listings/${listingId}/status`, {
    method: "PATCH",
    body: { status },
  });
  if (result.ok) {
    const community = `/comunidades/${result.data.community_id}`;
    revalidatePath(community);
    revalidatePath(`/anuncios/${listingId}`);
    redirect(status === "hidden" ? `${community}?ocultado=1` : `/anuncios/${listingId}?restaurado=1`);
  }
  const { status: code } = result.error;
  if (code === 404) redirect("/inicio?no-disponible=1");
  if (code === 403) redirect(`/anuncios/${listingId}?error=moderar-permiso`);
  if (code === 409) redirect(`/anuncios/${listingId}?error=moderar-estado`);
  redirect(`/anuncios/${listingId}?error=moderar`);
}

/** Elimina un anuncio propio y vuelve a su comunidad (el destino sale del anuncio, no del formulario). */
export async function deleteListing(formData: FormData): Promise<void> {
  await requireUser();
  const listingId = formText(formData, "listing_id");
  if (!isUuid(listingId)) redirect("/inicio");

  const current = await userApiFetch<ApiListing>(`/listings/${listingId}`);
  if (!current.ok) {
    if (current.error.status === 404) redirect("/inicio?no-disponible=1");
    redirect(`/anuncios/${listingId}?error=eliminar-permiso`);
  }
  const community = `/comunidades/${current.data.community_id}`;

  const result = await userApiFetch<null>(`/listings/${listingId}`, { method: "DELETE" });
  if (result.ok || result.error.status === 404) {
    revalidatePath(community);
    redirect(result.ok ? `${community}?eliminado=1` : `${community}?no-disponible=1`);
  }
  if (result.error.status === 403) redirect(`/anuncios/${listingId}?error=eliminar-permiso`);
  redirect(`/anuncios/${listingId}?error=eliminar`);
}
