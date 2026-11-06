import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { canAccessCommunity } from "@/features/communities/access";
import { AccessNotice } from "@/features/communities/components/AccessNotice";
import { getCommunity, getMyMembership } from "@/features/communities/data";
import { publishListing } from "@/features/listings/actions";
import { ListingForm } from "@/features/listings/components/ListingForm";
import { getCategories } from "@/features/listings/data";

export const metadata: Metadata = { title: "Publicar anuncio · EntreVecinos" };

type NewListingPageProps = { params: Promise<{ communityId: string }> };

export default async function NewListingPage({ params }: NewListingPageProps) {
  const user = await requireUser();
  const { communityId } = await params;
  const [community, membership] = await Promise.all([
    getCommunity(communityId),
    getMyMembership(communityId),
  ]);
  const approved = canAccessCommunity(user, membership);

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-10">
      <div>
        <Link href={`/comunidades/${community.id}`} className="text-sm font-medium text-emerald-800 underline">
          Volver a {community.name}
        </Link>
        <h1 className="mt-4 text-3xl font-semibold text-gray-900">Publicar un anuncio</h1>
      </div>
      {approved ? (
        <ListingForm
          action={publishListing.bind(null, community.id)}
          categories={await getCategories()}
          submitLabel="Publicar anuncio"
          pendingLabel="Publicando…"
        />
      ) : (
        <AccessNotice communityId={community.id} membership={membership} />
      )}
    </main>
  );
}
