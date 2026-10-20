type CspOptions = {
  nonce: string;
  isDev: boolean;
  /** Origen de las URL prefirmadas de las imágenes (p. ej. `http://localhost:9000`). */
  storageOrigin: string;
};

/** Origen (`esquema://host:puerto`) de una URL; lanza si no es válida. */
export function originOf(url: string | undefined): string {
  if (!url) throw new Error("STORAGE_PUBLIC_URL no está definida (origen de las imágenes para la CSP)");
  return new URL(url).origin;
}

/** Content-Security-Policy de la web (TK-046). Función pura, probada aparte del *Proxy*. */
export function buildCsp({ nonce, isDev, storageOrigin }: CspOptions): string {
  const directives = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ""}`,
    // En desarrollo, React y la recarga en caliente inyectan estilos sin nonce.
    `style-src 'self' ${isDev ? "'unsafe-inline'" : `'nonce-${nonce}'`}`,
    // Las imágenes llegan por /media/<id> → 302 a la URL prefirmada del almacenamiento.
    `img-src 'self' data: ${storageOrigin}`,
    "font-src 'self'",
    `connect-src 'self'${isDev ? " ws:" : ""}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    // Solo en producción y con el almacenamiento en HTTPS: con imágenes en http://localhost:9000
    // (imagen de producción probada en local) la mejora a HTTPS las rompería.
    ...(!isDev && storageOrigin.startsWith("https:") ? ["upgrade-insecure-requests"] : []),
  ];
  return directives.join("; ");
}
