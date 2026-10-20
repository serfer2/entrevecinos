import Link from "next/link";

import { formatPrice, formatPublishedAt } from "@/lib/format";
import { mediaSrc } from "@/lib/media";

import { LISTING_TYPE_LABELS } from "../labels";
import type { ApiListing } from "../types";

/** Precio de un anuncio: el importe, «Gratis» si es un regalo sin precio, o nada. */
export function listingPriceLabel(listing: Pick<ApiListing, "price" | "currency" | "type">): string | null {
  return formatPrice(listing.price, listing.currency) ?? (listing.type === "free" ? "Gratis" : null);
}

export function ListingCard({ listing }: { listing: ApiListing }) {
  const cover = listing.images.find((image) => image.is_cover) ?? listing.images[0];
  const price = listingPriceLabel(listing);

  return (
    <Link
      href={`/anuncios/${listing.id}`}
      className="flex h-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-white hover:border-emerald-600 focus-visible:ring-2 focus-visible:ring-emerald-600"
    >
      <div className="relative aspect-[4/3] bg-gray-100">
        {cover ? (
          // eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición
          <img src={mediaSrc(cover.url)} alt={listing.title} loading="lazy" className="h-full w-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-400">
            <svg aria-hidden viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <circle cx="9" cy="10" r="1.5" />
              <path d="m21 16-5-5-8 8" />
            </svg>
          </div>
        )}
        {listing.status === "reserved" && (
          <span className="absolute left-2 top-2 rounded bg-amber-500 px-2 py-0.5 text-xs font-semibold text-white">
            Reservado
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-1 p-3">
        <span className="text-xs font-medium uppercase tracking-wide text-emerald-800">
          {LISTING_TYPE_LABELS[listing.type]}
        </span>
        <h3 className="line-clamp-2 font-medium text-gray-900">{listing.title}</h3>
        <div className="mt-auto flex items-center justify-between gap-2 pt-1 text-sm">
          <span className="font-semibold text-gray-900">{price}</span>
          <time dateTime={listing.published_at} className="text-gray-600">
            {formatPublishedAt(listing.published_at)}
          </time>
        </div>
      </div>
    </Link>
  );
}
