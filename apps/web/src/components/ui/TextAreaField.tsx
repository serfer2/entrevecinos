import type { TextareaHTMLAttributes } from "react";

type TextAreaFieldProps = {
  name: string;
  label: string;
  error?: string;
  hint?: string;
} & Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "name" | "id">;

/** Área de texto con la misma accesibilidad que `TextField`. */
export function TextAreaField({ name, label, error, hint, rows = 4, ...props }: TextAreaFieldProps) {
  const id = `field-${name}`;
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-gray-900">
        {label}
      </label>
      <textarea
        id={id}
        name={name}
        rows={rows}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className="w-full min-w-0 rounded-lg border border-gray-300 bg-white px-3 py-2 text-base text-gray-900 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 aria-invalid:border-red-600"
        {...props}
      />
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
