import type { Metadata } from "next";
import Link from "next/link";

import { AuthShell } from "@/components/ui/AuthShell";
import { resendVerification } from "@/features/auth/actions";
import { ResendVerificationButton } from "@/features/auth/components/ResendVerificationButton";
import { LOGIN_PATH } from "@/features/auth/routes";

export const metadata: Metadata = { title: "Validar el correo · EntreVecinos" };

const MESSAGES: Record<string, string> = {
  caducado: "El enlace de validación ha caducado.",
  reemplazado:
    "Este enlace ya no es válido porque te hemos enviado uno más reciente. Abre el enlace del último correo que has recibido.",
  invalido: "El enlace de validación no es válido.",
  error: "No hemos podido validar tu correo. Inténtalo de nuevo más tarde.",
};

// Motivos en los que la cuenta sigue pendiente: se ofrece recibir otro enlace.
const RESENDABLE = new Set(["caducado", "reemplazado"]);

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
    <AuthShell title="Validar el correo">
      <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
        {MESSAGES[reason]}
      </p>
      {!RESENDABLE.has(reason) ? (
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
      {/* La raíz lleva a /inicio con sesión o al inicio de sesión sin ella. */}
      <Link href="/" className={linkClass}>
        Volver al inicio
      </Link>
    </AuthShell>
  );
}
