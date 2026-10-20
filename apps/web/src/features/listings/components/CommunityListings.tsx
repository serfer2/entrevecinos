import Link from "next/link";

import { Pagination } from "@/components/ui/Pagination";

import { getCommunityListings } from "../data";
import { type ListingSearchParams, listingSearchHref } from "../search-params";
import { ListingCard } from "./ListingCard";

type CommunityListingsProps = {
  communityId: string;
  search: ListingSearchParams;
};

/** Anuncios visibles de la comunidad (solo para miembros aprobados). */
export async function CommunityListings({ communityId, search }: CommunityListingsProps) {
  const listings = await getCommunityListings(communityId, search);

  if (listings.total === 0) {
    return (
      <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-gray-300 p-6">
        <p className="text-gray-700">Todavía no hay anuncios en esta comunidad.</p>
        <Link
          href={`/comunidades/${communityId}/anuncios/nuevo`}
          className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
        >
          Publica el primero
        </Link>
      </div>
    );
  }

  return (
    <section aria-labelledby="listings-title" className="flex flex-col gap-4">
      <h2 id="listings-title" className="sr-only">
        Anuncios
      </h2>
      <ul className="grid grid-cols-1 gap-4 min-[420px]:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {listings.items.map((listing) => (
          <li key={listing.id}>
            <ListingCard listing={listing} />
          </li>
        ))}
      </ul>
      <Pagination
        page={listings.page}
        pageSize={listings.page_size}
        total={listings.total}
        hrefFor={(page) => listingSearchHref(communityId, search, page)}
      />
    </section>
  );
}
