import "server-only";

import { userApiFetch } from "@/features/auth/api";
import type { ApiCommunity } from "@/features/communities/types";
import type { ApiPage } from "@/lib/api/types";

/** Comunidades pendientes de aprobación (inactivas), de la más antigua a la más reciente. */
export async function getPendingCommunities(page: number): Promise<ApiPage<ApiCommunity>> {
  const query = new URLSearchParams({ is_active: "false" });
  if (page > 1) query.set("page", String(page));
  const result = await userApiFetch<ApiPage<ApiCommunity>>(`/admin/communities?${query}`);
  if (result.ok) return result.data;
  throw new Error(`No se pudieron cargar las comunidades pendientes (estado ${result.error.status})`);
}
