import type { Metadata } from "next";

import { requireUser } from "@/features/auth/dal";
import { MembershipAction } from "@/features/communities/components/MembershipAction";
import { getCommunity, getMyMembership } from "@/features/communities/data";

type CommunityPageProps = { params: Promise<{ communityId: string }> };

export async function generateMetadata({ params }: CommunityPageProps): Promise<Metadata> {
  const { communityId } = await params;
  const community = await getCommunity(communityId);
  return { title: `${community.name} · EntreVecinos` };
}

const NOTICES = {
  pending:
    "Tu solicitud está pendiente de aprobación. Podrás ver y publicar anuncios cuando un administrador la apruebe.",
  rejected: "No tienes acceso a esta comunidad.",
  blocked: "No tienes acceso a esta comunidad.",
} as const;

export default async function CommunityPage({ params }: CommunityPageProps) {
  await requireUser();
  const { communityId } = await params;
  const [community, membership] = await Promise.all([
    getCommunity(communityId),
    getMyMembership(communityId),
  ]);
  const place = [community.city, community.postal_code].filter(Boolean).join(" · ");
  const approved = membership?.status === "approved";

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{community.name}</h1>
        {place && <p className="mt-1 text-gray-600">{place}</p>}
      </div>
      {community.description && (
        <p className="whitespace-pre-line text-gray-800">{community.description}</p>
      )}

      {!approved && (
        <section aria-label="Acceso a la comunidad" className="flex flex-col items-start gap-3">
          {membership ? (
            <p role="status" className="rounded-md bg-amber-50 px-3 py-2 text-amber-900">
              {NOTICES[membership.status as keyof typeof NOTICES]}
            </p>
          ) : (
            <>
              <p className="text-gray-700">Solicita el acceso para ver y publicar anuncios.</p>
              <MembershipAction communityId={community.id} status={undefined} />
            </>
          )}
        </section>
      )}
    </main>
  );
}
