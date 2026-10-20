import type { ListingType } from "./labels";

export type ListingStatus = "active" | "reserved" | "completed" | "hidden";

/** Esquema `Category` de la API. */
export type ApiCategory = { id: string; name: string; slug: string; is_active: boolean };

/** Esquema `Listing` de la API. */
export type ApiListing = {
  id: string;
  community_id: string;
  owner: {
    id: string;
    full_name: string;
    phone: string | null;
    email?: string | null;
    avatar_url: string | null;
  };
  category_id: string;
  title: string;
  description: string;
  type: ListingType;
  price: number | null;
  currency: string | null;
  images: { asset_id: string; url: string; position: number; is_cover: boolean }[];
  status: ListingStatus;
  published_at: string;
  updated_at: string;
};
