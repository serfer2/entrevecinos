import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { cache } from "react";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import type { ApiCommunity } from "@/features/communities/types";
import { isUuid } from "@/lib/forms";

type CommunityPageProps = { params: Promise<{ communityId: string }> };

const getCommunity = cache(async (communityId: string): Promise<ApiCommunity> => {
  if (!isUuid(communityId)) notFound();
  const result = await userApiFetch<ApiCommunity>(`/communities/${communityId}`);
  if (result.ok) return result.data;
  if (result.error.status === 404) notFound();
  throw new Error(`No se pudo cargar la comunidad (estado ${result.error.status})`);
});

export async function generateMetadata({ params }: CommunityPageProps): Promise<Metadata> {
  const { communityId } = await params;
  const community = await getCommunity(communityId);
  return { title: `${community.name} · EntreVecinos` };
}

export default async function CommunityPage({ params }: CommunityPageProps) {
  await requireUser();
  const { communityId } = await params;
  const community = await getCommunity(communityId);
  const place = [community.city, community.postal_code].filter(Boolean).join(" · ");

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{community.name}</h1>
        {place && <p className="mt-1 text-gray-600">{place}</p>}
      </div>
      {community.description && (
        <p className="whitespace-pre-line text-gray-800">{community.description}</p>
      )}
    </main>
  );
}
