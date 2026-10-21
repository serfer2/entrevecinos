import type { Metadata } from "next";
import Link from "next/link";

import { resendVerification } from "@/features/auth/actions";
import { ResendVerificationButton } from "@/features/auth/components/ResendVerificationButton";
import { LOGIN_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Validar el correo · EntreVecinos" };

const MESSAGES: Record<string, string> = {
  caducado: "El enlace de validación ha caducado.",
  invalido: "El enlace de validación no es válido.",
  error: "No hemos podido validar tu correo. Inténtalo de nuevo más tarde.",
};

const linkClass = "text-sm font-medium text-emerald-800 underline";

type VerifyEmailErrorPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function VerifyEmailErrorPage({ searchParams }: VerifyEmailErrorPageProps) {
  const params = await searchParams;
  const reason =
    typeof params.motivo === "string" && params.motivo in MESSAGES ? params.motivo : "invalido";
  const email = typeof params.email === "string" && params.email ? params.email : null;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-4 px-4 py-12">
      <h1 className="text-2xl font-semibold text-gray-900">Validar el correo</h1>
      <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-800">
        {MESSAGES[reason]}
      </p>
      {reason !== "caducado" ? (
        <Link href={LOGIN_PATH} className={linkClass}>
          Ir a iniciar sesión
        </Link>
      ) : email ? (
        <ResendVerificationButton email={email} action={resendVerification} />
      ) : (
        <Link href="/registro" className={linkClass}>
          Ir al registro
        </Link>
      )}
    </main>
  );
}
