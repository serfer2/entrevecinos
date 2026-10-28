import type { Metadata } from "next";
import Link from "next/link";

import { Pagination } from "@/components/ui/Pagination";
import { TextField } from "@/components/ui/TextField";
import { requireUser } from "@/features/auth/dal";
import { MembershipAction } from "@/features/communities/components/MembershipAction";
import { getMyMemberships, searchCommunities } from "@/features/communities/data";
import { parseCommunitySearch, searchHref } from "@/features/communities/search";

export const metadata: Metadata = { title: "Comunidades · EntreVecinos" };

type CommunitiesPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function CommunitiesPage({ searchParams }: CommunitiesPageProps) {
  const user = await requireUser();
  const search = parseCommunitySearch(await searchParams);
  const [results, memberships] = await Promise.all([
    searchCommunities(search),
    getMyMemberships(),
  ]);
  const statusOf = new Map(memberships.map((m) => [m.community.id, m.status]));

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-3xl font-semibold text-gray-900">Buscar comunidades</h1>
        <Link href="/comunidades/nueva" className="font-medium text-emerald-800 underline">
          Crear una comunidad
        </Link>
      </div>

      <form
        method="get"
        role="search"
        className="grid gap-3 rounded-2xl border border-gray-200 bg-white p-4 shadow-xs sm:grid-cols-[minmax(0,2fr)_minmax(0,1fr)_minmax(0,1fr)_auto] sm:items-end sm:p-5"
      >
        <TextField name="q" label="Nombre" type="search" maxLength={160} defaultValue={search.q} />
        <TextField name="city" label="Ciudad" maxLength={120} defaultValue={search.city} />
        <TextField
          name="postal_code"
          label="Código postal"
          inputMode="numeric"
          maxLength={16}
          defaultValue={search.postal_code}
        />
        <button
          type="submit"
          className="rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800"
        >
          Buscar
        </button>
      </form>

      <section aria-labelledby="results" className="flex flex-col gap-4">
        <h2 id="results" className="sr-only">
          Resultados
        </h2>
        {results.items.length === 0 ? (
          <p className="text-gray-700">
            No hemos encontrado comunidades con esos datos.{" "}
            <Link href="/comunidades/nueva" className="font-medium text-emerald-800 underline">
              Crea una comunidad
            </Link>
          </p>
        ) : (
          <ul className="flex flex-col divide-y divide-gray-200 overflow-hidden rounded-2xl border border-gray-200 bg-white">
            {results.items.map((community) => (
              <li
                key={community.id}
                className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium text-gray-900">{community.name}</p>
                  <p className="text-sm text-gray-600">
                    {[community.city, community.postal_code].filter(Boolean).join(" · ") ||
                      "Sin ubicación"}
                  </p>
                </div>
                <MembershipAction
                  communityId={community.id}
                  status={statusOf.get(community.id)}
                  isPlatformAdmin={user.platform_role === "platform_admin"}
                />
              </li>
            ))}
          </ul>
        )}
        <Pagination
          page={results.page}
          pageSize={results.page_size}
          total={results.total}
          hrefFor={(page) => searchHref(search, page)}
        />
      </section>
    </main>
  );
}
