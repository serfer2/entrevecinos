/** Esquema `User` de la API. */
export type ApiUser = {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  avatar_url: string | null;
  platform_role: "user" | "platform_admin";
  is_active: boolean;
  created_at: string;
};

/** Esquema `AuthResponse` de la API. */
export type AuthResponse = {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  user: ApiUser;
};

/** Esquema `RegistrationResponse` de la API. */
export type RegistrationResponse = {
  email: string;
  verification_expires_at: string;
};
