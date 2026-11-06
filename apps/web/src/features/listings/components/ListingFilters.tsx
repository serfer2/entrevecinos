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
    <GetForm
      role="search"
      action={`/comunidades/${communityId}`}
      className="flex flex-col gap-3 rounded-2xl border border-gray-200 bg-white p-4 shadow-xs sm:p-5"
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_auto] lg:items-end">
        <div className="flex min-w-0 flex-col gap-1">
          <label htmlFor="listing-search" className="text-sm font-medium text-gray-900">
            Buscar anuncios
          </label>
          <div className="relative">
            <svg
              aria-hidden
              viewBox="0 0 24 24"
              className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-500"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
            >
              <circle cx="11" cy="11" r="6.5" />
              <path d="m20 20-3.9-3.9" />
            </svg>
            <input
              id="listing-search"
              type="search"
              name="q"
              minLength={MIN_QUERY_LENGTH}
              maxLength={MAX_QUERY_LENGTH}
              defaultValue={search.qInput}
              aria-invalid={search.qTooShort ? true : undefined}
              aria-describedby={search.qTooShort ? errorId : undefined}
              placeholder="Bici, clases, herramientas…"
              className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-3 text-base text-gray-900 placeholder:text-gray-500 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 aria-invalid:border-red-600"
            />
          </div>
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
        <button
          type="submit"
          className="rounded-lg bg-emerald-700 px-5 py-2 font-medium text-white hover:bg-emerald-800 sm:col-span-2 lg:col-span-1"
        >
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
