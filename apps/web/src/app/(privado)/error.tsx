"use client";

export default function PrivateError({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-4 px-4 py-10">
      <h1 className="text-3xl font-semibold text-gray-900">Algo ha fallado</h1>
      <p role="alert" className="text-gray-700">
        No hemos podido cargar esta página. Inténtalo de nuevo en unos segundos.
      </p>
      <button
        type="button"
        onClick={reset}
        className="self-start rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800"
      >
        Reintentar
      </button>
    </main>
  );
}
