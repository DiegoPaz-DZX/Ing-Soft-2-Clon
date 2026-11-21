export const CATEGORIAS = Object.freeze([
  { id: 'alimentacion', nombre: 'Comida', color: 'bg-orange-500' },
  { id: 'transporte', nombre: 'Transporte', color: 'bg-sky-500' },
  { id: 'servicios', nombre: 'Servicios', color: 'bg-violet-500' },
  { id: 'entretenimiento', nombre: 'Entretenimiento', color: 'bg-pink-500' },
  { id: 'salud', nombre: 'Salud', color: 'bg-emerald-500' },
  { id: 'educacion', nombre: 'Educación', color: 'bg-amber-500' },
  { id: 'ahorro', nombre: 'Ahorro', color: 'bg-primary' },
  { id: 'otros', nombre: 'Otros', color: 'bg-slate-500' },
])

export function buscarCategoria(id) {
  return CATEGORIAS.find((categoria) => categoria.id === id)
}
