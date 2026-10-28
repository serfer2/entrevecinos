import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AuthShell } from "@/components/ui/AuthShell";
import { resendVerification, signup } from "@/features/auth/actions";
import { SignupForm } from "@/features/auth/components/SignupForm";
import { getCurrentUser } from "@/features/auth/dal";
import { HOME_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Crear cuenta · EntreVecinos" };

export default async function SignupPage() {
  // Con una sesión válida no tiene sentido registrarse. Si la API falla, se muestra el formulario.
  if (await getCurrentUser().catch(() => null)) redirect(HOME_PATH);

  return (
    <AuthShell title="Crea tu cuenta" intro="Únete a la comunidad de tu barrio en un par de minutos.">
      <SignupForm action={signup} resendAction={resendVerification} />
    </AuthShell>
  );
}
