import Link from "next/link";

import { PASSWORD_RESET_LINK_MESSAGES, type PasswordResetLinkError } from "../password-reset-link";
import { PASSWORD_RESET_REQUEST_PATH } from "../routes";

/** Enlace caducado o no válido: lo explica y ofrece pedir otro. */
export function PasswordResetLinkErrorNotice({ reason }: { reason: PasswordResetLinkError }) {
  return (
    <div className="flex flex-col gap-3">
      <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
        {PASSWORD_RESET_LINK_MESSAGES[reason]}
      </p>
      <Link
        href={PASSWORD_RESET_REQUEST_PATH}
        className="text-sm font-medium text-emerald-800 underline"
      >
        Pedir otro enlace
      </Link>
    </div>
  );
}
