import type { InputHTMLAttributes } from "react";

type TextFieldProps = {
  name: string;
  label: string;
  error?: string;
  hint?: string;
  /** Unidad visible dentro del campo, a la derecha (p. ej. «€»). Decorativa: explícala en `hint`. */
  suffix?: string;
} & Omit<InputHTMLAttributes<HTMLInputElement>, "name" | "id">;

/** Campo de formulario con etiqueta, ayuda y error enlazados para lectores de pantalla. */
export function TextField({ name, label, error, hint, suffix, ...inputProps }: TextFieldProps) {
  const id = `field-${name}`;
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-gray-900">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          name={name}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={`w-full min-w-0 rounded-lg border border-gray-300 bg-white py-2 pl-3 text-base text-gray-900 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 aria-invalid:border-red-600 ${suffix ? "pr-9" : "pr-3"}`}
          {...inputProps}
        />
        {suffix && (
          <span aria-hidden className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-gray-600">
            {suffix}
          </span>
        )}
      </div>
      {hint && (
        <p id={hintId} className="text-sm text-gray-600">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
