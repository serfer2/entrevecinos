// @vitest-environment node
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

/** Ficheros `"use server"` de `src/` (sin las pruebas). */
function serverActionFiles(dir = join(__dirname, "..")): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return serverActionFiles(path);
    if (!/\.tsx?$/.test(name) || /\.test\.tsx?$/.test(name)) return [];
    return readFileSync(path, "utf8").startsWith('"use server"') ? [path] : [];
  });
}

describe('ficheros "use server"', () => {
  it("solo exportan funciones async y tipos (Next lo exige)", () => {
    const offenders = serverActionFiles().flatMap((path) =>
      readFileSync(path, "utf8")
        .split("\n")
        .filter((line) => /^export (?!type |async function |default async function )/.test(line))
        .map((line) => `${path}: ${line}`),
    );

    expect(offenders).toEqual([]);
  });
});
