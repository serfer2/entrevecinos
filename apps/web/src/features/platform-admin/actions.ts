"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import type { ApiCommunity } from "@/features/communities/types";
import { formText, isUuid } from "@/lib/forms";

import { PENDING_COMMUNITIES_PATH, pendingCommunitiesPath } from "./paths";

/** Aprueba (activa) una comunidad pendiente y vuelve a la lista con el resultado en la URL. */
export async function approveCommunity(formData: FormData): Promise<void> {
  await requireUser();

  const communityId = formText(formData, "community_id");
  if (!isUuid(communityId)) redirect(pendingCommunitiesPath("error"));

  const result = await userApiFetch<ApiCommunity>(`/admin/communities/${communityId}`, {
    method: "PATCH",
    body: { is_active: true },
  });

  revalidatePath(PENDING_COMMUNITIES_PATH);
  revalidatePath("/inicio");
  redirect(pendingCommunitiesPath(result.ok ? "aprobada" : "error"));
}
