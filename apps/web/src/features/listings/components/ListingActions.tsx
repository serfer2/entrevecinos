import type { ApiListing } from "../types";

export type ListingActionsProps = {
  listing: ApiListing;
  /** El usuario es el autor del anuncio. */
  isOwner: boolean;
  /** El usuario gestiona la comunidad (administrador, moderador o administrador de plataforma). */
  canModerate: boolean;
};

/**
 * Acciones del detalle según quién mira. Ocultarlas no protege nada: la API decide los permisos.
 * Los tickets de edición, borrado, estados y moderación añaden aquí sus botones.
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars -- las props las usan los tickets siguientes
export function ListingActions(_props: ListingActionsProps) {
  return null;
}
