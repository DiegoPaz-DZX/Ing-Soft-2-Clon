from dataclasses import asdict


class ConversorJson:
    @staticmethod
    def tarjeta_a_dict(tarjeta):
        return {
            "totalIngresos": float(tarjeta.total_ingresos),
            "totalGastos": float(tarjeta.total_gastos),
            "balance": float(tarjeta.balance),
        }

    # NUEVO: soles en la raíz (como antes) y dólares en la clave "USD"
    @staticmethod
    def tarjetas_a_dict(tarjetas):
        datos = ConversorJson.tarjeta_a_dict(tarjetas["PEN"])
        datos["USD"] = ConversorJson.tarjeta_a_dict(tarjetas["USD"])
        return datos

    @staticmethod
    def tips_a_lista(tips):
        return [asdict(tip) for tip in tips]

    @staticmethod
    def categorias_a_lista(categorias):
        return [{"id": categoria.codigo, "nombre": categoria.nombre} for categoria in categorias]

    @staticmethod
    def recomendaciones_a_lista(recomendaciones):
        return [asdict(recomendacion) for recomendacion in recomendaciones]

    @staticmethod
    def movimientos_a_lista(movimientos):
        return [
            {
                "id": movimiento.pk,
                "tipo": movimiento.tipo,
                "descripcion": movimiento.descripcion,
                "monto": float(movimiento.monto),
                "moneda": movimiento.moneda,  # NUEVO
                "fecha": movimiento.fecha.isoformat(),
                "categoria": movimiento.categoria,
                "meta_id": movimiento.meta_id,
                "meta_nombre": movimiento.meta.nombre if movimiento.meta_id else None,
                "comprobante": movimiento.datos_comprobante(),
            }
            for movimiento in movimientos
        ]