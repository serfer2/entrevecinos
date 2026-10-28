"use client";

import { useActionState } from "react";

import type { RequestAccessState } from "../actions";

type RequestAccessButtonProps = {
  communityId: string;
  action: (state: RequestAccessState, formData: FormData) => Promise<RequestAccessState>;
};

export function RequestAccessButton({ communityId, action }: RequestAccessButtonProps) {
  const [state, formAction, pending] = useActionState(action, undefined);

  return (
    <form action={formAction} className="flex flex-col items-start gap-1">
      <input type="hidden" name="community_id" value={communityId} />
      <button
        type="submit"
        disabled={pending}
        className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {pending ? "Enviando…" : "Solicitar acceso"}
      </button>
      {state?.error && (
        <p role="alert" className="text-sm text-red-700">
          {state.error}
        </p>
      )}
    </form>
  );
}
