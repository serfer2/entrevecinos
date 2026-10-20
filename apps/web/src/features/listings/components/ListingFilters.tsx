import Link from "next/link";

import {
  clearSearchHref,
  type ListingSearchParams,
  MAX_QUERY_LENGTH,
  MIN_QUERY_LENGTH,
  SHORT_QUERY_MESSAGE,
} from "../search-params";

type ListingFiltersProps = {
  communityId: string;
  search: ListingSearchParams;
};

/** Buscador del listado: formulario GET, así la URL refleja la búsqueda y funciona sin JavaScript. */
export function ListingFilters({ communityId, search }: ListingFiltersProps) {
  const errorId = "listing-search-error";

  return (
    <form method="get" role="search" action={`/comunidades/${communityId}`} className="flex flex-col gap-2">
      <div className="flex flex-wrap items-end gap-2">
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <label htmlFor="listing-search" className="text-sm font-medium text-gray-900">
            Buscar anuncios
          </label>
          <input
            id="listing-search"
            type="search"
            name="q"
            minLength={MIN_QUERY_LENGTH}
            maxLength={MAX_QUERY_LENGTH}
            defaultValue={search.qInput}
            aria-invalid={search.qTooShort ? true : undefined}
            aria-describedby={search.qTooShort ? errorId : undefined}
            className="rounded-md border border-gray-300 px-3 py-2 text-base text-gray-900 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 aria-invalid:border-red-600"
          />
        </div>
        <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800">
          Buscar
        </button>
        {search.qInput && (
          <Link
            href={clearSearchHref(communityId, search)}
            className="rounded-md border border-gray-300 px-4 py-2 font-medium text-gray-800 hover:bg-gray-50"
          >
            Limpiar
          </Link>
        )}
      </div>
      {search.qTooShort && (
        <p id={errorId} className="text-sm text-red-700">
          {SHORT_QUERY_MESSAGE}
        </p>
      )}
    </form>
  );
}
