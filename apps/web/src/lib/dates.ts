const LONG_DATE = new Intl.DateTimeFormat("es-ES", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "Europe/Madrid",
});

/** «20 de octubre de 2026». */
export function formatLongDate(iso: string): string {
  return LONG_DATE.format(new Date(iso));
}
