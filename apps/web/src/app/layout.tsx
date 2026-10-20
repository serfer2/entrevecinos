import type { Metadata } from "next";
import { connection } from "next/server";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "EntreVecinos",
};

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  // La CSP usa un nonce por petición (src/proxy.ts): todas las páginas se renderizan por petición.
  await connection();

  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
