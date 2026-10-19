"use server";

import { redirect } from "next/navigation";

import { invalidBodyFields } from "@/lib/api/errors";
import { apiFetch } from "@/lib/api/server";

import { safeNextPath } from "./redirect";
import { HOME_PATH } from "./routes";
import {
  fieldErrorsOf,
  LOGIN_MESSAGES,
  type LoginField,
  loginSchema,
  SIGNUP_FIELD_MESSAGES,
  signupSchema,
  type SignupField,
} from "./schemas";
import { createSession } from "./session";
import type { AuthResponse } from "./types";

export type SignupState =
  | {
      fieldErrors?: Partial<Record<SignupField, string>>;
      formError?: string;
      /** Valores a conservar en el formulario. Nunca incluye la contraseña. */
      values?: { full_name: string; email: string; phone: string };
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

  const result = await apiFetch<AuthResponse>("/auth/register", {
    method: "POST",
    body: parsed.data,
  });

  if (!result.ok) {
    if (result.error.status === 409) {
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

  await createSession(result.data.access_token, result.data.expires_in);
  redirect(HOME_PATH);
}

export type LoginState =
  | {
      fieldErrors?: Partial<Record<LoginField, string>>;
      formError?: string;
      /** Valores a conservar en el formulario. Nunca incluye la contraseña. */
      values?: { email: string };
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
  redirect(safeNextPath(formData.get("next")) ?? HOME_PATH);
}
