import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AuthShell } from "@/components/ui/AuthShell";
import { requestPasswordReset } from "@/features/auth/actions";
import { PasswordResetRequestForm } from "@/features/auth/components/PasswordResetRequestForm";
import { getCurrentUser } from "@/features/auth/dal";
import { HOME_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Recuperar contraseña · EntreVecinos" };

type PasswordResetRequestPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function PasswordResetRequestPage({
  searchParams,
}: PasswordResetRequestPageProps) {
  // Con una sesión válida no hace falta recuperar nada. Si la API falla, se muestra el formulario.
  if (await getCurrentUser().catch(() => null)) redirect(HOME_PATH);

  const params = await searchParams;
  const email = typeof params.email === "string" ? params.email.slice(0, 320) : undefined;

  return (
    <AuthShell
      title="Recupera tu contraseña"
      intro="Escribe el correo de tu cuenta y te enviaremos un enlace para elegir una contraseña nueva."
    >
      <PasswordResetRequestForm action={requestPasswordReset} defaultEmail={email} />
    </AuthShell>
  );
}
