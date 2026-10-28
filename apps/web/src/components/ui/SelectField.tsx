import type { SelectHTMLAttributes } from "react";

type SelectFieldProps = {
  name: string;
  label: string;
  options: { value: string; label: string }[];
  /** Opción vacía inicial (p. ej. «Elige una categoría»). */
  placeholder?: string;
  error?: string;
  id?: string;
} & Omit<SelectHTMLAttributes<HTMLSelectElement>, "name" | "id">;

/** Desplegable con etiqueta y error accesibles, como `TextField`. */
export function SelectField({ name, label, options, placeholder, error, id, ...props }: SelectFieldProps) {
  const fieldId = id ?? `field-${name}`;
  const errorId = error ? `${fieldId}-error` : undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={fieldId} className="text-sm font-medium text-gray-900">
        {label}
      </label>
      <select
        id={fieldId}
        name={name}
        aria-invalid={error ? true : undefined}
        aria-describedby={errorId}
        className="w-full min-w-0 rounded-lg border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 aria-invalid:border-red-600"
        {...props}
      >
        {placeholder !== undefined && <option value="">{placeholder}</option>}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p id={errorId} className="text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
