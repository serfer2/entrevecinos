/** Logotipo: un brote (lo que crece entre vecinos) junto al nombre. Decorativo salvo el texto. */
export function BrandMark({ size = "md" }: { size?: "md" | "lg" }) {
  const large = size === "lg";

  return (
    <span className="inline-flex items-center gap-2">
      <span
        aria-hidden
        className={`flex items-center justify-center rounded-full bg-emerald-700 text-emerald-50 ${large ? "h-10 w-10" : "h-8 w-8"}`}
      >
        <svg viewBox="0 0 24 24" className={large ? "h-6 w-6" : "h-5 w-5"} fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 20v-8" />
          <path d="M12 12c0-3.5-2.5-6-6.5-6 0 3.5 2.5 6 6.5 6Z" />
          <path d="M12 14.5c0-3 2.2-5.5 6.5-5.5 0 3-2.2 5.5-6.5 5.5Z" />
        </svg>
      </span>
      <span className={`font-display font-semibold tracking-tight text-emerald-900 ${large ? "text-2xl" : "text-xl"}`}>
        EntreVecinos
      </span>
    </span>
  );
}
