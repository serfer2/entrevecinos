"use client";

import { type PointerEvent, type RefObject, useRef, useState } from "react";

type LightboxProps = {
  dialogRef: RefObject<HTMLDialogElement | null>;
  /** Nombre del visor para lectores de pantalla (p. ej. «Fotografías de Bici»). */
  label: string;
  images: { src: string; alt: string }[];
  current: number;
  onChange: (index: number) => void;
};

/** Distancia mínima, en píxeles, para que un arrastre horizontal cambie de imagen. */
const SWIPE_THRESHOLD = 50;

const controlClass =
  "flex h-11 w-11 items-center justify-center rounded-full bg-white/10 text-white backdrop-blur hover:bg-white/20 focus-visible:outline-white";

function Chevron({ direction }: { direction: "left" | "right" }) {
  return (
    <svg aria-hidden viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d={direction === "left" ? "m15 18-6-6 6-6" : "m9 18 6-6-6-6"} />
    </svg>
  );
}

/**
 * Visor de imágenes a pantalla completa en un `<dialog>` modal: se abre con
 * `dialogRef.current.showModal()`, se cierra con Escape, el botón o pulsando fuera de la imagen, y
 * cambia de imagen con los botones, las flechas del teclado o deslizando el dedo.
 */
export function Lightbox({ dialogRef, label, images, current, onChange }: LightboxProps) {
  const [dragX, setDragX] = useState(0);
  const start = useRef<{ x: number; y: number; id: number } | null>(null);
  // Tras arrastrar no se interpreta el clic final como «pulsar fuera» (que cerraría el visor).
  const dragged = useRef(false);
  const many = images.length > 1;
  const go = (index: number) => onChange((index + images.length) % images.length);
  const close = () => dialogRef.current?.close();

  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (!many || (event.pointerType === "mouse" && event.button !== 0)) return;
    // Los botones gestionan su propio clic: capturar el puntero lo desviaría al contenedor.
    if (event.target instanceof Element && event.target.closest("button")) return;
    dragged.current = false;
    start.current = { x: event.clientX, y: event.clientY, id: event.pointerId };
    // Mejora opcional (sigue el arrastre fuera del contenedor); si el puntero ya no está activo, se omite.
    try {
      event.currentTarget.setPointerCapture?.(event.pointerId);
    } catch {}
  };
  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    if (start.current?.id !== event.pointerId) return;
    const dx = event.clientX - start.current.x;
    if (Math.abs(dx) > 5) dragged.current = true;
    setDragX(dx);
  };
  const onPointerEnd = (event: PointerEvent<HTMLDivElement>) => {
    const origin = start.current;
    if (origin?.id !== event.pointerId) return;
    start.current = null;
    setDragX(0);
    const dx = event.clientX - origin.x;
    const dy = event.clientY - origin.y;
    if (event.type === "pointerup" && Math.abs(dx) > SWIPE_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      go(current + (dx < 0 ? 1 : -1));
    }
  };

  return (
    <dialog
      ref={dialogRef}
      aria-label={label}
      className="m-0 h-dvh max-h-none w-screen max-w-none bg-gray-950 p-0 backdrop:bg-gray-950"
      onKeyDown={(event) => {
        if (event.key === "ArrowRight" && many) go(current + 1);
        if (event.key === "ArrowLeft" && many) go(current - 1);
      }}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between gap-4 p-3 text-white sm:p-4">
          <p aria-live="polite" className="text-sm font-medium tabular-nums">
            {many && `${current + 1} / ${images.length}`}
          </p>
          <button type="button" autoFocus onClick={close} aria-label="Cerrar" className={controlClass}>
            <svg aria-hidden viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </div>

        <div
          className="relative flex min-h-0 flex-1 touch-pan-y select-none items-center justify-center px-2 pb-4 sm:px-20"
          onClick={(event) => {
            // Pulsar fuera de la imagen (en el fondo) cierra el visor.
            if (event.target === event.currentTarget && !dragged.current) close();
            dragged.current = false;
          }}
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerEnd}
          onPointerCancel={onPointerEnd}
        >
          {/* eslint-disable-next-line @next/next/no-img-element -- URL prefirmada que cambia en cada petición */}
          <img
            src={images[current].src}
            alt={images[current].alt}
            draggable={false}
            className={`h-full w-full object-contain ${dragX === 0 ? "transition-transform duration-200 motion-reduce:transition-none" : ""}`}
            style={dragX === 0 ? undefined : { transform: `translateX(${dragX}px)` }}
          />
          {many && (
            <>
              <button
                type="button"
                aria-label="Imagen anterior"
                onClick={() => go(current - 1)}
                className={`${controlClass} absolute left-2 top-1/2 -translate-y-1/2 sm:left-4`}
              >
                <Chevron direction="left" />
              </button>
              <button
                type="button"
                aria-label="Imagen siguiente"
                onClick={() => go(current + 1)}
                className={`${controlClass} absolute right-2 top-1/2 -translate-y-1/2 sm:right-4`}
              >
                <Chevron direction="right" />
              </button>
            </>
          )}
        </div>
      </div>
    </dialog>
  );
}
