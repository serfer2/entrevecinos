"use client";

import { useState } from "react";

import { mediaSrc } from "@/lib/media";

type ListingGalleryProps = {
  title: string;
  images: { asset_id: string; url: string; is_cover: boolean }[];
};

/** Galería del detalle: imagen principal y miniaturas; flechas izquierda y derecha para cambiar. */
export function ListingGallery({ title, images }: ListingGalleryProps) {
  const initial = Math.max(0, images.findIndex((image) => image.is_cover));
  const [current, setCurrent] = useState(initial);

  if (images.length === 0) {
    return (
      <div className="flex aspect-[4/3] items-center justify-center rounded-lg bg-gray-100 text-gray-500">
        Sin fotografías
      </div>
    );
  }

  const go = (index: number) => setCurrent((index + images.length) % images.length);

  return (
    <div
      className="flex flex-col gap-3"
      role="group"
      aria-roledescription="galería"
      aria-label={`Fotografías de ${title}`}
      onKeyDown={(event) => {
        if (event.key === "ArrowRight") go(current + 1);
        if (event.key === "ArrowLeft") go(current - 1);
      }}
    >
      <div className="aspect-[4/3] overflow-hidden rounded-lg bg-gray-100">
        {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición */}
        <img
          src={mediaSrc(images[current].url)}
          alt={`${title}, imagen ${current + 1} de ${images.length}`}
          className="h-full w-full object-contain"
        />
      </div>
      <p aria-live="polite" className="sr-only">
        Imagen {current + 1} de {images.length}
      </p>
      {images.length > 1 && (
        <ul className="flex flex-wrap gap-2">
          {images.map((image, index) => (
            <li key={image.asset_id}>
              <button
                type="button"
                aria-label={`Imagen ${index + 1} de ${images.length}`}
                aria-pressed={index === current}
                onClick={() => setCurrent(index)}
                className="block h-16 w-16 overflow-hidden rounded border-2 border-transparent aria-pressed:border-emerald-700"
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada */}
                <img src={mediaSrc(image.url)} alt="" loading="lazy" className="h-full w-full object-cover" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
