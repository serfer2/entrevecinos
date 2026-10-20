import { type NextRequest, NextResponse } from "next/server";

import { getSessionToken } from "@/features/auth/session";
import { apiRedirect } from "@/lib/api/server";
import { isUuid } from "@/lib/forms";

type RouteContext = { params: Promise<{ assetId: string }> };

/**
 * Sirve una imagen al navegador sin exponer el token: pide a la API la URL prefirmada
 * (sin seguir la redirección) y redirige a ella.
 */
export async function GET(_request: NextRequest, { params }: RouteContext) {
  const { assetId } = await params;
  const token = await getSessionToken();
  if (!token) return new NextResponse(null, { status: 401 });
  if (!isUuid(assetId)) return new NextResponse(null, { status: 404 });

  const { status, location } = await apiRedirect(`/media/${assetId}`, token);
  if (status === 302 && location) {
    return new NextResponse(null, {
      status: 302,
      headers: { Location: location, "Cache-Control": "private, max-age=240" },
    });
  }
  if (status === 401) return new NextResponse(null, { status: 401 });
  // 403 y 404 por igual: no se revela qué imágenes existen.
  if (status === 403 || status === 404) return new NextResponse(null, { status: 404 });
  return new NextResponse(null, { status: 502 });
}
