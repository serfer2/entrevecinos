import type { ApiMyMembership } from "../types";
import { MembershipAction } from "./MembershipAction";

const NOTICES = {
  pending:
    "Tu solicitud está pendiente de aprobación. Podrás ver y publicar anuncios cuando un administrador la apruebe.",
  rejected: "No tienes acceso a esta comunidad.",
  blocked: "No tienes acceso a esta comunidad.",
} as const;

type AccessNoticeProps = {
  communityId: string;
  membership: ApiMyMembership | undefined;
};

/** Aviso para quien no tiene una membresía aprobada (en lugar de los anuncios). */
export function AccessNotice({ communityId, membership }: AccessNoticeProps) {
  return (
    <section aria-label="Acceso a la comunidad" className="flex flex-col items-start gap-3">
      {membership ? (
        <p role="status" className="rounded-lg bg-amber-50 px-3 py-2 text-amber-900">
          {NOTICES[membership.status as keyof typeof NOTICES]}
        </p>
      ) : (
        <>
          <p className="text-gray-700">Solicita el acceso para ver y publicar anuncios.</p>
          <MembershipAction communityId={communityId} status={undefined} />
        </>
      )}
    </section>
  );
}
