"use client";

import { useRef, useState } from "react";

import { Lightbox } from "@/components/ui/Lightbox";
import { mediaSrc } from "@/lib/media";

type ListingGalleryProps = {
  title: string;
  images: { asset_id: string; url: string; is_cover: boolean }[];
};

/**
 * Galería del detalle: imagen principal y miniaturas; flechas izquierda y derecha para cambiar.
 * Pulsar la imagen principal la abre a pantalla completa (`Lightbox`).
 */
export function ListingGallery({ title, images }: ListingGalleryProps) {
  const initial = Math.max(0, images.findIndex((image) => image.is_cover));
  const [current, setCurrent] = useState(initial);
  const lightboxRef = useRef<HTMLDialogElement>(null);

  if (images.length === 0) {
    return (
      <div className="flex aspect-[4/3] items-center justify-center rounded-2xl border border-dashed border-emerald-300 bg-emerald-50 text-emerald-800">
        Sin fotografías
      </div>
    );
  }

  const go = (index: number) => setCurrent((index + images.length) % images.length);

  const label = `Fotografías de ${title}`;
  const alt = (index: number) => `${title}, imagen ${index + 1} de ${images.length}`;

  return (
    <>
      <div
        className="flex flex-col gap-3"
        role="group"
        aria-roledescription="galería"
        aria-label={label}
        onKeyDown={(event) => {
          if (event.key === "ArrowRight") go(current + 1);
          if (event.key === "ArrowLeft") go(current - 1);
        }}
      >
        <button
          type="button"
          aria-label={`Ampliar imagen ${current + 1} de ${images.length}`}
          onClick={() => lightboxRef.current?.showModal()}
          className="group relative block aspect-[4/3] cursor-zoom-in overflow-hidden rounded-2xl border border-gray-200 bg-white"
        >
          {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición */}
          <img src={mediaSrc(images[current].url)} alt={alt(current)} className="h-full w-full object-contain" />
          <span
            aria-hidden
            className="absolute bottom-3 right-3 flex h-9 w-9 items-center justify-center rounded-full bg-white/90 text-emerald-900 shadow-sm transition group-hover:scale-110 motion-reduce:transition-none"
          >
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
            </svg>
          </span>
        </button>
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
                  className="block h-16 w-16 overflow-hidden rounded-lg border-2 border-transparent opacity-80 hover:opacity-100 aria-pressed:border-emerald-700 aria-pressed:opacity-100"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada */}
                  <img src={mediaSrc(image.url)} alt="" loading="lazy" className="h-full w-full object-cover" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <Lightbox
        dialogRef={lightboxRef}
        label={label}
        images={images.map((image, index) => ({ src: mediaSrc(image.url), alt: alt(index) }))}
        current={current}
        onChange={setCurrent}
      />
    </>
  );
}
