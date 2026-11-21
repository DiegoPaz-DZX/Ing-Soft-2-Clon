import { CATEGORIAS } from '../../domain/categorias.js'

export default function SelectorCategoria({ value, onChange, error, categorias = CATEGORIAS }) {
  return (
    <fieldset>
      <legend className="label-caps mb-2 text-ink">Categoría</legend>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
        {categorias.map((categoria) => {
          const seleccionada = value === categoria.id

          return (
            <label
              key={categoria.id}
              className={`flex cursor-pointer items-center gap-2 rounded-xl border px-3 py-2 text-xs transition ${
                seleccionada
                  ? 'border-primary bg-primary-soft font-semibold text-primary-dark'
                  : 'border-line bg-app text-ink hover:border-primary/40'
              }`}
            >
              <input
                type="radio"
                name="categoria"
                value={categoria.id}
                checked={seleccionada}
                onChange={(event) => onChange(event.target.value)}
                className="sr-only"
              />
              <span className={`h-2.5 w-2.5 rounded-full ${categoria.color}`} aria-hidden="true" />
              {categoria.nombre}
            </label>
          )
        })}
      </div>
      {error && <p className="mt-1.5 text-xs text-expense">{error}</p>}
    </fieldset>
  )
}
