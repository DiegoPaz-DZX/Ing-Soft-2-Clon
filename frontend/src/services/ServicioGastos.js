import Gasto from '../domain/Gasto.js'
import { buscarCategoria } from '../domain/categorias.js'

export default class ServicioGastos {
  constructor(repositorio) {
    this.repositorio = repositorio
  }

  listar() {
    return this.repositorio
      .listar()
      .sort((a, b) => `${b.fecha}${b.registradoEn}`.localeCompare(`${a.fecha}${a.registradoEn}`))
  }

  registrar(datos) {
    const gasto = Gasto.crear(datos)
    const gastos = [...this.repositorio.listar(), gasto]
    this.repositorio.guardar(gastos)
    return gasto
  }

  resumenDelDia(fecha, gastos = this.listar()) {
    const gastosDelDia = gastos.filter((gasto) => gasto.fecha === fecha)
    const total = gastosDelDia.reduce((suma, gasto) => suma + Number(gasto.monto), 0)
    const acumulado = gastosDelDia.reduce((resultado, gasto) => {
      resultado[gasto.categoria] = (resultado[gasto.categoria] ?? 0) + Number(gasto.monto)
      return resultado
    }, {})
    const categoriaMayor = Object.entries(acumulado).sort((a, b) => b[1] - a[1])[0]

    return {
      total,
      cantidad: gastosDelDia.length,
      mayorCategoria: categoriaMayor
        ? { ...buscarCategoria(categoriaMayor[0]), total: categoriaMayor[1] }
        : null,
    }
  }

}
