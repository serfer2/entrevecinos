import Link from "next/link";

export default function CommunityNotFound() {
  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-4 px-4 py-10">
      <h1 className="text-2xl font-semibold text-gray-900">Comunidad no encontrada</h1>
      <p className="text-gray-700">Esta comunidad no existe o ya no está disponible.</p>
      <Link href="/inicio" className="font-medium text-emerald-800 underline">
        Volver al inicio
      </Link>
    </main>
  );
}
