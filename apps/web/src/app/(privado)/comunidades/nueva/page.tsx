import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { createCommunity } from "@/features/communities/actions";
import { CommunityForm } from "@/features/communities/components/CommunityForm";
import { getMyMemberships } from "@/features/communities/data";
import { pendingCommunityOf } from "@/features/communities/pending";

export const metadata: Metadata = { title: "Crear comunidad · EntreVecinos" };

export default async function NewCommunityPage() {
  const user = await requireUser();
  // Solo se puede tener una comunidad pendiente de aprobación a la vez.
  const pending = pendingCommunityOf(await getMyMemberships(), user.id);

  return (
    <main className="mx-auto flex w-full max-w-md flex-col gap-6 px-4 py-10">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Crear una comunidad</h1>
        {!pending && (
          <p className="mt-2 text-gray-700">
            Un administrador la revisará antes de activarla. Después serás su administrador y podrás
            aprobar a los vecinos que pidan unirse.
          </p>
        )}
      </div>
      {pending ? (
        <>
          <p role="status" className="rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-900">
            Ya tienes una comunidad pendiente de aprobación: «{pending.name}». Podrás crear otra
            cuando un administrador la revise.
          </p>
          <Link href="/inicio" className="self-start font-medium text-emerald-800 underline">
            Volver al inicio
          </Link>
        </>
      ) : (
        <CommunityForm action={createCommunity} />
      )}
    </main>
  );
}
