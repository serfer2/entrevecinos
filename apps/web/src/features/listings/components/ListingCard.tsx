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
      className="group flex h-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white no-underline shadow-xs transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md focus-visible:outline-emerald-600 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
    >
      <div className="relative aspect-[4/3] overflow-hidden bg-gray-100">
        {cover ? (
          // eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición
          <img
            src={mediaSrc(cover.url)}
            alt={listing.title}
            loading="lazy"
            className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.03] motion-reduce:transition-none motion-reduce:group-hover:scale-100"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-emerald-50 text-emerald-300">
            <svg aria-hidden viewBox="0 0 24 24" className="h-10 w-10" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="3" y="5" width="18" height="14" rx="2" />
              <circle cx="9" cy="10" r="1.5" />
              <path d="m21 16-5-5-8 8" />
            </svg>
          </div>
        )}
        <span className="absolute left-2 top-2 rounded-full bg-white/90 px-2.5 py-0.5 text-xs font-semibold text-emerald-900 shadow-xs">
          {LISTING_TYPE_LABELS[listing.type]}
        </span>
        {listing.status === "reserved" && (
          <span className="absolute right-2 top-2 rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-900 shadow-xs">
            Reservado
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        <h3 className="line-clamp-2 font-medium leading-snug text-gray-900 group-hover:text-emerald-900">
          {listing.title}
        </h3>
        <div className="mt-auto flex items-baseline justify-between gap-2">
          <span className="text-lg font-semibold text-emerald-800">{price}</span>
          <time dateTime={listing.published_at} className="text-xs text-gray-600">
            {formatPublishedAt(listing.published_at)}
          </time>
        </div>
      </div>
    </Link>
  );
}
