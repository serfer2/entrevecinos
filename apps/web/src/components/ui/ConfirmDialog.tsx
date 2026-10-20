"use client";

import { type ReactNode, useId, useRef } from "react";

type ConfirmDialogProps = {
  /** Acción del formulario (normalmente una Server Action). */
  action: (formData: FormData) => void | Promise<void>;
  /** Campos ocultos del formulario. */
  children?: ReactNode;
  triggerLabel: string;
  title: string;
  message: string;
  confirmLabel: string;
  triggerClassName?: string;
};

const buttonClass = "rounded-md px-3 py-1.5 text-sm font-medium";

/**
 * Botón que pide confirmación antes de enviar su formulario. Con JavaScript abre un `<dialog>`
 * modal (atrapa el foco y lo devuelve al botón al cerrarse); sin JavaScript envía directamente.
 */
export function ConfirmDialog({
  action,
  children,
  triggerLabel,
  title,
  message,
  confirmLabel,
  triggerClassName = `${buttonClass} border border-red-700 text-red-800 hover:bg-red-50`,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const messageId = useId();

  return (
    <form action={action}>
      {children}
      <button
        type="submit"
        className={triggerClassName}
        onClick={(event) => {
          event.preventDefault();
          dialogRef.current?.showModal();
        }}
      >
        {triggerLabel}
      </button>
      <dialog
        ref={dialogRef}
        aria-labelledby={titleId}
        aria-describedby={messageId}
        className="m-auto max-w-sm rounded-lg p-6 shadow-xl backdrop:bg-black/40"
      >
        <h2 id={titleId} className="text-lg font-semibold text-gray-900">
          {title}
        </h2>
        <p id={messageId} className="mt-2 text-gray-700">
          {message}
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <button
            type="button"
            autoFocus
            onClick={() => dialogRef.current?.close()}
            className={`${buttonClass} border border-gray-300 text-gray-800 hover:bg-gray-50`}
          >
            Cancelar
          </button>
          <button type="submit" className={`${buttonClass} bg-red-700 text-white hover:bg-red-800`}>
            {confirmLabel}
          </button>
        </div>
      </dialog>
    </form>
  );
}
