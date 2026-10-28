"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

type NavLinkProps = {
  href: string;
  children: ReactNode;
  /** Prefijo de ruta que también marca el enlace como actual (p. ej. `/comunidades`). */
  section?: string;
  className?: string;
};

/** Enlace de navegación que marca la sección actual con `aria-current="page"`. */
export function NavLink({ href, children, section, className }: NavLinkProps) {
  const pathname = usePathname();
  const prefix = section ?? href;
  const current = pathname === href || pathname.startsWith(`${prefix}/`) || pathname === prefix;

  return (
    <Link
      href={href}
      aria-current={current ? "page" : undefined}
      className={
        className ??
        "rounded-full px-3 py-2 text-sm font-medium text-gray-700 no-underline hover:bg-emerald-50 hover:text-emerald-900 aria-[current=page]:bg-emerald-100 aria-[current=page]:text-emerald-900"
      }
    >
      {children}
    </Link>
  );
}
