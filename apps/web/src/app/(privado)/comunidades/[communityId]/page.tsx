import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { AccessNotice } from "@/features/communities/components/AccessNotice";
import { getCommunity, getMyMembership } from "@/features/communities/data";
import { firstParam, type SearchParams } from "@/lib/search-params";

type CommunityPageProps = {
  params: Promise<{ communityId: string }>;
  searchParams: Promise<SearchParams>;
};

export async function generateMetadata({ params }: CommunityPageProps): Promise<Metadata> {
  const { communityId } = await params;
  const community = await getCommunity(communityId);
  return { title: `${community.name} · EntreVecinos` };
}

export default async function CommunityPage({ params, searchParams }: CommunityPageProps) {
  await requireUser();
  const { communityId } = await params;
  const query = await searchParams;
  const [community, membership] = await Promise.all([
    getCommunity(communityId),
    getMyMembership(communityId),
  ]);
  const place = [community.city, community.postal_code].filter(Boolean).join(" · ");
  const approved = membership?.status === "approved";

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-10">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">{community.name}</h1>
          {place && <p className="mt-1 text-gray-600">{place}</p>}
        </div>
        {approved && (
          <div className="flex flex-wrap gap-2">
            <Link
              href={`/comunidades/${community.id}/anuncios/nuevo`}
              className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800"
            >
              Publicar anuncio
            </Link>
            {/* Solo orientativo: la API decide los permisos (403 en la gestión). */}
            {membership.role === "community_admin" && (
              <Link
                href={`/comunidades/${community.id}/gestion/solicitudes`}
                className="rounded-md border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50"
              >
                Gestionar comunidad
              </Link>
            )}
          </div>
        )}
      </div>
      {community.description && (
        <p className="whitespace-pre-line text-gray-800">{community.description}</p>
      )}

      {approved && firstParam(query, "publicado") === "1" && (
        <p role="status" className="rounded-md bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          Anuncio publicado.
        </p>
      )}

      {!approved && <AccessNotice communityId={community.id} membership={membership} />}
    </main>
  );
}
