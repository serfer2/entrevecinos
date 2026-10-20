import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ContactOwner, mailtoHref, telHref } from "./ContactOwner";

const owner = { full_name: "Ana", phone: "+34 600 11 22 33", email: "ana@example.com" };

describe("ContactOwner", () => {
  it("despliega el teléfono (primero) y el correo como enlaces", async () => {
    render(<ContactOwner owner={owner} listingTitle="Bici" isOwner={false} />);

    await userEvent.click(screen.getByText("Contactar con Ana"));

    const links = screen.getAllByRole("link");
    expect(links.map((link) => link.textContent)).toEqual(["+34 600 11 22 33", "ana@example.com"]);
    expect(links[0].getAttribute("href")).toBe("tel:+34600112233");
    expect(links[1].getAttribute("href")).toBe("mailto:ana@example.com?subject=Interesado%20en%3A%20Bici");
  });

  it("sin teléfono, solo el correo", () => {
    render(<ContactOwner owner={{ ...owner, phone: null }} listingTitle="Bici" isOwner={false} />);

    expect(screen.queryByText(/Teléfono/)).toBeNull();
    expect(screen.getByRole("link", { hidden: true, name: "ana@example.com" })).toBeTruthy();
  });

  it("en mi propio anuncio no hay botón de contacto", () => {
    render(<ContactOwner owner={owner} listingTitle="Bici" isOwner />);

    expect(screen.getByText("Este es tu anuncio.")).toBeTruthy();
    expect(screen.queryByText("Contactar con Ana")).toBeNull();
  });

  it("codifica el asunto con tildes y &", () => {
    expect(mailtoHref("a@b.c", "Sofá & mesa")).toBe("mailto:a@b.c?subject=Interesado%20en%3A%20Sof%C3%A1%20%26%20mesa");
    expect(telHref("(91) 123-45-67")).toBe("tel:911234567");
  });
});
