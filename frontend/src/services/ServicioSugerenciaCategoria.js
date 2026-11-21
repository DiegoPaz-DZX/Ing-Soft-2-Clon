import { CATEGORIAS } from '../domain/categorias.js'

export const PALABRAS_CLAVE = Object.freeze({
  alimentacion: [
    'almuerzo', 'desayuno', 'cena', 'comida', 'menu', 'restaurante', 'pollo', 'pizza',
    'hamburguesa', 'cafe', 'snack', 'mercado', 'supermercado', 'bodega', 'fruta', 'pan',
    'bebida', 'gaseosa', 'jugo', 'chifa', 'cevicheria', 'polleria',
  ],
  transporte: [
    'pasaje', 'taxi', 'uber', 'cabify', 'bus', 'micro', 'combi', 'gasolina',
    'combustible', 'peaje', 'estacionamiento', 'cochera', 'movilidad', 'moto',
  ],
  servicios: [
    'luz', 'agua', 'internet', 'telefono', 'celular', 'recarga', 'cable', 'gas', 'alquiler',
    'renta', 'arbitrios', 'mantenimiento',
  ],
  entretenimiento: [
    'cine', 'netflix', 'spotify', 'juego', 'videojuego', 'steam', 'concierto', 'fiesta',
    'discoteca', 'bar', 'salida', 'streaming', 'disney', 'paseo', 'karaoke',
  ],
  salud: [
    'medicina', 'pastilla', 'farmacia', 'doctor', 'medico', 'consulta', 'clinica', 'hospital',
    'dentista', 'analisis', 'botica', 'terapia', 'vitamina', 'examen medico',
  ],
  educacion: [
    'libro', 'curso', 'matricula', 'pension', 'universidad', 'colegio', 'taller', 'clase',
    'utiles', 'cuaderno', 'fotocopia', 'impresion', 'academia', 'certificado',
  ],
})

export function normalizarTexto(texto) {
  return String(texto ?? '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .trim()
}

export function singularizar(palabra) {
  return palabra.endsWith('s') ? palabra.slice(0, -1) : palabra
}

function prepararParaComparar(texto) {
  const palabras = normalizarTexto(texto).split(/[^a-z0-9]+/).filter(Boolean)
  return ` ${palabras.map(singularizar).join(' ')} `
}

function puntuarCategorias(descripcion) {
  const texto = prepararParaComparar(descripcion)
  return Object.entries(PALABRAS_CLAVE).map(([categoria, claves]) => ({
    categoria,
    puntaje: claves.filter((clave) => texto.includes(prepararParaComparar(clave))).length,
  }))
}

export function sugerirCategoria(descripcion, catalogo = CATEGORIAS) {
  const puntajes = puntuarCategorias(descripcion)
  const maximo = Math.max(...puntajes.map((item) => item.puntaje))
  if (maximo === 0) return null

  const ganadoras = puntajes.filter((item) => item.puntaje === maximo)
  if (ganadoras.length !== 1) return null

  const { categoria } = ganadoras[0]
  return catalogo.some((item) => item.id === categoria) ? categoria : null
}
