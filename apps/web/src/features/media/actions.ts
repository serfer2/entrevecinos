"use server";

import { userApiFetch } from "@/features/auth/api";
import { requireUser } from "@/features/auth/dal";
import { IMAGE_MESSAGES, imageFileError } from "@/lib/media";

export type UploadImageResult = { id: string } | { error: string };

type ApiMediaAsset = { id: string; url: string };

/** Sube una imagen a la API (una por llamada, para no superar el límite de las Server Actions). */
export async function uploadImage(formData: FormData): Promise<UploadImageResult> {
  await requireUser();

  const file = formData.get("file");
  if (!(file instanceof File)) return { error: IMAGE_MESSAGES.type };
  const invalid = imageFileError(file);
  if (invalid) return { error: invalid };

  const body = new FormData();
  body.set("file", file, file.name);
  const result = await userApiFetch<ApiMediaAsset>("/media", { method: "POST", body });
  if (result.ok) return { id: result.data.id };
  if (result.error.status === 413) return { error: IMAGE_MESSAGES.too_large };
  if (result.error.status === 415 || result.error.status === 422) return { error: IMAGE_MESSAGES.type };
  return { error: IMAGE_MESSAGES.error };
}
