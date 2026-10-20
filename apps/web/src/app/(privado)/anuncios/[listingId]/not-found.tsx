import Link from "next/link";

export default function ListingNotFound() {
  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-4 px-4 py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Anuncio no disponible</h1>
      <p className="text-gray-700">Este anuncio no está disponible. Puede que se haya eliminado o retirado.</p>
      <Link href="/inicio" className="font-medium text-emerald-800 underline">
        Mis comunidades
      </Link>
    </main>
  );
}
