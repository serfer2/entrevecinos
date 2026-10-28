import type { ReactNode } from "react";

import { BrandMark } from "@/components/brand/BrandMark";

type AuthShellProps = {
  title: string;
  /** Frase breve bajo el título. */
  intro?: string;
  children: ReactNode;
};

/** Marco de las páginas públicas (inicio de sesión, registro, validación del correo). */
export function AuthShell({ title, intro, children }: AuthShellProps) {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center gap-6 px-4 py-12">
      <div className="flex flex-col items-center gap-2 text-center">
        <BrandMark size="lg" />
        <p className="text-sm text-gray-600">Compra, Vende, ofrece y regala entre vecinos.</p>
      </div>
      <div className="flex flex-col gap-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
          {intro && <p className="text-gray-600">{intro}</p>}
        </div>
        {children}
      </div>
    </main>
  );
}
