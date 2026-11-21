import test from 'node:test'
import assert from 'node:assert/strict'
import {
  normalizarTexto,
  PALABRAS_CLAVE,
  singularizar,
  sugerirCategoria,
} from '../src/services/ServicioSugerenciaCategoria.js'
import { CATEGORIAS } from '../src/domain/categorias.js'

test('"Menú universitario" sugiere Comida (alimentacion)', () => {
  assert.equal(sugerirCategoria('Menú universitario'), 'alimentacion')
})

test('"Varios" es ambiguo: no sugiere nada', () => {
  assert.equal(sugerirCategoria('Varios'), null)
})

test('ignora tildes y mayúsculas', () => {
  assert.equal(sugerirCategoria('Menú'), 'alimentacion')
  assert.equal(sugerirCategoria('GAS'), 'servicios')
  assert.equal(sugerirCategoria('CAFÉ con amigos'), 'alimentacion')
  assert.equal(sugerirCategoria('Suscripción Netflix'), 'entretenimiento')
})

test('reconoce plurales', () => {
  assert.equal(sugerirCategoria('Pasajes de la semana'), 'transporte')
  assert.equal(sugerirCategoria('Almuerzos'), 'alimentacion')
})

test('un empate entre categorías no sugiere nada', () => {
  assert.equal(sugerirCategoria('Cena en el cine'), null)
})

test('cadena vacía y undefined devuelven null', () => {
  assert.equal(sugerirCategoria(''), null)
  assert.equal(sugerirCategoria(undefined), null)
})

test('palabras ambiguas eliminadas no sugieren', () => {
  assert.equal(sugerirCategoria('Compras en Metro'), null)
  assert.equal(sugerirCategoria('Pago de cuota del préstamo'), null)
})

test('reconoce frases de varias palabras', () => {
  assert.equal(sugerirCategoria('Examen médico'), 'salud')
})

test('no confunde subcadenas con palabras', () => {
  assert.equal(sugerirCategoria('panorama'), null)
})

test('solo sugiere categorías que existan en el catálogo recibido', () => {
  const sinAlimentacion = CATEGORIAS.filter((categoria) => categoria.id !== 'alimentacion')
  assert.equal(sugerirCategoria('Almuerzo', sinAlimentacion), null)
  assert.equal(sugerirCategoria('Pasaje', sinAlimentacion), 'transporte')
})

test('funciones auxiliares', () => {
  assert.equal(normalizarTexto('  Educación '), 'educacion')
  assert.equal(singularizar('pasajes'), 'pasaje')
  assert.equal(singularizar('taxi'), 'taxi')
})

test('con el catálogo real, cada categoría con palabras clave sugiere algo', () => {
  const ejemplos = {
    alimentacion: 'almuerzo',
    transporte: 'pasaje',
    servicios: 'luz',
    entretenimiento: 'cine',
    salud: 'farmacia',
    educacion: 'libro',
  }
  for (const [id, palabra] of Object.entries(ejemplos)) {
    assert.equal(sugerirCategoria(palabra, CATEGORIAS), id)
  }
})

test('un catálogo sin la categoría ganadora no sugiere nada', () => {
  assert.equal(sugerirCategoria('almuerzo', [{ id: 'transporte' }]), null)
})

test('cada clave de PALABRAS_CLAVE existe como id en el catálogo', () => {
  const ids = CATEGORIAS.map((categoria) => categoria.id)
  for (const clave of Object.keys(PALABRAS_CLAVE)) {
    assert.ok(ids.includes(clave), `"${clave}" no existe en CATEGORIAS`)
  }
})

test('"Delivery de paquete" ya no sugiere Comida', () => {
  assert.equal(sugerirCategoria('Delivery de paquete'), null)
})

test('el id alimentacion se muestra como Comida', () => {
  assert.equal(CATEGORIAS.find((categoria) => categoria.id === 'alimentacion').nombre, 'Comida')
})
