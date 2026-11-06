import Link from "next/link";
import type { ReactNode } from "react";

import { BrandMark } from "@/components/brand/BrandMark";
import { NavLink } from "@/components/nav/NavLink";
import { logout } from "@/features/auth/actions";

/**
 * Cabecera común de la zona privada. No comprueba la sesión: lo hace cada página con
 * `requireUser()`, porque los layouts no se vuelven a renderizar al navegar.
 */
export default function PrivateLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="z-20 border-b sm:sticky sm:top-0 border-gray-200 bg-gray-50/90 backdrop-blur">
        <nav
          aria-label="Principal"
          className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <Link href="/inicio" className="self-start no-underline sm:self-auto">
            <BrandMark />
          </Link>
          <ul className="-mx-3 flex flex-wrap items-center gap-1 sm:mx-0">
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
                  className="rounded-full px-3 py-2 text-sm font-medium text-gray-700 hover:bg-emerald-50 hover:text-emerald-900"
                >
                  Cerrar sesión
                </button>
              </form>
            </li>
          </ul>
        </nav>
      </header>
      <div className="flex-1">{children}</div>
      <footer className="border-t border-gray-200">
        <p className="mx-auto w-full max-w-6xl px-4 py-6 text-sm text-gray-600">
          EntreVecinos · Dale una segunda vida a las cosas, cerca de casa.
        </p>
      </footer>
    </div>
  );
}
