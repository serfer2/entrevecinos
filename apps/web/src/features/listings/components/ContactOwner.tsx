type ContactOwnerProps = {
  owner: { full_name: string; phone: string | null; email?: string | null };
  listingTitle: string;
  isOwner: boolean;
};

/** `tel:` sin espacios ni separadores (se conserva el `+` internacional). */
export function telHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, "")}`;
}

export function mailtoHref(email: string, listingTitle: string): string {
  return `mailto:${email}?subject=${encodeURIComponent(`Interesado en: ${listingTitle}`)}`;
}

/**
 * Canal de contacto del MVP. Los datos solo llegan aquí si la API los ha autorizado (miembro
 * aprobado): el desplegable es presentación, no protección.
 */
export function ContactOwner({ owner, listingTitle, isOwner }: ContactOwnerProps) {
  if (isOwner) return <p className="mt-2 text-sm text-gray-600">Este es tu anuncio.</p>;

  return (
    <details className="group mt-3">
      <summary className="inline-flex cursor-pointer list-none rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 [&::-webkit-details-marker]:hidden">
        Contactar con {owner.full_name}
      </summary>
      <ul className="mt-3 flex flex-col gap-2">
        {owner.phone && (
          <li>
            <span className="text-sm text-gray-600">Teléfono: </span>
            <a href={telHref(owner.phone)} className="font-medium text-emerald-800 underline">
              {owner.phone}
            </a>
          </li>
        )}
        {owner.email && (
          <li>
            <span className="text-sm text-gray-600">Correo: </span>
            <a href={mailtoHref(owner.email, listingTitle)} className="break-all font-medium text-emerald-800 underline">
              {owner.email}
            </a>
          </li>
        )}
      </ul>
    </details>
  );
}
