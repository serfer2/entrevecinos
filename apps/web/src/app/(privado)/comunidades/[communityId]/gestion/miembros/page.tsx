import type { Metadata } from "next";
import Link from "next/link";

import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { Forbidden } from "@/components/ui/Forbidden";
import { Pagination } from "@/components/ui/Pagination";
import { requireUser } from "@/features/auth/dal";
import { manageMember } from "@/features/communities/admin/actions";
import {
  MEMBER_CONFLICTS,
  type MemberConflict,
  membersPath,
  ROLE_LABELS,
  rowActions,
  STATUS_FILTERS,
  STATUS_LABELS,
  type StatusFilter,
} from "@/features/communities/admin/members";
import { requestsPath } from "@/features/communities/admin/paths";
import { getCommunity, getCommunityMemberships } from "@/features/communities/data";
import { formatLongDate } from "@/lib/dates";
import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

export const metadata: Metadata = { title: "Miembros · EntreVecinos" };

type MembersPageProps = {
  params: Promise<{ communityId: string }>;
  searchParams: Promise<SearchParams>;
};

const DONE_MESSAGES = {
  bloqueado: (name: string) => `${name} ha sido bloqueado.`,
  desbloqueado: (name: string) => `${name} ha sido desbloqueado.`,
  expulsado: (name: string) => `${name} ha sido expulsado.`,
} as const;

const button = "rounded-lg px-3 py-1.5 text-sm font-medium";

export default async function MembersPage({ params, searchParams }: MembersPageProps) {
  const user = await requireUser();
  const { communityId } = await params;
  const query = await searchParams;
  const estado = firstParam(query, "estado");
  const filter = estado in STATUS_FILTERS ? (estado as StatusFilter) : null;
  const page = pageParam(query);
  const [community, memberships] = await Promise.all([
    getCommunity(communityId),
    getCommunityMemberships(communityId, {
      status: filter ? STATUS_FILTERS[filter].status : undefined,
      page,
    }),
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

  const done = firstParam(query, "resultado");
  const success =
    done in DONE_MESSAGES
      ? DONE_MESSAGES[done as keyof typeof DONE_MESSAGES](firstParam(query, "nombre") || "El vecino")
      : null;
  const errorCode = firstParam(query, "error");
  const error = errorCode in MEMBER_CONFLICTS ? MEMBER_CONFLICTS[errorCode as MemberConflict] : null;
  const list = memberships.page;
  const filterQuery = filter ? { estado: filter } : undefined;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-6">
      <div>
        <Link href={`/comunidades/${communityId}`} className="text-sm font-medium text-emerald-800 underline">
          Volver a {community.name}
        </Link>
        <h1 className="mt-4 text-3xl font-semibold text-gray-900">Miembros</h1>
      </div>

      {success && (
        <p role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {success}
        </p>
      )}
      {error && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
          {error}
        </p>
      )}

      <nav aria-label="Filtrar por estado">
        <ul className="flex flex-wrap gap-2 text-sm">
          <li>
            <Link
              href={membersPath(communityId)}
              aria-current={filter === null ? "page" : undefined}
              className="rounded-full border border-gray-300 px-3 py-1 aria-[current=page]:border-emerald-700 aria-[current=page]:bg-emerald-50"
            >
              Todos
            </Link>
          </li>
          {Object.entries(STATUS_FILTERS).map(([value, { label }]) => (
            <li key={value}>
              <Link
                href={membersPath(communityId, { estado: value })}
                aria-current={filter === value ? "page" : undefined}
                className="rounded-full border border-gray-300 px-3 py-1 aria-[current=page]:border-emerald-700 aria-[current=page]:bg-emerald-50"
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {list.items.length === 0 ? (
        <p className="text-gray-700">No hay miembros con este estado.</p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 overflow-hidden rounded-2xl border border-gray-200 bg-white">
          {list.items.map(({ user: member, role, status, joined_at }) => {
            const actions = rowActions({ status, role, userId: member.id }, user.id);
            const hidden = (
              <>
                <input type="hidden" name="community_id" value={communityId} />
                <input type="hidden" name="user_id" value={member.id} />
                <input type="hidden" name="name" value={member.full_name} />
              </>
            );
            return (
              <li key={member.id} className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-medium text-gray-900">{member.full_name}</p>
                  <p className="text-sm text-gray-600">
                    {ROLE_LABELS[role]}
                    {status !== "approved" && ` · ${STATUS_LABELS[status]}`}
                    {status !== "rejected" && joined_at && ` · Miembro desde el ${formatLongDate(joined_at)}`}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {actions === "solicitud" ? (
                    <Link href={requestsPath(communityId)} className="text-sm font-medium text-emerald-800 underline">
                      Ir a solicitudes
                    </Link>
                  ) : (
                    actions.map((action) =>
                      action === "desbloquear" ? (
                        <form key={action} action={manageMember}>
                          {hidden}
                          <input type="hidden" name="action" value={action} />
                          <button type="submit" className={`${button} border border-emerald-700 text-emerald-800 hover:bg-emerald-50`}>
                            Desbloquear
                          </button>
                        </form>
                      ) : (
                        <ConfirmDialog
                          key={action}
                          action={manageMember}
                          triggerLabel={action === "bloquear" ? "Bloquear" : "Expulsar"}
                          title={action === "bloquear" ? `¿Bloquear a ${member.full_name}?` : `¿Expulsar a ${member.full_name}?`}
                          message={
                            action === "bloquear"
                              ? "Dejará de ver y publicar anuncios, sus anuncios dejarán de mostrarse en la comunidad y no podrá volver a solicitar el acceso."
                              : "Dejará de ver y publicar anuncios y sus anuncios dejarán de mostrarse, aunque podrá volver a solicitar el acceso."
                          }
                          confirmLabel={action === "bloquear" ? "Bloquear" : "Expulsar"}
                        >
                          {hidden}
                          <input type="hidden" name="action" value={action} />
                        </ConfirmDialog>
                      ),
                    )
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      )}

      <Pagination
        page={list.page}
        pageSize={list.page_size}
        total={list.total}
        hrefFor={(n) => membersPath(communityId, { ...filterQuery, ...(n > 1 ? { page: String(n) } : {}) })}
      />
    </main>
  );
}
