"use client";

import type { FormHTMLAttributes } from "react";

/**
 * Formulario GET que no envía los campos vacíos, para que la URL solo lleve lo elegido
 * (`?type=sell` en lugar de `?q=&type=sell&category_id=`). Sin JavaScript se envían todos y la
 * página los ignora igualmente.
 */
export function GetForm(props: Omit<FormHTMLAttributes<HTMLFormElement>, "method">) {
  return (
    <form
      {...props}
      method="get"
      onSubmit={(event) => {
        props.onSubmit?.(event);
        const fields = Array.from(event.currentTarget.elements).filter(
          (element): element is HTMLInputElement | HTMLSelectElement =>
            (element instanceof HTMLInputElement || element instanceof HTMLSelectElement) &&
            element.name !== "" &&
            element.value === "",
        );
        // Los campos deshabilitados no se envían; se rehabilitan tras construir la petición.
        for (const field of fields) field.disabled = true;
        setTimeout(() => {
          for (const field of fields) field.disabled = false;
        });
      }}
    />
  );
}
