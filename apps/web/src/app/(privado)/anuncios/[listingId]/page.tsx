import type { Metadata } from "next";
import Link from "next/link";

import { Forbidden } from "@/components/ui/Forbidden";
import { requireUser } from "@/features/auth/dal";
import { getCommunity, getMyMembership } from "@/features/communities/data";
import { ContactOwner } from "@/features/listings/components/ContactOwner";
import { ListingActions } from "@/features/listings/components/ListingActions";
import { listingPriceLabel } from "@/features/listings/components/ListingCard";
import { ListingGallery } from "@/features/listings/components/ListingGallery";
import { getCategories, getListing } from "@/features/listings/data";
import { LISTING_TYPE_LABELS } from "@/features/listings/labels";
import { formatLongDate } from "@/lib/dates";
import { firstParam, type SearchParams } from "@/lib/search-params";

type ListingPageProps = {
  params: Promise<{ listingId: string }>;
  searchParams: Promise<SearchParams>;
};

const URL_MESSAGES = {
  actualizado: "Anuncio actualizado.",
  restaurado: "Anuncio restaurado.",
} as const;

const STATUS_MESSAGES = {
  reservado: "Anuncio marcado como reservado.",
  disponible: "El anuncio vuelve a estar disponible.",
  finalizado: "Anuncio finalizado. Ya no se muestra en el listado.",
} as const;

const URL_ERRORS = {
  "eliminar-permiso": "No puedes eliminar este anuncio.",
  eliminar: "No se pudo eliminar el anuncio. Inténtalo de nuevo.",
  "estado-permiso": "Solo quien publicó el anuncio puede cambiar su estado.",
  "estado-conflicto": "Este cambio de estado no es posible en este momento.",
  estado: "No se pudo cambiar el estado. Inténtalo de nuevo.",
  "moderar-permiso": "No puedes moderar este anuncio.",
  "moderar-estado": "El anuncio ya estaba en ese estado.",
  moderar: "No se pudo cambiar el estado del anuncio. Inténtalo de nuevo.",
} as const;

const NO_ACCESS = "No tienes acceso a los anuncios de esta comunidad.";

export async function generateMetadata({ params }: ListingPageProps): Promise<Metadata> {
  const { listingId } = await params;
  const result = await getListing(listingId);
  return { title: result.ok ? `${result.listing.title} · EntreVecinos` : "Sin acceso · EntreVecinos" };
}

export default async function ListingPage({ params, searchParams }: ListingPageProps) {
  const user = await requireUser();
  const { listingId } = await params;
  const query = await searchParams;
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
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:py-10">
      <Link href={`/comunidades/${community.id}`} className="self-start text-sm font-medium text-emerald-800 underline">
        ← Volver a {community.name}
      </Link>
      {Object.entries(URL_MESSAGES).map(
        ([param, message]) =>
          firstParam(query, param) === "1" && (
            <p key={param} role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
              {message}
            </p>
          ),
      )}
      {firstParam(query, "cambio") in STATUS_MESSAGES && (
        <p role="status" className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
          {STATUS_MESSAGES[firstParam(query, "cambio") as keyof typeof STATUS_MESSAGES]}
        </p>
      )}
      {firstParam(query, "error") in URL_ERRORS && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
          {URL_ERRORS[firstParam(query, "error") as keyof typeof URL_ERRORS]}
        </p>
      )}

      <div className="grid gap-8 md:grid-cols-2 lg:gap-12">
        <ListingGallery title={listing.title} images={listing.images} />

        <div className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 font-semibold text-emerald-900">
              {LISTING_TYPE_LABELS[listing.type]}
            </span>
            {listing.status === "reserved" && (
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 font-semibold text-amber-900">Reservado</span>
            )}
            {listing.status === "completed" && (
              <span className="rounded-full bg-gray-200 px-2.5 py-0.5 font-semibold text-gray-800">Finalizado</span>
            )}
            {category && <span className="text-gray-600">{category.name}</span>}
          </div>
          <h1 className="text-3xl font-semibold text-gray-900">{listing.title}</h1>
          {listing.status === "completed" && (
            <p role="status" className="rounded-lg bg-gray-100 px-3 py-2 text-sm text-gray-800">
              Este anuncio está finalizado.
            </p>
          )}
          {price && <p className="text-3xl font-semibold text-emerald-800">{price}</p>}
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
            <h2 id="description-title" className="mb-2 text-xl font-semibold text-gray-900">
              Descripción
            </h2>
            <p className="whitespace-pre-line break-words text-gray-800">{listing.description}</p>
          </section>

          <section aria-labelledby="owner-title" className="rounded-2xl border border-gray-200 bg-white p-5">
            <h2 id="owner-title" className="text-xl font-semibold text-gray-900">
              Anunciante
            </h2>
            <p className="mt-1 text-gray-800">{listing.owner.full_name}</p>
            <ContactOwner owner={listing.owner} listingTitle={listing.title} isOwner={isOwner} />
          </section>
        </div>
      </div>
    </main>
  );
}
