import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Pagination } from "./Pagination";

const hrefFor = (page: number) => `/lista?page=${page}`;

describe("Pagination", () => {
  it("no se muestra con una sola página", () => {
    const { container } = render(<Pagination page={1} pageSize={20} total={5} hrefFor={hrefFor} />);

    expect(container.innerHTML).toBe("");
  });

  it("primera página: solo «Siguiente»", () => {
    render(<Pagination page={1} pageSize={10} total={25} hrefFor={hrefFor} />);

    expect(screen.getByRole("navigation", { name: "Paginación" })).toBeTruthy();
    expect(screen.getByText("Página 1 de 3")).toBeTruthy();
    expect(screen.queryByRole("link", { name: "Anterior" })).toBeNull();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/lista?page=2");
  });

  it("página intermedia: ambos enlaces", () => {
    render(<Pagination page={2} pageSize={10} total={25} hrefFor={hrefFor} />);

    expect(screen.getByRole("link", { name: "Anterior" }).getAttribute("href")).toBe("/lista?page=1");
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/lista?page=3");
  });

  it("última página: solo «Anterior»", () => {
    render(<Pagination page={3} pageSize={10} total={25} hrefFor={hrefFor} />);

    expect(screen.getByRole("link", { name: "Anterior" })).toBeTruthy();
    expect(screen.queryByRole("link", { name: "Siguiente" })).toBeNull();
  });

  it("más allá del final: vuelve a la última", () => {
    render(<Pagination page={9} pageSize={10} total={25} hrefFor={hrefFor} />);

    expect(screen.getByRole("link", { name: "Anterior" }).getAttribute("href")).toBe("/lista?page=3");
  });
});
