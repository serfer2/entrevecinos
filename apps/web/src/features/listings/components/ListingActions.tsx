import Link from "next/link";

import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

import { deleteListing } from "../actions";
import type { ApiListing } from "../types";

export type ListingActionsProps = {
  listing: ApiListing;
  /** El usuario es el autor del anuncio. */
  isOwner: boolean;
  /** El usuario gestiona la comunidad (administrador, moderador o administrador de plataforma). */
  canModerate: boolean;
};

const secondary =
  "rounded-md border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50";

/**
 * Acciones del detalle según quién mira. Ocultarlas no protege nada: la API decide los permisos.
 */
export function ListingActions({ listing, isOwner }: ListingActionsProps) {
  const canEdit = isOwner && listing.status !== "hidden" && listing.status !== "completed";
  if (!isOwner) return null;

  return (
    <div className="flex flex-wrap gap-2" aria-label="Acciones del anuncio" role="group">
      {canEdit && (
        <Link href={`/anuncios/${listing.id}/editar`} className={secondary}>
          Editar anuncio
        </Link>
      )}
      <ConfirmDialog
        action={deleteListing}
        triggerLabel="Eliminar anuncio"
        title="¿Eliminar este anuncio?"
        message="Dejará de verse en la comunidad. Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
      >
        <input type="hidden" name="listing_id" value={listing.id} />
      </ConfirmDialog>
    </div>
  );
}
