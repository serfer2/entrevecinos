import type { Metadata } from "next";
import Link from "next/link";

import { Forbidden } from "@/components/ui/Forbidden";
import { requireUser } from "@/features/auth/dal";
import { updateListing } from "@/features/listings/actions";
import { listingFormValuesOf } from "@/features/listings/changes";
import { ListingForm } from "@/features/listings/components/ListingForm";
import { getCategories, getListing } from "@/features/listings/data";
import { EDIT_MESSAGES } from "@/features/listings/form";

export const metadata: Metadata = { title: "Editar anuncio · EntreVecinos" };

type EditListingPageProps = { params: Promise<{ listingId: string }> };

export default async function EditListingPage({ params }: EditListingPageProps) {
  const user = await requireUser();
  const { listingId } = await params;
  const result = await getListing(listingId);
  // La API vuelve a comprobar que es el autor al guardar.
  if (!result.ok || result.listing.owner.id !== user.id) {
    return <Forbidden message={EDIT_MESSAGES.forbidden} backHref={`/anuncios/${listingId}`} backLabel="Volver al anuncio" />;
  }
  const { listing } = result;

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-10">
      <div>
        <Link href={`/anuncios/${listing.id}`} className="text-sm font-medium text-emerald-800 underline">
          Volver al anuncio
        </Link>
        <h1 className="mt-4 text-2xl font-semibold text-gray-900">Editar anuncio</h1>
      </div>
      <ListingForm
        action={updateListing.bind(null, listing.id)}
        categories={await getCategories()}
        initialValues={listingFormValuesOf(listing)}
        submitLabel="Guardar cambios"
        pendingLabel="Guardando…"
      />
    </main>
  );
}
