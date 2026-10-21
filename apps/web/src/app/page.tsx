import { redirect } from "next/navigation";

import { getCurrentUser } from "@/features/auth/dal";
import { HOME_PATH, LOGIN_PATH } from "@/features/auth/routes";

// La raíz no tiene contenido propio: con sesión lleva al inicio y sin ella, al inicio de sesión.
export default async function Home() {
  // Si la API falla, se trata como sin sesión (igual que en /iniciar-sesion).
  const user = await getCurrentUser().catch(() => null);
  redirect(user ? HOME_PATH : LOGIN_PATH);
}
