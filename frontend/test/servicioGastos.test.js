import test from 'node:test'
import assert from 'node:assert/strict'
import ServicioGastos from '../src/services/ServicioGastos.js'

class RepositorioMemoria {
  constructor() {
    this.gastos = []
  }

  listar() {
    return [...this.gastos]
  }

  guardar(gastos) {
    this.gastos = [...gastos]
  }
}

test('registra un gasto con una categoría válida', () => {
  const servicio = new ServicioGastos(new RepositorioMemoria())
  const gasto = servicio.registrar({
    descripcion: 'Almuerzo',
    monto: '18.50',
    fecha: '2026-09-29',
    categoria: 'alimentacion',
  })

  assert.equal(gasto.monto, 18.5)
  assert.equal(servicio.listar().length, 1)
})

test('calcula la categoría con mayor consumo del día', () => {
  const servicio = new ServicioGastos(new RepositorioMemoria())
  servicio.registrar({ descripcion: 'Bus', monto: 5, fecha: '2026-09-29', categoria: 'transporte' })
  servicio.registrar({ descripcion: 'Taxi', monto: 20, fecha: '2026-09-29', categoria: 'transporte' })
  servicio.registrar({ descripcion: 'Cena', monto: 15, fecha: '2026-09-29', categoria: 'alimentacion' })

  const resumen = servicio.resumenDelDia('2026-09-29')
  assert.equal(resumen.total, 40)
  assert.equal(resumen.mayorCategoria.id, 'transporte')
  assert.equal(resumen.mayorCategoria.total, 25)
})
