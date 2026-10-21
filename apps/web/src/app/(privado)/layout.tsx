import Link from "next/link";
import type { ReactNode } from "react";

import { NavLink } from "@/components/nav/NavLink";
import { logout } from "@/features/auth/actions";

/**
 * Cabecera común de la zona privada. No comprueba la sesión: lo hace cada página con
 * `requireUser()`, porque los layouts no se vuelven a renderizar al navegar.
 */
export default function PrivateLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-gray-200 bg-white">
        <nav
          aria-label="Principal"
          className="mx-auto flex w-full max-w-5xl flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <Link href="/inicio" className="text-lg font-semibold text-emerald-800">
            EntreVecinos
          </Link>
          <ul className="flex flex-wrap items-center gap-1">
            <li>
              <NavLink href="/comunidades" section="/comunidades">
                Comunidades
              </NavLink>
            </li>
            <li>
              <NavLink href="/perfil">Mi perfil</NavLink>
            </li>
            <li>
              {/* POST: un enlace GET permitiría cerrar la sesión desde otra web o con un prefetch. */}
              <form action={logout}>
                <button
                  type="submit"
                  className="rounded-md px-3 py-2 text-sm font-medium text-gray-700 hover:bg-emerald-50 hover:text-emerald-900"
                >
                  Cerrar sesión
                </button>
              </form>
            </li>
          </ul>
        </nav>
      </header>
      <div className="flex-1">{children}</div>
    </div>
  );
}
