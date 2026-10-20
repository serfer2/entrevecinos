import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { MEMBERSHIP_STATUS_LABELS } from "@/features/communities/components/MembershipAction";
import { getMyMemberships } from "@/features/communities/data";

export const metadata: Metadata = { title: "Inicio · EntreVecinos" };

export default async function HomePage() {
  const user = await requireUser();
  const memberships = await getMyMemberships();

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Hola, {user.full_name}</h1>

      <section aria-labelledby="my-communities" className="flex flex-col gap-3">
        <h2 id="my-communities" className="text-lg font-medium text-gray-900">
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
          <ul className="flex flex-col divide-y divide-gray-200 rounded-md border border-gray-200">
            {memberships.map(({ community, status }) => (
              <li key={community.id} className="flex items-center justify-between gap-3 p-4">
                <Link
                  href={`/comunidades/${community.id}`}
                  className="font-medium text-emerald-800 underline"
                >
                  {community.name}
                </Link>
                <span className="text-sm text-gray-600">{MEMBERSHIP_STATUS_LABELS[status]}</span>
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
