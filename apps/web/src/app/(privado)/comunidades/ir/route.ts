import { type NextRequest, NextResponse } from "next/server";

import { listingCriteria, parseListingSearch } from "@/features/listings/search-params";
import { isUuid } from "@/lib/forms";

/** Redirección con `Location` relativo: `request.url` lleva el host interno del servidor. */
function seeOther(path: string): NextResponse {
  return new NextResponse(null, { status: 303, headers: { Location: path } });
}

/**
 * Destino del selector de comunidad (formulario GET): valida el id y redirige a la comunidad
 * conservando solo la búsqueda y los filtros válidos (la página vuelve a la primera).
 */
export function GET(request: NextRequest) {
  const params = Object.fromEntries(request.nextUrl.searchParams);
  if (!isUuid(params.id)) return seeOther("/inicio");

  const query = listingCriteria(parseListingSearch(params)).toString();
  return seeOther(`/comunidades/${params.id}${query ? `?${query}` : ""}`);
}
