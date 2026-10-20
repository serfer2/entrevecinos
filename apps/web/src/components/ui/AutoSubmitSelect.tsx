"use client";

import type { ComponentProps } from "react";

import { SelectField } from "./SelectField";

/**
 * `SelectField` que envía su formulario al cambiar (mejora progresiva: sin JavaScript se usa el
 * botón del formulario).
 */
export function AutoSubmitSelect(props: ComponentProps<typeof SelectField>) {
  return (
    <SelectField
      {...props}
      onChange={(event) => {
        props.onChange?.(event);
        event.currentTarget.form?.requestSubmit();
      }}
    />
  );
}
