import type { Metadata } from "next";
import Link from "next/link";

import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { Forbidden } from "@/components/ui/Forbidden";
import { Pagination } from "@/components/ui/Pagination";
import { requireUser } from "@/features/auth/dal";
import {
  REQUESTS_RESULT_MESSAGES,
  type RequestsResult,
  requestsPath,
} from "@/features/communities/admin/paths";
import { reviewRequest } from "@/features/communities/admin/actions";
import { getCommunity, getCommunityMemberships } from "@/features/communities/data";
import { formatLongDate } from "@/lib/dates";
import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

export const metadata: Metadata = { title: "Solicitudes · EntreVecinos" };

type RequestsPageProps = {
  params: Promise<{ communityId: string }>;
  searchParams: Promise<SearchParams>;
};

export default async function RequestsPage({ params, searchParams }: RequestsPageProps) {
  await requireUser();
  const { communityId } = await params;
  const query = await searchParams;
  const page = pageParam(query);
  const [community, memberships] = await Promise.all([
    getCommunity(communityId),
    getCommunityMemberships(communityId, { status: "pending", page }),
  ]);

  if (!memberships.ok) {
    return (
      <Forbidden
        message="No tienes permisos para gestionar esta comunidad."
        backHref={`/comunidades/${communityId}`}
        backLabel={`Volver a ${community.name}`}
      />
    );
  }

  const result = firstParam(query, "resultado");
  const message =
    result in REQUESTS_RESULT_MESSAGES ? REQUESTS_RESULT_MESSAGES[result as RequestsResult] : null;
  const requests = memberships.page;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-10">
      <div>
        <Link href={`/comunidades/${communityId}`} className="text-sm font-medium text-emerald-800 underline">
          Volver a {community.name}
        </Link>
        <h1 className="mt-4 text-3xl font-semibold text-gray-900">Solicitudes de acceso</h1>
      </div>

      {message && (
        <p
          role={result === "error" ? "alert" : "status"}
          className={`rounded-lg px-3 py-2 text-sm ${result === "error" ? "bg-red-50 text-red-800" : "bg-emerald-50 text-emerald-900"}`}
        >
          {message}
        </p>
      )}

      {requests.items.length === 0 ? (
        <p className="text-gray-700">No hay solicitudes pendientes.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 overflow-hidden rounded-2xl border border-gray-200 bg-white">
          {requests.items.map(({ user, requested_at }) => (
            <li key={user.id} className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium text-gray-900">{user.full_name}</p>
                <p className="text-sm text-gray-600">Solicitado el {formatLongDate(requested_at)}</p>
              </div>
              <div className="flex gap-2">
                <form action={reviewRequest}>
                  <input type="hidden" name="community_id" value={communityId} />
                  <input type="hidden" name="user_id" value={user.id} />
                  <input type="hidden" name="decision" value="approved" />
                  <button
                    type="submit"
                    className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
                  >
                    Aprobar
                  </button>
                </form>
                <ConfirmDialog
                  action={reviewRequest}
                  triggerLabel="Rechazar"
                  title={`¿Rechazar la solicitud de ${user.full_name}?`}
                  message="No podrá volver a solicitar el acceso."
                  confirmLabel="Rechazar solicitud"
                >
                  <input type="hidden" name="community_id" value={communityId} />
                  <input type="hidden" name="user_id" value={user.id} />
                  <input type="hidden" name="decision" value="rejected" />
                </ConfirmDialog>
              </div>
            </li>
          ))}
        </ul>
      )}

      <Pagination
        page={requests.page}
        pageSize={requests.page_size}
        total={requests.total}
        hrefFor={(n) => (n > 1 ? `${requestsPath(communityId)}?page=${n}` : requestsPath(communityId))}
      />
    </main>
  );
}
