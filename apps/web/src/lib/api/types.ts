/** Respuesta paginada común de la API (`PageMeta` + `items`). */
export type ApiPage<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
};
