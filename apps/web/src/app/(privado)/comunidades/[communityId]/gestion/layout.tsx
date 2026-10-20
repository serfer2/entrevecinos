import type { ReactNode } from "react";

import { NavLink } from "@/components/nav/NavLink";

type ManagementLayoutProps = {
  children: ReactNode;
  params: Promise<{ communityId: string }>;
};

const tabClass =
  "border-b-2 border-transparent px-3 py-2 text-sm font-medium text-gray-700 hover:text-emerald-900 aria-[current=page]:border-emerald-700 aria-[current=page]:text-emerald-900";

/** Pestañas de la gestión de la comunidad. Cada página comprueba los permisos (403 de la API). */
export default async function ManagementLayout({ children, params }: ManagementLayoutProps) {
  const { communityId } = await params;
  const base = `/comunidades/${communityId}/gestion`;

  return (
    <div className="flex flex-col">
      <nav aria-label="Gestión de la comunidad" className="mx-auto w-full max-w-3xl px-4 pt-6">
        <ul className="flex gap-2 border-b border-gray-200">
          <li>
            <NavLink href={`${base}/solicitudes`} className={tabClass}>
              Solicitudes
            </NavLink>
          </li>
          <li>
            <NavLink href={`${base}/miembros`} className={tabClass}>
              Miembros
            </NavLink>
          </li>
        </ul>
      </nav>
      {children}
    </div>
  );
}
