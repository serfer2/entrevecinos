import type { z } from "zod";

import type { ListingFormValues } from "./form";
import type { listingSchema } from "./schemas";
import type { ApiListing } from "./types";

type ParsedListing = z.output<typeof listingSchema>;

/** Valores iniciales del formulario a partir del anuncio (precio con coma decimal). */
export function listingFormValuesOf(listing: ApiListing): ListingFormValues {
  return {
    title: listing.title,
    description: listing.description,
    category_id: listing.category_id,
    type: listing.type,
    price: listing.price === null ? "" : listing.price.toFixed(2).replace(".", ","),
    image_asset_ids: [...listing.images].sort((a, b) => a.position - b.position).map((i) => i.asset_id),
  };
}

/** Cuerpo del `PATCH` con solo los campos que cambian (vacío si no hay cambios). */
export function listingChanges(current: ApiListing, next: ParsedListing): Record<string, unknown> {
  const changes: Record<string, unknown> = {};
  for (const field of ["title", "description", "category_id", "type"] as const) {
    if (current[field] !== next[field]) changes[field] = next[field];
  }
  const nextPrice = next.price === null ? null : Number(next.price);
  if (nextPrice !== current.price) {
    changes.price = next.price;
    if (next.price !== null) changes.currency = current.currency ?? "EUR";
  }
  return changes;
}

/** Si el orden de las imágenes o la portada cambian (la portada es siempre la primera elegida). */
export function imagesChanged(current: ApiListing, nextIds: string[]): boolean {
  const ordered = [...current.images].sort((a, b) => a.position - b.position);
  if (ordered.length !== nextIds.length) return true;
  if (ordered.some((image, index) => image.asset_id !== nextIds[index])) return true;
  return ordered.length > 0 && !ordered[0].is_cover;
}
