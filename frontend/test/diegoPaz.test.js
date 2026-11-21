import test from 'node:test'
import assert from 'node:assert/strict'

import ConversorDivisa from '../src/domain/ConversorDivisa.js'
import ServicioMetas from '../src/services/ServicioMetas.js'
import {
  cerrarSesionRemota,
  guardarUsuario,
  obtenerUsuario,
} from '../src/services/sesion.js'

class RepositorioMetasEnMemoria {
  constructor() {
    this.meta = null
  }

  guardar(meta) {
    this.meta = meta
    return meta
  }
}

class AlmacenamientoEnMemoria {
  constructor() {
    this.valores = new Map()
  }

  setItem(clave, valor) {
    this.valores.set(clave, valor)
  }

  getItem(clave) {
    return this.valores.get(clave) ?? null
  }

  removeItem(clave) {
    this.valores.delete(clave)
  }
}

test('HU16 limita el avance de una meta al 100%', () => {
  const servicio = new ServicioMetas(new RepositorioMetasEnMemoria())
  const meta = {
    id: 1,
    objetivoPEN: 100,
    totalAbonadoPEN: 150,
  }

  const progreso = servicio.calcularProgreso(meta, [], 3.75)

  assert.equal(progreso.porcentaje, 100)
  assert.equal(progreso.completada, true)
  assert.equal(progreso.faltantePEN, 0)
})

test('HU16 calcula el porcentaje y el monto faltante de una meta', () => {
  const servicio = new ServicioMetas(new RepositorioMetasEnMemoria())
  const meta = {
    id: 1,
    objetivoPEN: 1000,
    totalAbonadoPEN: 250,
  }

  const progreso = servicio.calcularProgreso(meta, [], 3.75)

  assert.equal(progreso.porcentaje, 25)
  assert.equal(progreso.ahorradoPEN, 250)
  assert.equal(progreso.faltantePEN, 750)
  assert.equal(progreso.completada, false)
})

test('HU29 conserva el balance de una meta en soles al cambiar a dólares', () => {
  const servicio = new ServicioMetas(new RepositorioMetasEnMemoria())
  const meta = {
    id: 7,
    objetivoPEN: 1500,
    totalAbonadoPEN: 375,
  }
  const solesPorDolar = 3.75
  const progreso = servicio.calcularProgreso(meta, [], solesPorDolar)
  const conversor = new ConversorDivisa({ solesPorUnidad: solesPorDolar })

  assert.equal(progreso.ahorradoPEN, 375)
  assert.equal(conversor.deSoles(progreso.ahorradoPEN), 100)
  assert.equal(conversor.deSoles(progreso.objetivoPEN), 400)
  assert.equal(progreso.porcentaje, 25)
})

test('HU29 convierte gastos de ahorro en PEN y USD para calcular el progreso', () => {
  const servicio = new ServicioMetas(new RepositorioMetasEnMemoria())
  const meta = {
    id: 7,
    objetivoPEN: 1000,
    totalAbonadoPEN: 0,
  }
  const transacciones = [
    { tipo: 'gasto', categoria: 'ahorro', monto: 100, moneda: 'PEN', metaId: 7 },
    { tipo: 'gasto', categoria: 'ahorro', monto: 100, moneda: 'USD', metaId: 7 },
    { tipo: 'gasto', categoria: 'comida', monto: 1000, moneda: 'PEN', metaId: 7 },
  ]

  const progreso = servicio.calcularProgreso(meta, transacciones, 3.75)

  assert.equal(progreso.ahorradoPEN, 475)
  assert.equal(progreso.porcentaje, 47.5)
})

test('HU17 revoca la sesión remotamente y limpia el almacenamiento local', async () => {
  globalThis.sessionStorage = new AlmacenamientoEnMemoria()
  globalThis.localStorage = new AlmacenamientoEnMemoria()
  guardarUsuario({ id: 10, token: 'token-valido' })
  localStorage.setItem('kyzen.transacciones', '[{"id":1}]')

  const llamadas = []
  const fetchOriginal = globalThis.fetch
  globalThis.fetch = async (url, opciones) => {
    llamadas.push({ url, opciones })
    return { ok: true }
  }

  try {
    await cerrarSesionRemota()

    assert.equal(llamadas.length, 1)
    assert.equal(llamadas[0].url, 'http://localhost:8000/api/logout')
    assert.equal(
      llamadas[0].opciones.headers.Authorization,
      'Bearer token-valido',
    )
    assert.equal(obtenerUsuario(), null)
    assert.equal(localStorage.getItem('kyzen.transacciones'), null)
  } finally {
    globalThis.fetch = fetchOriginal
  }
})

test('HU17 limpia la sesión local aunque el logout remoto falle', async () => {
  globalThis.sessionStorage = new AlmacenamientoEnMemoria()
  globalThis.localStorage = new AlmacenamientoEnMemoria()
  guardarUsuario({ id: 10, token: 'token-valido' })

  const fetchOriginal = globalThis.fetch
  globalThis.fetch = async () => {
    throw new Error('servidor no disponible')
  }

  try {
    await assert.rejects(cerrarSesionRemota(), /servidor no disponible/)
    assert.equal(obtenerUsuario(), null)
  } finally {
    globalThis.fetch = fetchOriginal
  }
})
