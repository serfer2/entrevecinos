import type { Metadata } from "next";

import { signup } from "@/features/auth/actions";
import { SignupForm } from "@/features/auth/components/SignupForm";

export const metadata: Metadata = { title: "Crear cuenta · EntreVecinos" };

export default function SignupPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-12">
      <h1 className="mb-6 text-2xl font-semibold text-gray-900">Crea tu cuenta</h1>
      <SignupForm action={signup} />
    </main>
  );
}
