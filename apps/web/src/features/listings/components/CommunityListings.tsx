import Link from "next/link";

import { Pagination } from "@/components/ui/Pagination";
import { getMyMemberships } from "@/features/communities/data";

import { getCategories, getCommunityListings } from "../data";
import {
  clearFiltersHref,
  clearSearchHref,
  hasFilters,
  type ListingSearchParams,
  listingSearchHref,
} from "../search-params";
import { CommunitySwitcher } from "./CommunitySwitcher";
import { ListingCard } from "./ListingCard";
import { ListingFilters } from "./ListingFilters";

type CommunityListingsProps = {
  communityId: string;
  search: ListingSearchParams;
};

/** Anuncios visibles de la comunidad (solo para miembros aprobados), con búsqueda y filtros. */
export async function CommunityListings({ communityId, search }: CommunityListingsProps) {
  const [listings, categories, memberships] = await Promise.all([
    getCommunityListings(communityId, search),
    getCategories(),
    getMyMemberships(),
  ]);
  const searching = search.q !== "";
  const filtering = hasFilters(search);
  const myCommunities = memberships.filter((m) => m.status === "approved").map((m) => m.community);

  const controls = (
    <div className="flex flex-col gap-3">
      <CommunitySwitcher currentId={communityId} communities={myCommunities} search={search} />
      <ListingFilters communityId={communityId} search={search} categories={categories} />
    </div>
  );

  if (listings.total === 0 && !searching && !filtering) {
    return (
      <div className="flex flex-col gap-4">
        {controls}
        <div className="flex flex-col items-start gap-3 rounded-lg border border-dashed border-gray-300 p-6">
          <p className="text-gray-700">Todavía no hay anuncios en esta comunidad.</p>
          <Link
            href={`/comunidades/${communityId}/anuncios/nuevo`}
            className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
          >
            Publica el primero
          </Link>
        </div>
      </div>
    );
  }

  let summary: string | null = null;
  if (listings.total === 0) {
    summary = filtering ? "No hay anuncios con estos filtros." : `No hay anuncios que coincidan con "${search.q}".`;
  } else if (searching) {
    summary = `${listings.total} ${listings.total === 1 ? "resultado" : "resultados"} para "${search.q}"`;
  }

  return (
    <section aria-labelledby="listings-title" className="flex flex-col gap-4">
      <h2 id="listings-title" className="sr-only">
        Anuncios
      </h2>
      {controls}
      <p aria-live="polite" className={summary ? "text-sm text-gray-700" : "sr-only"}>
        {summary}
      </p>
      {listings.total === 0 && (
        <Link
          href={filtering ? clearFiltersHref(communityId, search) : clearSearchHref(communityId, search)}
          className="self-start font-medium text-emerald-800 underline"
        >
          {filtering ? "Limpiar filtros" : "Ver todos los anuncios"}
        </Link>
      )}
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
