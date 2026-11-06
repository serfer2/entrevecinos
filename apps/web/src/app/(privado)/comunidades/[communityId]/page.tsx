import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { canAccessCommunity, canManageCommunity } from "@/features/communities/access";
import { AccessNotice } from "@/features/communities/components/AccessNotice";
import { getCommunity, getMyMembership } from "@/features/communities/data";
import { CommunityListings } from "@/features/listings/components/CommunityListings";
import { parseListingSearch } from "@/features/listings/search-params";
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

const URL_MESSAGES = {
  publicado: "Anuncio publicado.",
  eliminado: "Anuncio eliminado.",
  ocultado: "Anuncio ocultado.",
  "no-disponible": "Este anuncio ya no estaba disponible.",
} as const;

export default async function CommunityPage({ params, searchParams }: CommunityPageProps) {
  const user = await requireUser();
  const { communityId } = await params;
  const query = await searchParams;
  const [community, membership] = await Promise.all([
    getCommunity(communityId),
    getMyMembership(communityId),
  ]);
  const place = [community.city, community.postal_code].filter(Boolean).join(" · ");
  const approved = canAccessCommunity(user, membership);

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-semibold text-gray-900 sm:text-4xl">{community.name}</h1>
          {place && (
            <p className="flex items-center gap-1.5 text-gray-600">
              <svg aria-hidden viewBox="0 0 24 24" className="h-4 w-4 text-emerald-700" fill="none" stroke="currentColor" strokeWidth="1.8">
                <path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11Z" />
                <circle cx="12" cy="10" r="2.3" />
              </svg>
              {place}
            </p>
          )}
        </div>
        {approved && (
          <div className="flex flex-wrap gap-2">
            <Link
              href={`/comunidades/${community.id}/anuncios/nuevo`}
              className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-medium text-white no-underline shadow-xs hover:bg-emerald-800"
            >
              Publicar anuncio
            </Link>
            {/* Solo orientativo: la API decide los permisos (403 en la gestión). */}
            {canManageCommunity(user, membership) && (
              <Link
                href={`/comunidades/${community.id}/gestion/solicitudes`}
                className="rounded-lg border border-emerald-700 bg-white px-4 py-2 text-sm font-medium text-emerald-800 no-underline hover:bg-emerald-50"
              >
                Gestionar comunidad
              </Link>
            )}
          </div>
        )}
      </div>
      {community.description && (
        <p className="max-w-3xl whitespace-pre-line text-gray-700">{community.description}</p>
      )}

      {approved &&
        Object.entries(URL_MESSAGES).map(
          ([param, message]) =>
            firstParam(query, param) === "1" && (
              <p key={param} role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
                {message}
              </p>
            ),
        )}

      {approved ? (
        <CommunityListings communityId={community.id} search={parseListingSearch(query)} />
      ) : (
        <AccessNotice communityId={community.id} membership={membership} />
      )}
    </main>
  );
}
