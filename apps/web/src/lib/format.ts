const TIME_ZONE = "Europe/Madrid";
const DAY_MS = 24 * 60 * 60 * 1000;

/** «45,50 €». `null` si no hay precio. */
export function formatPrice(price: number | null, currency: string | null): string | null {
  if (price === null) return null;
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: currency ?? "EUR" }).format(price);
}

function madridDay(date: Date): number {
  const [year, month, day] = new Intl.DateTimeFormat("en-CA", { timeZone: TIME_ZONE })
    .format(date)
    .split("-")
    .map(Number);
  return Date.UTC(year, month - 1, day) / DAY_MS;
}

/** «hoy», «ayer», «hace 3 días» durante una semana; después «12 oct.» (con año si no es el actual). */
export function formatPublishedAt(iso: string, now: Date = new Date()): string {
  const date = new Date(iso);
  const days = madridDay(now) - madridDay(date);
  if (days <= 0) return "hoy";
  if (days === 1) return "ayer";
  if (days < 7) return `hace ${days} días`;
  const sameYear =
    new Intl.DateTimeFormat("es-ES", { timeZone: TIME_ZONE, year: "numeric" }).format(date) ===
    new Intl.DateTimeFormat("es-ES", { timeZone: TIME_ZONE, year: "numeric" }).format(now);
  return new Intl.DateTimeFormat("es-ES", {
    timeZone: TIME_ZONE,
    day: "numeric",
    month: "short",
    ...(sameYear ? {} : { year: "numeric" }),
  }).format(date);
}
