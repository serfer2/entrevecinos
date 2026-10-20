import Link from "next/link";

import { AutoSubmitSelect } from "@/components/ui/AutoSubmitSelect";
import { GetForm } from "@/components/ui/GetForm";

import { LISTING_TYPE_LABELS, LISTING_TYPES } from "../labels";
import {
  clearFiltersHref,
  clearSearchHref,
  hasFilters,
  isPriceOrder,
  LISTING_ORDERS,
  type ListingSearchParams,
  MAX_QUERY_LENGTH,
  MIN_QUERY_LENGTH,
  SHORT_QUERY_MESSAGE,
} from "../search-params";
import type { ApiCategory } from "../types";

type ListingFiltersProps = {
  communityId: string;
  search: ListingSearchParams;
  categories: ApiCategory[];
};

/**
 * Búsqueda y filtros del listado en un único formulario GET: la URL refleja lo elegido y funciona
 * sin JavaScript («Aplicar»); con JavaScript, cambiar un desplegable aplica el filtro al momento.
 */
export function ListingFilters({ communityId, search, categories }: ListingFiltersProps) {
  const errorId = "listing-search-error";
  const typeLabel = search.type ? LISTING_TYPE_LABELS[search.type] : null;
  const categoryLabel = categories.find((c) => c.id === search.categoryId)?.name ?? null;

  return (
    <GetForm role="search" action={`/comunidades/${communityId}`} className="flex flex-col gap-3">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr_auto] lg:items-end">
        <div className="flex min-w-0 flex-col gap-1">
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
        <AutoSubmitSelect
          name="type"
          label="Tipo"
          placeholder="Todos los tipos"
          options={LISTING_TYPES.map((value) => ({ value, label: LISTING_TYPE_LABELS[value] }))}
          defaultValue={search.type}
        />
        <AutoSubmitSelect
          name="category_id"
          label="Categoría"
          placeholder="Todas las categorías"
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
          defaultValue={search.categoryId}
        />
        <AutoSubmitSelect
          name="orden"
          label="Ordenar por"
          options={Object.entries(LISTING_ORDERS).map(([value, { label }]) => ({ value, label }))}
          defaultValue={search.order}
          aria-describedby={isPriceOrder(search.order) ? "listing-order-note" : undefined}
        />
        <button type="submit" className="rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800">
          Aplicar
        </button>
      </div>
      {search.qTooShort && (
        <p id={errorId} className="text-sm text-red-700">
          {SHORT_QUERY_MESSAGE}
        </p>
      )}
      {isPriceOrder(search.order) && (
        <p id="listing-order-note" className="text-sm text-gray-600">
          Los anuncios sin precio aparecen al final.
        </p>
      )}
      {(search.qInput || hasFilters(search)) && (
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
          {hasFilters(search) && (
            <span className="text-gray-700">
              Filtros activos: {[typeLabel, categoryLabel].filter(Boolean).join(" · ")}
            </span>
          )}
          {hasFilters(search) && (
            <Link href={clearFiltersHref(communityId, search)} className="font-medium text-emerald-800 underline">
              Limpiar filtros
            </Link>
          )}
          {search.qInput && (
            <Link href={clearSearchHref(communityId, search)} className="font-medium text-emerald-800 underline">
              Limpiar búsqueda
            </Link>
          )}
        </div>
      )}
    </GetForm>
  );
}
