import { AutoSubmitSelect } from "@/components/ui/AutoSubmitSelect";

import { type ListingSearchParams, listingCriteria } from "../search-params";

type CommunitySwitcherProps = {
  currentId: string;
  communities: { id: string; name: string }[];
  search: ListingSearchParams;
};

/**
 * Cambia a otra de mis comunidades conservando la búsqueda y los filtros. Es un formulario GET a
 * `/comunidades/ir`, que redirige a la comunidad elegida: funciona también sin JavaScript.
 */
export function CommunitySwitcher({ currentId, communities, search }: CommunitySwitcherProps) {
  if (communities.length < 2) return null;

  return (
    <form method="get" action="/comunidades/ir" className="flex flex-wrap items-end gap-2">
      <AutoSubmitSelect
        id="community-switcher"
        name="id"
        label="Comunidad"
        options={communities.map((c) => ({ value: c.id, label: c.name }))}
        defaultValue={currentId}
      />
      {Array.from(listingCriteria(search)).map(([name, value]) => (
        <input key={name} type="hidden" name={name} value={value} />
      ))}
      <button
        type="submit"
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-800 hover:bg-gray-50"
      >
        Cambiar
      </button>
    </form>
  );
}
