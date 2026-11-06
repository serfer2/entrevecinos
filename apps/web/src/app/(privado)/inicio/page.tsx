import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { MEMBERSHIP_STATUS_LABELS } from "@/features/communities/components/MembershipAction";
import { getMyMemberships } from "@/features/communities/data";
import { PENDING_COMMUNITIES_PATH } from "@/features/platform-admin/paths";
import { firstParam, type SearchParams } from "@/lib/search-params";

export const metadata: Metadata = { title: "Inicio · EntreVecinos" };

type HomePageProps = { searchParams: Promise<SearchParams> };

export default async function HomePage({ searchParams }: HomePageProps) {
  const user = await requireUser();
  const memberships = await getMyMemberships();
  const query = await searchParams;

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-semibold text-gray-900">Hola, {user.full_name}</h1>
        <p className="text-gray-600">Esto es lo que pasa en tus comunidades.</p>
      </div>
      {firstParam(query, "no-disponible") === "1" && (
        <p role="status" className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Este anuncio ya no estaba disponible.
        </p>
      )}
      {firstParam(query, "comunidad-pendiente") === "1" && (
        <p role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          Hemos recibido tu comunidad. Un administrador la revisará antes de activarla.
        </p>
      )}
      {user.platform_role === "platform_admin" && (
        <Link href={PENDING_COMMUNITIES_PATH} className="self-start font-medium text-emerald-800 underline">
          Comunidades pendientes de aprobación
        </Link>
      )}

      <section aria-labelledby="my-communities" className="flex flex-col gap-3">
        <h2 id="my-communities" className="text-xl font-semibold text-gray-900">
          Mis comunidades
        </h2>
        {memberships.length === 0 ? (
          <p className="text-gray-700">
            Todavía no perteneces a ninguna comunidad.{" "}
            <Link href="/comunidades" className="font-medium text-emerald-800 underline">
              Busca la de tu barrio
            </Link>{" "}
            o{" "}
            <Link href="/comunidades/nueva" className="font-medium text-emerald-800 underline">
              crea una
            </Link>
            .
          </p>
        ) : (
          <ul className="flex flex-col divide-y divide-gray-200 overflow-hidden rounded-2xl border border-gray-200 bg-white">
            {memberships.map(({ community, status }) => (
              <li key={community.id} className="flex items-center justify-between gap-3 px-5 py-4 hover:bg-emerald-50/50">
                {community.is_active ? (
                  <>
                    <Link
                      href={`/comunidades/${community.id}`}
                      className="font-medium text-emerald-800 underline"
                    >
                      {community.name}
                    </Link>
                    <span className="text-sm text-gray-600">{MEMBERSHIP_STATUS_LABELS[status]}</span>
                  </>
                ) : (
                  // Pendiente de aprobación: su página todavía no existe para nadie.
                  <>
                    <span className="font-medium text-gray-900">{community.name}</span>
                    <span className="text-sm font-medium text-amber-800">Pendiente de aprobación</span>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
        {memberships.length > 0 && (
          <Link href="/comunidades" className="self-start text-sm font-medium text-emerald-800 underline">
            Buscar más comunidades
          </Link>
        )}
      </section>
    </main>
  );
}
