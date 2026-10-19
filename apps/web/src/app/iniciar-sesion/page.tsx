import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { login } from "@/features/auth/actions";
import { LoginForm } from "@/features/auth/components/LoginForm";
import { getCurrentUser } from "@/features/auth/dal";
import { safeNextPath } from "@/features/auth/redirect";
import { HOME_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Iniciar sesión · EntreVecinos" };

type LoginPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = await searchParams;
  const next = safeNextPath(params.next) ?? undefined;

  // Con una sesión válida no tiene sentido volver a iniciarla. Si la API falla, se muestra el formulario.
  if (await getCurrentUser().catch(() => null)) redirect(HOME_PATH);

  const notice =
    params.motivo === "sesion-caducada"
      ? "Tu sesión ha caducado. Vuelve a iniciar sesión."
      : undefined;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-12">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Inicia sesión</h1>
      <LoginForm action={login} next={next} notice={notice} />
    </main>
  );
}
