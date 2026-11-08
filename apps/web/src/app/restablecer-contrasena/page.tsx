import type { Metadata } from "next";

import { AuthShell } from "@/components/ui/AuthShell";
import { resetPassword } from "@/features/auth/actions";
import { PasswordResetForm } from "@/features/auth/components/PasswordResetForm";
import { PasswordResetLinkErrorNotice } from "@/features/auth/components/PasswordResetLinkError";
import { isPasswordResetLinkError } from "@/features/auth/password-reset-link";
import { getPasswordResetToken } from "@/features/auth/reset-token";

export const metadata: Metadata = { title: "Nueva contraseña · EntreVecinos" };

type PasswordResetPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

/** Se llega desde el enlace del correo (`/restablecer-contrasena/enlace`), que deja el token. */
export default async function PasswordResetPage({ searchParams }: PasswordResetPageProps) {
  const { motivo } = await searchParams;
  const hasToken = Boolean(await getPasswordResetToken());

  if (isPasswordResetLinkError(motivo) || !hasToken) {
    return (
      <AuthShell title="Elige una contraseña nueva">
        <PasswordResetLinkErrorNotice
          reason={isPasswordResetLinkError(motivo) ? motivo : "invalido"}
        />
      </AuthShell>
    );
  }

  return (
    <AuthShell
      title="Elige una contraseña nueva"
      intro="Al cambiarla se cerrarán las sesiones abiertas en todos tus dispositivos."
    >
      <PasswordResetForm action={resetPassword} />
    </AuthShell>
  );
}
