import "server-only";

import { cache } from "react";

import { userApiFetch } from "@/features/auth/api";

import type { ApiCategory } from "./types";

export const getCategories = cache(async (): Promise<ApiCategory[]> => {
  const result = await userApiFetch<{ items: ApiCategory[] }>("/categories");
  if (result.ok) return result.data.items;
  throw new Error(`No se pudieron cargar las categorías (estado ${result.error.status})`);
});
