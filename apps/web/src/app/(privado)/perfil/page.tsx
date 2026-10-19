import type { Metadata } from "next";
import Link from "next/link";

import { requireUser } from "@/features/auth/dal";
import { updateProfile } from "@/features/profile/actions";
import { ProfileForm } from "@/features/profile/components/ProfileForm";

export const metadata: Metadata = { title: "Mi perfil · EntreVecinos" };

export default async function ProfilePage() {
  const user = await requireUser();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col gap-8 px-4 py-12">
      <div>
        <Link href="/inicio" className="text-sm font-medium text-emerald-800 underline">
          Volver al inicio
        </Link>
        <h1 className="mt-4 text-2xl font-semibold text-gray-900">Mi perfil</h1>
      </div>

      <section aria-labelledby="saved-data">
        <h2 id="saved-data" className="mb-3 text-lg font-medium text-gray-900">
          Tus datos
        </h2>
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <dt className="text-gray-600">Nombre</dt>
          <dd className="text-gray-900">{user.full_name}</dd>
          <dt className="text-gray-600">Correo</dt>
          <dd className="text-gray-900">
            {user.email}
            <span className="block text-gray-600">El correo no se puede cambiar</span>
          </dd>
          <dt className="text-gray-600">Teléfono</dt>
          <dd className="text-gray-900">{user.phone ?? "Sin teléfono"}</dd>
        </dl>
      </section>

      <section aria-labelledby="edit-data">
        <h2 id="edit-data" className="mb-3 text-lg font-medium text-gray-900">
          Editar datos de contacto
        </h2>
        <ProfileForm
          action={updateProfile}
          initialValues={{ full_name: user.full_name, phone: user.phone }}
        />
      </section>
    </main>
  );
}
