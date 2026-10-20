// @vitest-environment node
import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { GET } from "./route";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";

function go(query: string) {
  // En Docker el servidor ve su propio host (0.0.0.0): la redirección debe ser relativa.
  const response = GET(new NextRequest(`http://0.0.0.0:3000/comunidades/ir?${query}`));
  return { status: response.status, location: response.headers.get("location") };
}

describe("GET /comunidades/ir", () => {
  it("redirige a la comunidad conservando búsqueda y filtros, sin la página", () => {
    expect(go(`id=${id}&q=bici&type=sell&page=3`)).toEqual({
      status: 303,
      location: `/comunidades/${id}?q=bici&type=sell`,
    });
  });

  it("descarta los filtros vacíos o no válidos", () => {
    expect(go(`id=${id}&type=rent&category_id=`).location).toBe(`/comunidades/${id}`);
  });

  it("id no válido → inicio", () => {
    expect(go("id=../admin").location).toBe("/inicio");
  });
});
