import "server-only";

import { cookies } from "next/headers";

import { SESSION_COOKIE } from "./routes";

/** Guarda el JWT en una cookie httpOnly: el JavaScript del navegador nunca lo ve. */
export async function createSession(token: string, expiresIn: number): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: expiresIn,
  });
}

export async function getSessionToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE)?.value;
}
