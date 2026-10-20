import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ApiListing } from "../types";
import { ListingActions } from "./ListingActions";

const listing = { id: "l1", status: "active" } as ApiListing;

describe("ListingActions", () => {
  it("el autor ve «Editar anuncio»", () => {
    render(<ListingActions listing={listing} isOwner canModerate={false} />);

    expect(screen.getByRole("link", { name: "Editar anuncio" }).getAttribute("href")).toBe("/anuncios/l1/editar");
  });

  it("otros vecinos no ven la edición", () => {
    render(<ListingActions listing={listing} isOwner={false} canModerate />);

    expect(screen.queryByRole("link", { name: "Editar anuncio" })).toBeNull();
  });

  it.each(["hidden", "completed"] as const)("sin edición en anuncios %s", (status) => {
    render(<ListingActions listing={{ ...listing, status }} isOwner canModerate={false} />);

    expect(screen.queryByRole("link", { name: "Editar anuncio" })).toBeNull();
  });
});
