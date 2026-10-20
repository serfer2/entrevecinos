import type { Metadata } from "next";

import { requireUser } from "@/features/auth/dal";
import { createCommunity } from "@/features/communities/actions";
import { CommunityForm } from "@/features/communities/components/CommunityForm";

export const metadata: Metadata = { title: "Crear comunidad · EntreVecinos" };

export default async function NewCommunityPage() {
  await requireUser();

  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Crear una comunidad</h1>
        <p className="mt-2 text-gray-700">
          Serás su administrador y podrás aprobar a los vecinos que pidan unirse.
        </p>
      </div>
      <CommunityForm action={createCommunity} />
    </main>
  );
}
