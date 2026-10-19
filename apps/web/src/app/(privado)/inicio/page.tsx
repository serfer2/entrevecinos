import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";

export const metadata: Metadata = { title: "Inicio · EntreVecinos" };

export default async function HomePage() {
  const user = await requireUser();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-12">
      <h1 className="text-2xl font-semibold text-gray-900">Hola, {user.full_name}</h1>
      <Link href="/perfil" className="mt-4 font-medium text-emerald-800 underline">
        Mi perfil
      </Link>
    </main>
  );
}
