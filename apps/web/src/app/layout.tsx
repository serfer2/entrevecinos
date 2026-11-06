import type { Metadata } from "next";
import { Figtree, Fraunces } from "next/font/google";
import { connection } from "next/server";
import "@/styles/globals.css";

// Autoalojadas por next/font: la CSP solo admite fuentes del propio origen.
const body = Figtree({ subsets: ["latin"], variable: "--font-body", display: "swap" });
const heading = Fraunces({ subsets: ["latin"], variable: "--font-heading", display: "swap", axes: ["SOFT"] });

export const metadata: Metadata = {
  title: "EntreVecinos",
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // La CSP usa un nonce por petición (src/proxy.ts): todas las páginas se renderizan por petición.
  await connection();

  return (
    <html lang="es" className={`${body.variable} ${heading.variable}`}>
      <body>{children}</body>
    </html>
  );
}
