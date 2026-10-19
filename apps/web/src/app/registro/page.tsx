import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { signup } from "@/features/auth/actions";
import { SignupForm } from "@/features/auth/components/SignupForm";
import { getCurrentUser } from "@/features/auth/dal";
import { HOME_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Crear cuenta · EntreVecinos" };

export default async function SignupPage() {
  // Con una sesión válida no tiene sentido registrarse. Si la API falla, se muestra el formulario.
  if (await getCurrentUser().catch(() => null)) redirect(HOME_PATH);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-12">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Crea tu cuenta</h1>
      <SignupForm action={signup} />
    </main>
  );
}
