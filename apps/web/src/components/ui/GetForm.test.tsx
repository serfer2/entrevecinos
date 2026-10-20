import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { GetForm } from "./GetForm";

describe("GetForm", () => {
  it("deshabilita los campos vacíos al enviar (no llegan a la URL) y después los rehabilita", () => {
    vi.useFakeTimers();
    render(
      <GetForm action="/x" onSubmit={(event) => event.preventDefault()}>
        <input name="q" defaultValue="" aria-label="q" />
        <select name="type" defaultValue="sell" aria-label="type">
          <option value="">Todos</option>
          <option value="sell">Vendo</option>
        </select>
        <button type="submit">Aplicar</button>
      </GetForm>,
    );
    const q = screen.getByLabelText("q") as HTMLInputElement;
    const type = screen.getByLabelText("type") as HTMLSelectElement;

    fireEvent.submit(screen.getByRole("button").closest("form")!);

    expect([q.disabled, type.disabled]).toEqual([true, false]);
    vi.runAllTimers();
    expect(q.disabled).toBe(false);
    vi.useRealTimers();
  });
});
