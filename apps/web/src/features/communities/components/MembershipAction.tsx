import Link from "next/link";

import { requestAccess } from "../actions";
import type { MembershipStatus } from "../types";
import { RequestAccessButton } from "./RequestAccessButton";

type MembershipActionProps = {
  communityId: string;
  status: MembershipStatus | undefined;
  /** `platform_admin` entra en cualquier comunidad, sea cual sea su membresía (como en la API). */
  isPlatformAdmin?: boolean;
};

/** Acción disponible en una comunidad según mi membresía. */
export function MembershipAction({ communityId, status, isPlatformAdmin = false }: MembershipActionProps) {
  switch (isPlatformAdmin ? "approved" : status) {
    case undefined:
      return <RequestAccessButton communityId={communityId} action={requestAccess} />;
    case "pending":
      return <p className="text-sm font-medium text-amber-800">Solicitud pendiente</p>;
    case "approved":
      return (
        <Link
          href={`/comunidades/${communityId}`}
          className="rounded-lg border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50"
        >
          Entrar
        </Link>
      );
    default:
      // Texto neutro a propósito para rechazados y bloqueados.
      return <p className="text-sm text-gray-600">Acceso no disponible</p>;
  }
}

export const MEMBERSHIP_STATUS_LABELS: Record<MembershipStatus, string> = {
  pending: "Pendiente",
  approved: "Miembro",
  rejected: "Rechazado",
  blocked: "Bloqueado",
};
