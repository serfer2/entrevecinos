import "server-only";

import type { ApiMyMembership } from "@/features/communities/types";
import { apiFetch } from "@/lib/api/server";

import { COMMUNITIES_PATH, HOME_PATH } from "./routes";

/**
 * Destino tras iniciar sesión sin `next`, según las comunidades activas en las que el usuario es
 * miembro aprobado: ninguna → la búsqueda de comunidades; una → esa comunidad; varias → el inicio,
 * que las lista. Recibe el token recién emitido porque la *cookie*
 * de sesión se acaba de escribir. Si la API falla, va al inicio: la sesión ya está creada.
 */
export async function postLoginPath(token: string): Promise<string> {
  const result = await apiFetch<{ items: ApiMyMembership[] }>("/users/me/memberships?status=approved", {
    token,
  });
  if (!result.ok) return HOME_PATH;

  // La API devuelve las comunidades desactivadas si la membresía está aprobada; su página da 404.
  const communities = result.data.items.filter((m) => m.community.is_active);
  if (communities.length === 0) return COMMUNITIES_PATH;
  if (communities.length === 1) return `${COMMUNITIES_PATH}/${communities[0].community.id}`;
  return HOME_PATH;
}
