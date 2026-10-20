"use client";

import { useId, useState } from "react";

import { IMAGE_MESSAGES, IMAGE_TYPES, imageFileError, MAX_LISTING_IMAGES, mediaSrc } from "@/lib/media";

import type { UploadImageResult } from "../actions";

type Item =
  | { key: string; name: string; state: "uploading" }
  | { key: string; name: string; state: "error"; error: string }
  | { key: string; name: string; state: "done"; id: string };

type ImagePickerProps = {
  upload: (formData: FormData) => Promise<UploadImageResult>;
  /** Imágenes ya subidas (al editar o tras un error del formulario). */
  initialIds?: string[];
  error?: string;
  onBusyChange?: (busy: boolean) => void;
};

let counter = 0;
const nextKey = () => `img-${++counter}`;

const smallButton =
  "rounded border border-gray-300 px-2 py-1 text-xs font-medium text-gray-800 hover:bg-gray-50 disabled:opacity-40";

/**
 * Selector de fotografías: sube cada fichero al elegirlo (en serie), permite reordenar y quitar,
 * y envía los ids en campos ocultos `image_asset_ids` en el orden mostrado. La primera es la portada.
 */
export function ImagePicker({ upload, initialIds = [], error, onBusyChange }: ImagePickerProps) {
  const inputId = useId();
  const [items, setItems] = useState<Item[]>(() =>
    initialIds.map((id) => ({ key: nextKey(), name: "", state: "done", id })),
  );
  const [busy, setBusy] = useState(false);
  const done = items.filter((item) => item.state === "done");

  const update = (key: string, item: Item) =>
    setItems((current) => current.map((existing) => (existing.key === key ? item : existing)));

  async function handleFiles(files: File[]) {
    setBusy(true);
    onBusyChange?.(true);
    let available = MAX_LISTING_IMAGES - done.length;
    for (const file of files) {
      const key = nextKey();
      const invalid = available <= 0 ? IMAGE_MESSAGES.max : imageFileError(file);
      if (invalid) {
        setItems((current) => [...current, { key, name: file.name, state: "error", error: invalid }]);
        continue;
      }
      available -= 1;
      setItems((current) => [...current, { key, name: file.name, state: "uploading" }]);
      const data = new FormData();
      data.set("file", file);
      const result = await upload(data).catch(() => ({ error: IMAGE_MESSAGES.error }));
      update(
        key,
        "id" in result
          ? { key, name: file.name, state: "done", id: result.id }
          : { key, name: file.name, state: "error", error: result.error },
      );
    }
    setBusy(false);
    onBusyChange?.(false);
  }

  /** Intercambia la fotografía con la anterior o la siguiente subida (ignora los errores). */
  function move(key: string, offset: -1 | 1) {
    setItems((current) => {
      const uploaded = current.flatMap((item, index) => (item.state === "done" ? [index] : []));
      const position = uploaded.indexOf(current.findIndex((item) => item.key === key));
      const from = uploaded[position];
      const to = uploaded[position + offset];
      if (from === undefined || to === undefined) return current;
      const next = [...current];
      [next[from], next[to]] = [next[to], next[from]];
      return next;
    });
  }

  const remove = (key: string) => setItems((current) => current.filter((item) => item.key !== key));
  const doneKeys = done.map((item) => item.key);

  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-sm font-medium text-gray-900">Fotografías (hasta 10)</legend>
      <label
        htmlFor={inputId}
        className="self-start cursor-pointer rounded-md border border-emerald-700 px-3 py-1.5 text-sm font-medium text-emerald-800 hover:bg-emerald-50 has-[:focus-visible]:ring-2"
      >
        Añadir fotografías
        <input
          id={inputId}
          type="file"
          accept={IMAGE_TYPES.join(",")}
          multiple
          disabled={busy || done.length >= MAX_LISTING_IMAGES}
          className="sr-only"
          aria-describedby={`${inputId}-hint`}
          onChange={(event) => {
            const files = Array.from(event.target.files ?? []);
            event.target.value = "";
            if (files.length > 0) void handleFiles(files);
          }}
        />
      </label>
      <p id={`${inputId}-hint`} className="text-sm text-gray-600">
        JPEG, PNG o WebP de hasta 5 MB. La primera será la portada.
      </p>
      {error && <p className="text-sm text-red-700">{error}</p>}

      <ul aria-live="polite" className="flex flex-col gap-2">
        {items.map((item) => {
          const position = doneKeys.indexOf(item.key);
          return (
            <li key={item.key} className="flex items-center gap-3 rounded-md border border-gray-200 p-2">
              {item.state === "done" ? (
                <>
                  {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición */}
                  <img
                    src={mediaSrc(item.id)}
                    alt={`Fotografía ${position + 1}`}
                    className="h-16 w-16 rounded object-cover"
                  />
                  <input type="hidden" name="image_asset_ids" value={item.id} />
                  <span className="flex-1 text-sm text-gray-700">
                    {position === 0 ? "Portada" : `Fotografía ${position + 1}`}
                  </span>
                  <button
                    type="button"
                    className={smallButton}
                    disabled={position === 0}
                    aria-label={`Subir fotografía ${position + 1}`}
                    onClick={() => move(item.key, -1)}
                  >
                    Subir
                  </button>
                  <button
                    type="button"
                    className={smallButton}
                    disabled={position === done.length - 1}
                    aria-label={`Bajar fotografía ${position + 1}`}
                    onClick={() => move(item.key, 1)}
                  >
                    Bajar
                  </button>
                </>
              ) : (
                <span className="flex-1 text-sm">
                  <span className="text-gray-800">{item.name}</span>{" "}
                  {item.state === "uploading" ? (
                    <span className="text-gray-600">Subiendo…</span>
                  ) : (
                    <span className="text-red-700">{item.error}</span>
                  )}
                </span>
              )}
              {item.state !== "uploading" && (
                <button
                  type="button"
                  className={smallButton}
                  aria-label={item.state === "done" ? `Quitar fotografía ${position + 1}` : `Quitar ${item.name}`}
                  onClick={() => remove(item.key)}
                >
                  Quitar
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </fieldset>
  );
}
