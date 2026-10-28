import Link from "next/link";

import { ConfirmDialog } from "@/components/ui/ConfirmDialog";

import { changeListingStatus, deleteListing, moderateListing } from "../actions";
import type { ApiListing, ListingStatus } from "../types";

export type ListingActionsProps = {
  listing: ApiListing;
  /** El usuario es el autor del anuncio. */
  isOwner: boolean;
  /** El usuario gestiona la comunidad (administrador, moderador o administrador de plataforma). */
  canModerate: boolean;
};

const secondary =
  "rounded-lg border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50";

function StatusButton({ listingId, status, label }: { listingId: string; status: ListingStatus; label: string }) {
  return (
    <form action={changeListingStatus}>
      <input type="hidden" name="listing_id" value={listingId} />
      <input type="hidden" name="status" value={status} />
      <button type="submit" className={secondary}>
        {label}
      </button>
    </form>
  );
}

/**
 * Acciones del detalle según quién mira; los roles se suman (un administrador que es el autor ve
 * las de ambos). Ocultarlas no protege nada: la API decide los permisos.
 */
export function ListingActions({ listing, isOwner, canModerate }: ListingActionsProps) {
  const hidden = listing.status === "hidden";
  const canEdit = isOwner && !hidden && listing.status !== "completed";
  if (!isOwner && !canModerate) return null;

  return (
    <div className="flex flex-col gap-3">
      {hidden && (isOwner || canModerate) && (
        <p role="status" className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">
          Este anuncio está oculto y no se muestra en la comunidad.
        </p>
      )}
      <div className="flex flex-wrap gap-2" aria-label="Acciones del anuncio" role="group">
        {canEdit && (
          <Link href={`/anuncios/${listing.id}/editar`} className={secondary}>
            Editar anuncio
          </Link>
        )}
        {isOwner && listing.status === "active" && (
          <StatusButton listingId={listing.id} status="reserved" label="Marcar como reservado" />
        )}
        {isOwner && listing.status === "reserved" && (
          <StatusButton listingId={listing.id} status="active" label="Quitar reserva" />
        )}
        {isOwner && (listing.status === "active" || listing.status === "reserved") && (
          <ConfirmDialog
            action={changeListingStatus}
            triggerLabel="Marcar como finalizado"
            title="¿Marcar este anuncio como finalizado?"
            message="Dejará de mostrarse en el listado y no podrás volver a activarlo ni editarlo."
            confirmLabel="Marcar como finalizado"
            triggerClassName={secondary}
          >
            <input type="hidden" name="listing_id" value={listing.id} />
            <input type="hidden" name="status" value="completed" />
          </ConfirmDialog>
        )}
        {isOwner && (
          <ConfirmDialog
            action={deleteListing}
            triggerLabel="Eliminar anuncio"
            title="¿Eliminar este anuncio?"
            message="Dejará de verse en la comunidad. Esta acción no se puede deshacer."
            confirmLabel="Eliminar"
          >
            <input type="hidden" name="listing_id" value={listing.id} />
          </ConfirmDialog>
        )}
        {canModerate && !hidden && (
          <ConfirmDialog
            action={moderateListing}
            triggerLabel="Ocultar anuncio"
            title="¿Ocultar este anuncio?"
            message="Dejará de mostrarse en la comunidad. Podrás restaurarlo más tarde."
            confirmLabel="Ocultar"
          >
            <input type="hidden" name="listing_id" value={listing.id} />
            <input type="hidden" name="status" value="hidden" />
          </ConfirmDialog>
        )}
        {canModerate && hidden && (
          <form action={moderateListing}>
            <input type="hidden" name="listing_id" value={listing.id} />
            <input type="hidden" name="status" value="active" />
            <button type="submit" className={secondary}>
              Restaurar anuncio
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
