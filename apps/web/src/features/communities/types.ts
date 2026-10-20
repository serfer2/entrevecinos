/** Esquema `Community` de la API. */
export type ApiCommunity = {
  id: string;
  name: string;
  description: string | null;
  postal_code: string | null;
  city: string | null;
  created_by: string;
  is_active: boolean;
  created_at: string;
};
