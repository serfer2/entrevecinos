"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { formText, isUuid } from "@/lib/forms";

import type { ApiMembership } from "../types";
import { requestsPath } from "./paths";

const DECISIONS = { approved: "aprobada", rejected: "rechazada" } as const;

/** Aprueba o rechaza una solicitud y vuelve a la lista con el resultado en la URL. */
export async function reviewRequest(formData: FormData): Promise<void> {
  await requireUser();

  const communityId = formText(formData, "community_id");
  const userId = formText(formData, "user_id");
  const decision = formText(formData, "decision");
  if (!isUuid(communityId) || !isUuid(userId) || !(decision in DECISIONS)) {
    redirect(isUuid(communityId) ? requestsPath(communityId, "error") : "/inicio");
  }

  const result = await userApiFetch<ApiMembership>(
    `/communities/${communityId}/memberships/${userId}`,
    { method: "PATCH", body: { status: decision } },
  );

  revalidatePath(requestsPath(communityId));
  if (result.ok) redirect(requestsPath(communityId, DECISIONS[decision as keyof typeof DECISIONS]));
  if (result.error.status === 409) redirect(requestsPath(communityId, "revisada"));
  // 403: la página vuelve a pedir la lista y muestra el aviso de permisos.
  if (result.error.status === 403) redirect(requestsPath(communityId));
  redirect(requestsPath(communityId, "error"));
}
