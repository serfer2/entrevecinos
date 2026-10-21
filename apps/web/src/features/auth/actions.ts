"use server";

import { redirect } from "next/navigation";

import { errorCodeOf, invalidBodyFields } from "@/lib/api/errors";
import { apiFetch } from "@/lib/api/server";

import { postLoginPath } from "./destination";
import { safeNextPath } from "./redirect";
import {
  fieldErrorsOf,
  LOGIN_MESSAGES,
  type LoginField,
  loginSchema,
  SIGNUP_FIELD_MESSAGES,
  signupSchema,
  type SignupField,
} from "./schemas";
import { createSession, deleteSession } from "./session";
import type { AuthResponse, RegistrationResponse } from "./types";

export type SignupState =
  | {
      fieldErrors?: Partial<Record<SignupField, string>>;
      formError?: string;
      /** Valores a conservar en el formulario. Nunca incluye la contraseña. */
      values?: { full_name: string; email: string; phone: string };
      /** Cuenta creada: correo al que se ha enviado el enlace de validación. */
      verificationSentTo?: string;
      /** El correo pertenece a una cuenta pendiente de validar: se ofrece el reenvío. */
      pendingVerification?: boolean;
    }
  | undefined;

function text(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

export async function signup(_state: SignupState, formData: FormData): Promise<SignupState> {
  const values = {
    full_name: text(formData, "full_name"),
    email: text(formData, "email"),
    phone: text(formData, "phone"),
  };

  const parsed = signupSchema.safeParse({ ...values, password: text(formData, "password") });
  if (!parsed.success) {
    return { fieldErrors: fieldErrorsOf<SignupField>(parsed.error), values };
  }

  const result = await apiFetch<RegistrationResponse>("/auth/register", {
    method: "POST",
    body: parsed.data,
  });

  if (!result.ok) {
    if (result.error.status === 409) {
      if (errorCodeOf(result.error) === "email_pending_verification") {
        return {
          fieldErrors: { email: "Este correo está pendiente de validación." },
          pendingVerification: true,
          values,
        };
      }
      return { fieldErrors: { email: "Este correo ya está en uso." }, values };
    }
    if (result.error.status === 422) {
      const fieldErrors: Partial<Record<SignupField, string>> = {};
      for (const field of invalidBodyFields(result.error)) {
        if (field in SIGNUP_FIELD_MESSAGES) {
          fieldErrors[field as SignupField] = SIGNUP_FIELD_MESSAGES[field as SignupField];
        }
      }
      if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
    }
    return { formError: "No se pudo crear la cuenta. Inténtalo de nuevo.", values };
  }

  // La cuenta se activa al abrir el enlace del correo (/verificar-correo): aún no hay sesión.
  return { verificationSentTo: result.data.email };
}

export type LoginState =
  | {
      fieldErrors?: Partial<Record<LoginField, string>>;
      formError?: string;
      /** Valores a conservar en el formulario. Nunca incluye la contraseña. */
      values?: { email: string };
      /** Credenciales correctas, pero falta validar el correo. */
      emailNotVerified?: boolean;
    }
  | undefined;

export async function login(_state: LoginState, formData: FormData): Promise<LoginState> {
  const values = { email: text(formData, "email") };

  const parsed = loginSchema.safeParse({ ...values, password: text(formData, "password") });
  if (!parsed.success) {
    return { fieldErrors: fieldErrorsOf<LoginField>(parsed.error), values };
  }

  const result = await apiFetch<AuthResponse>("/auth/token", {
    method: "POST",
    body: parsed.data,
  });

  if (!result.ok) {
    if (result.error.status === 401) {
      // Mensaje genérico: no revela si falló el correo o la contraseña.
      return { formError: "Correo o contraseña incorrectos.", values };
    }
    if (result.error.status === 403 && errorCodeOf(result.error) === "email_not_verified") {
      return {
        formError: "Tienes que validar tu correo electrónico antes de iniciar sesión.",
        emailNotVerified: true,
        values,
      };
    }
    if (result.error.status === 422) {
      const fieldErrors: Partial<Record<LoginField, string>> = {};
      for (const field of invalidBodyFields(result.error)) {
        if (field in LOGIN_MESSAGES) fieldErrors[field as LoginField] = LOGIN_MESSAGES[field as LoginField];
      }
      if (Object.keys(fieldErrors).length > 0) return { fieldErrors, values };
    }
    return { formError: "No se pudo iniciar sesión. Inténtalo de nuevo.", values };
  }

  await createSession(result.data.access_token, result.data.expires_in);
  redirect(safeNextPath(formData.get("next")) ?? (await postLoginPath(result.data.access_token)));
}

export type ResendVerificationState = { sent?: boolean; error?: string } | undefined;

/** Pide otro enlace de validación. La API responde igual exista o no la cuenta pendiente. */
export async function resendVerification(
  _state: ResendVerificationState,
  formData: FormData,
): Promise<ResendVerificationState> {
  const result = await apiFetch("/auth/email-verification/resend", {
    method: "POST",
    body: { email: text(formData, "email") },
  });
  if (!result.ok) return { error: "No se pudo reenviar el correo. Inténtalo de nuevo." };
  return { sent: true };
}

/** Cierra la sesión y va a la raíz, que lleva al inicio de sesión. Se envía por POST. */
export async function logout(): Promise<void> {
  // Borrar la cookie en una Server Action invalida también la caché del router del cliente.
  await deleteSession();
  redirect("/");
}
