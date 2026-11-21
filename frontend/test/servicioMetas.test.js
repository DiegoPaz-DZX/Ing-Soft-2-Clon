import test from 'node:test'
import assert from 'node:assert/strict'
import ServicioMetas from '../src/services/ServicioMetas.js'
import ConversorDivisa from '../src/domain/ConversorDivisa.js'
import MetaAhorro from '../src/domain/MetaAhorro.js'

class RepositorioEnMemoria {
  constructor() {
    this.meta = null
  }
  obtener() {
    return this.meta
  }
  guardar(meta) {
    this.meta = meta
    return meta
  }
}

const soles = new ConversorDivisa({ solesPorUnidad: 1 })
const dolares = new ConversorDivisa({ solesPorUnidad: 3.75 })

test('crea la meta guardando el objetivo en soles aunque se escriba en dólares', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  const meta = await servicio.crear({ nombre: 'Laptop', objetivo: 400 }, dolares)
  assert.equal(meta.objetivoPEN, 1500)
})

test('rechaza metas sin nombre o con monto no positivo', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  await assert.rejects(servicio.crear({ nombre: ' ', objetivo: 100 }, soles), /nombre/)
  await assert.rejects(servicio.crear({ nombre: 'Viaje', objetivo: 0 }, soles), /mayor que cero/)
})

test('abonar suma el monto convertido a soles', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  const creada = await servicio.crear({ nombre: 'Viaje', objetivo: 1000 }, soles)
  const meta = await servicio.abonar(creada, 100, dolares)
  assert.equal(meta.totalAbonadoPEN, 375)
})

test('abonar sin meta registrada falla y un abono inválido se rechaza', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  await assert.rejects(servicio.abonar(null, 10, soles), /Registra una meta/)
  await servicio.crear({ nombre: 'Viaje', objetivo: 1000 }, soles)
  const creada = await servicio.crear({ nombre: 'Viaje', objetivo: 1000 }, soles)
  await assert.rejects(servicio.abonar(creada, -5, soles), /abono/)
})

test('el progreso es el mismo sin importar la divisa en que se vea', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  const meta = await servicio.crear({ nombre: 'Viaje', objetivo: 1000 }, soles)
  const conAbono = await servicio.abonar(meta, 250, soles)
  const progreso = servicio.calcularProgreso(conAbono, [], 3.75)
  assert.equal(progreso.porcentaje, 25)
  assert.equal(dolares.deSoles(progreso.ahorradoPEN), 250 / 3.75)
  assert.equal(meta.objetivoPEN, 1000)
})

test('suma los gastos de categoría ahorro en soles y dólares', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  const meta = await servicio.crear({ nombre: 'Viaje', objetivo: 1000 }, soles)
  const transacciones = [
    { tipo: 'gasto', categoria: 'ahorro', monto: 100, moneda: 'PEN', metaId: 0 },
    { tipo: 'gasto', categoria: 'ahorro', monto: 100, moneda: 'USD', metaId: 0 },
    { tipo: 'gasto', categoria: 'comida', monto: 999, moneda: 'PEN' },
  ]
  assert.equal(servicio.calcularProgreso(meta, transacciones, 3.75).ahorradoPEN, 475)
})

test('marca la meta como completada y limita el porcentaje a 100', async () => {
  const servicio = new ServicioMetas(new RepositorioEnMemoria())
  const creada = await servicio.crear({ nombre: 'Viaje', objetivo: 100 }, soles)
  const meta = await servicio.abonar(creada, 150, soles)
  const progreso = servicio.calcularProgreso(meta, [], 3.75)
  assert.equal(progreso.porcentaje, 100)
  assert.equal(progreso.completada, true)
  assert.equal(progreso.faltantePEN, 0)
})

test('lee el formato anterior de meta guardada', () => {
  const meta = MetaAhorro.desdeJSON({ nombre: 'Viejo', objetivo: 500, moneda: 'PEN' })
  assert.equal(meta.objetivoPEN, 500)
  assert.deepEqual(meta.abonos, [])
})

test('el conversor rechaza un tipo de cambio inválido', () => {
  assert.throws(() => new ConversorDivisa({ solesPorUnidad: 0 }), /tipo de cambio/)
})
