export const LISTING_TYPES = ["sell", "wanted", "offer_service", "need_service", "free", "other"] as const;

export type ListingType = (typeof LISTING_TYPES)[number];

/** Etiquetas de los tipos de anuncio (README §1.2). */
export const LISTING_TYPE_LABELS: Record<ListingType, string> = {
  sell: "Vendo",
  wanted: "Busco",
  offer_service: "Ofrezco",
  need_service: "Necesito",
  free: "Regalo",
  other: "Otros",
};
