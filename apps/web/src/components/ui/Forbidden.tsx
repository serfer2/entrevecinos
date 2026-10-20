import Link from "next/link";

type ForbiddenProps = {
  message: string;
  backHref?: string;
  backLabel?: string;
};

/** Aviso común para las páginas a las que la API responde 403. */
export function Forbidden({ message, backHref = "/inicio", backLabel = "Volver al inicio" }: ForbiddenProps) {
  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-4 px-4 py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Sin permisos</h1>
      <p role="alert" className="text-gray-700">
        {message}
      </p>
      <Link href={backHref} className="font-medium text-emerald-800 underline">
        {backLabel}
      </Link>
    </main>
  );
}
