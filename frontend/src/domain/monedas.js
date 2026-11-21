export const MONEDAS = Object.freeze([
  { codigo: 'PEN', nombre: 'Soles (S/)', simbolo: 'S/' },
  { codigo: 'USD', nombre: 'Dólares (US$)', simbolo: 'US$' },
])

export function simboloMoneda(codigo) {
  return MONEDAS.find((m) => m.codigo === codigo)?.simbolo ?? 'S/'
}

// Ejemplo: formatearConMoneda(1234.5, 'USD') -> "US$ 1,234.50"
export function formatearConMoneda(monto, moneda = 'PEN') {
  const numero = Number(monto).toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
  return `${simboloMoneda(moneda)} ${numero}`
}