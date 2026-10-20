const API_MEDIA_PREFIX = "/v1/media/";

/** URL de una imagen para el navegador: la ruta de Next que añade la sesión (`/media/<id>`). */
export function mediaSrc(urlOrId: string): string {
  const id = urlOrId.startsWith(API_MEDIA_PREFIX) ? urlOrId.slice(API_MEDIA_PREFIX.length) : urlOrId;
  return `/media/${id}`;
}

export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
export const IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
export const MAX_LISTING_IMAGES = 10;

export const IMAGE_MESSAGES = {
  too_large: "La imagen supera 5 MB.",
  type: "Formato no permitido. Usa JPEG, PNG o WebP.",
  max: "Puedes adjuntar hasta 10 fotografías.",
  error: "No se pudo subir la imagen. Inténtalo de nuevo.",
} as const;

/** Comprobación previa de un fichero (la API vuelve a validar el contenido real). */
export function imageFileError(file: { size: number; type: string }): string | null {
  if (!(IMAGE_TYPES as readonly string[]).includes(file.type)) return IMAGE_MESSAGES.type;
  if (file.size > MAX_IMAGE_BYTES) return IMAGE_MESSAGES.too_large;
  if (file.size === 0) return IMAGE_MESSAGES.type;
  return null;
}
