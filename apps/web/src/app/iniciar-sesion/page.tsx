import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AuthShell } from "@/components/ui/AuthShell";
import { login, resendVerification } from "@/features/auth/actions";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { getCurrentUser } from "@/features/auth/dal";
import { safeNextPath } from "@/features/auth/redirect";
import { HOME_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Iniciar sesión · EntreVecinos" };

const NOTICES: Record<string, string> = {
  "sesion-caducada": "Tu sesión ha caducado. Vuelve a iniciar sesión.",
  "correo-validado": "Tu correo ya está validado. Inicia sesión.",
};

type LoginPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = await searchParams;
  const next = safeNextPath(params.next) ?? undefined;

  // Con una sesión válida no tiene sentido volver a iniciarla. Si la API falla, se muestra el formulario.
  if (await getCurrentUser().catch(() => null)) redirect(HOME_PATH);

  const notice = NOTICES[String(params.motivo)];

  return (
    <AuthShell title="Inicia sesión" intro="Vuelve a tu comunidad y mira qué hay cerca.">
      <LoginForm action={login} resendAction={resendVerification} next={next} notice={notice} />
    </AuthShell>
  );
}
