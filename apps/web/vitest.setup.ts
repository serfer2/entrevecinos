import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// `server-only` lanza un error fuera del entorno react-server; en las pruebas no aplica.
vi.mock("server-only", () => ({}));

afterEach(() => {
  cleanup();
});
