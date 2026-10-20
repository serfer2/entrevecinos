import type { Metadata } from "next";
import Link from "next/link";

import { Forbidden } from "@/components/ui/Forbidden";
import { requireUser } from "@/features/auth/dal";
import { getCommunity, getMyMembership } from "@/features/communities/data";
import { ListingActions } from "@/features/listings/components/ListingActions";
import { listingPriceLabel } from "@/features/listings/components/ListingCard";
import { ListingGallery } from "@/features/listings/components/ListingGallery";
import { getCategories, getListing } from "@/features/listings/data";
import { LISTING_TYPE_LABELS } from "@/features/listings/labels";
import { formatLongDate } from "@/lib/dates";

type ListingPageProps = { params: Promise<{ listingId: string }> };

const NO_ACCESS = "No tienes acceso a los anuncios de esta comunidad.";

export async function generateMetadata({ params }: ListingPageProps): Promise<Metadata> {
  const { listingId } = await params;
  const result = await getListing(listingId);
  return { title: result.ok ? `${result.listing.title} · EntreVecinos` : "Sin acceso · EntreVecinos" };
}

export default async function ListingPage({ params }: ListingPageProps) {
  const user = await requireUser();
  const { listingId } = await params;
  const result = await getListing(listingId);
  if (!result.ok) return <Forbidden message={NO_ACCESS} />;

  const { listing } = result;
  const [categories, community, membership] = await Promise.all([
    getCategories(),
    getCommunity(listing.community_id),
    getMyMembership(listing.community_id),
  ]);
  const category = categories.find((c) => c.id === listing.category_id);
  const price = listingPriceLabel(listing);
  const updated = new Date(listing.updated_at).getTime() - new Date(listing.published_at).getTime() > 60_000;
  const isOwner = listing.owner.id === user.id;
  const canModerate =
    user.platform_role === "platform_admin" ||
    (membership?.status === "approved" && membership.role !== "member");

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-10">
      <Link href={`/comunidades/${community.id}`} className="self-start text-sm font-medium text-emerald-800 underline">
        Volver a {community.name}
      </Link>

      <div className="grid gap-8 md:grid-cols-2">
        <ListingGallery title={listing.title} images={listing.images} />

        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="rounded bg-emerald-50 px-2 py-0.5 font-medium text-emerald-900">
              {LISTING_TYPE_LABELS[listing.type]}
            </span>
            {listing.status === "reserved" && (
              <span className="rounded bg-amber-500 px-2 py-0.5 font-semibold text-white">Reservado</span>
            )}
            {category && <span className="text-gray-600">{category.name}</span>}
          </div>
          <h1 className="text-2xl font-semibold text-gray-900">{listing.title}</h1>
          {price && <p className="text-2xl font-semibold text-gray-900">{price}</p>}
          <p className="text-sm text-gray-600">
            Publicado el <time dateTime={listing.published_at}>{formatLongDate(listing.published_at)}</time>
            {updated && (
              <>
                {" · "}Actualizado el <time dateTime={listing.updated_at}>{formatLongDate(listing.updated_at)}</time>
              </>
            )}
          </p>

          <ListingActions listing={listing} isOwner={isOwner} canModerate={canModerate} />

          <section aria-labelledby="description-title">
            <h2 id="description-title" className="mb-2 text-lg font-medium text-gray-900">
              Descripción
            </h2>
            <p className="whitespace-pre-line break-words text-gray-800">{listing.description}</p>
          </section>

          <section aria-labelledby="owner-title" className="rounded-lg border border-gray-200 p-4">
            <h2 id="owner-title" className="text-lg font-medium text-gray-900">
              Anunciante
            </h2>
            <p className="mt-1 text-gray-800">{listing.owner.full_name}</p>
          </section>
        </div>
      </div>
    </main>
  );
}
