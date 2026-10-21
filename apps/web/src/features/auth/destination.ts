import "server-only";

import type { ApiMyMembership } from "@/features/communities/types";
import { apiFetch } from "@/lib/api/server";

import { COMMUNITIES_PATH, HOME_PATH } from "./routes";

/**
 * Destino tras iniciar sesión sin `next`: la búsqueda de comunidades si el usuario no es miembro
 * aprobado de ninguna activa; si no, el inicio. Recibe el token recién emitido porque la *cookie*
 * de sesión se acaba de escribir. Si la API falla, va al inicio: la sesión ya está creada.
 */
export async function postLoginPath(token: string): Promise<string> {
  const result = await apiFetch<{ items: ApiMyMembership[] }>("/users/me/memberships?status=approved", {
    token,
  });
  if (!result.ok) return HOME_PATH;

  // La API devuelve las comunidades desactivadas si la membresía está aprobada; su página da 404.
  const communities = result.data.items.filter((m) => m.community.is_active);
  return communities.length === 0 ? COMMUNITIES_PATH : HOME_PATH;
}
