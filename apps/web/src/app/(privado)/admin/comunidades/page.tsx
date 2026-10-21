import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { Pagination } from "@/components/ui/Pagination";
import { requireUser } from "@/features/auth/dal";
import { approveCommunity } from "@/features/platform-admin/actions";
import { getPendingCommunities } from "@/features/platform-admin/data";
import {
  PENDING_COMMUNITIES_PATH,
  PENDING_COMMUNITIES_RESULT_MESSAGES,
  type PendingCommunitiesResult,
} from "@/features/platform-admin/paths";
import { formatLongDate } from "@/lib/dates";
import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

export const metadata: Metadata = { title: "Comunidades pendientes · EntreVecinos" };

type PendingCommunitiesPageProps = { searchParams: Promise<SearchParams> };

export default async function PendingCommunitiesPage({ searchParams }: PendingCommunitiesPageProps) {
  const user = await requireUser();
  // Solo para administradores de plataforma; al resto no se le revela que la página existe.
  if (user.platform_role !== "platform_admin") notFound();

  const query = await searchParams;
  const communities = await getPendingCommunities(pageParam(query));
  const result = firstParam(query, "resultado");
  const message =
    result in PENDING_COMMUNITIES_RESULT_MESSAGES
      ? PENDING_COMMUNITIES_RESULT_MESSAGES[result as PendingCommunitiesResult]
      : null;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Comunidades pendientes de aprobación</h1>

      {message && (
        <p
          role={result === "error" ? "alert" : "status"}
          className={`rounded-md px-3 py-2 text-sm ${result === "error" ? "bg-red-50 text-red-800" : "bg-emerald-50 text-emerald-900"}`}
        >
          {message}
        </p>
      )}

      {communities.items.length === 0 ? (
        <p className="text-gray-700">No hay comunidades pendientes de aprobación.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 rounded-md border border-gray-200">
          {communities.items.map((community) => (
            <li
              key={community.id}
              className="flex flex-col gap-3 p-4 sm:flex-row sm:items-start sm:justify-between"
            >
              <div className="flex flex-col gap-1">
                <p className="font-medium text-gray-900">{community.name}</p>
                <p className="text-sm text-gray-600">
                  {[community.city, community.postal_code].filter(Boolean).join(" · ") ||
                    "Sin ubicación"}
                  {" · "}Creada el {formatLongDate(community.created_at)}
                </p>
                {community.description && (
                  <p className="text-sm whitespace-pre-line text-gray-700">{community.description}</p>
                )}
              </div>
              <form action={approveCommunity}>
                <input type="hidden" name="community_id" value={community.id} />
                <button
                  type="submit"
                  className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
                >
                  Aprobar
                </button>
              </form>
            </li>
          ))}
        </ul>
      )}

      <Pagination
        page={communities.page}
        pageSize={communities.page_size}
        total={communities.total}
        hrefFor={(n) => (n > 1 ? `${PENDING_COMMUNITIES_PATH}?page=${n}` : PENDING_COMMUNITIES_PATH)}
      />
    </main>
  );
}
