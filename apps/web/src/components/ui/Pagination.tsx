import Link from "next/link";

type PaginationProps = {
  page: number;
  pageSize: number;
  total: number;
  /** URL de una página concreta (conserva el resto de parámetros). */
  hrefFor: (page: number) => string;
};

const linkClass =
  "rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50";

/** Navegación «Anterior / Siguiente» de un listado paginado. No se muestra con una sola página. */
export function Pagination({ page, pageSize, total, hrefFor }: PaginationProps) {
  const pages = Math.max(1, Math.ceil(total / pageSize));
  if (pages <= 1 && page <= 1) return null;

  return (
    <nav aria-label="Paginación" className="flex items-center justify-between gap-4">
      {page > 1 ? (
        <Link href={hrefFor(Math.min(page - 1, pages))} className={linkClass} rel="prev">
          Anterior
        </Link>
      ) : (
        <span />
      )}
      <p className="text-sm text-gray-700">
        Página {page} de {pages}
      </p>
      {page < pages ? (
        <Link href={hrefFor(page + 1)} className={linkClass} rel="next">
          Siguiente
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}
