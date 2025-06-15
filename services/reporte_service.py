from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from services.restaurant_service import RestaurantService

router = APIRouter(prefix="/reportes", tags=["reportes"])

class ReportService:

    def calcular_reporte(self, user_id: str, restaurante_id: str):
        restaurante_data = RestaurantService.obtener_restaurante(self, user_id, restaurante_id)
        hoy = datetime.now().date()

        ventas_dia = 0
        pedidos_completados = 0
        tiempos_entrega = []
        clientes_atendidos = set()
        propinas_recibidas = 0
        platos_vendidos = defaultdict(int)
        pedidos_por_hora = defaultdict(int)
        pedidos_por_personal = defaultdict(lambda: {"pedidos_entregados": 0, "tiempos": []})
        ventas_por_dia_semana = {d: 0 for d in ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]}

        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

        for pedido_id, pedido in restaurante_data.get("pedidos", {}).items():
            estados = pedido.get("estados", {})
            estado_actual = estados.get("estado_actual", "")
            timestamp_confirmado = estados.get("confirmado")
            timestamp_entregado = estados.get("entregado") or estados.get("pagado")
            if not timestamp_confirmado:
                continue

            fecha_pedido = datetime.fromtimestamp(timestamp_confirmado / 1000).date()
            hora_pedido = datetime.fromtimestamp(timestamp_confirmado / 1000).hour
            dia_semana = dias[fecha_pedido.weekday()]

            # Calcular venta del pedido
            venta_pedido = 0
            for plato_id, detalle in pedido.get("platos", {}).items():
                cantidad = detalle.get("cantidad", 0)
                plato = restaurante_data.get("platos", {}).get(plato_id, {})
                precio = plato.get("precio", 0)
                venta_pedido += cantidad * precio
                # Plato estrella solo para hoy y pedidos completados
                if fecha_pedido == hoy and estado_actual in ["pagado", "entregado"]:
                    platos_vendidos[plato_id] += cantidad

            ventas_por_dia_semana[dia_semana] += venta_pedido

            # Solo pedidos completados cuentan para ventas del día y estadísticas
            if fecha_pedido == hoy and estado_actual in ["pagado", "entregado"]:
                ventas_dia += venta_pedido
                pedidos_completados += 1
                pedidos_por_hora[f"{hora_pedido}:00"] += 1
                silla_id = pedido.get("silla_id", "")
                if silla_id:
                    clientes_atendidos.add(silla_id)
                # Tiempo de entrega
                if timestamp_entregado:
                    tiempo_entrega = (timestamp_entregado - timestamp_confirmado) / 1000
                    tiempos_entrega.append(tiempo_entrega)
                # Por personal
                trabajador_id = pedido.get("trabajador_id")
                if trabajador_id:
                    trabajador = restaurante_data.get("trabajadores", {}).get(trabajador_id, {})
                    nombre_personal = trabajador.get("nombre", "Desconocido")
                    pedidos_por_personal[nombre_personal]["pedidos_entregados"] += 1
                    if timestamp_entregado:
                        pedidos_por_personal[nombre_personal]["tiempos"].append(tiempo_entrega)

        # Plato estrella
        plato_estrella_id = max(platos_vendidos.items(), key=lambda x: x[1], default=(None, 0))[0]
        plato_estrella = "Ninguno"
        if plato_estrella_id:
            plato_data = restaurante_data.get("platos", {}).get(plato_estrella_id, {})
            plato_estrella = plato_data.get("nombre", "Desconocido")

        # Tiempo promedio de entrega
        tiempo_promedio_entrega = "No disponible"
        if tiempos_entrega:
            promedio_segundos = statistics.mean(tiempos_entrega)
            tiempo_promedio_entrega = str(timedelta(seconds=promedio_segundos))

        # Personal stats
        personal_stats = []
        for nombre, data in pedidos_por_personal.items():
            tiempo_prom = "No disponible"
            if data["tiempos"]:
                tiempo_prom = str(timedelta(seconds=statistics.mean(data["tiempos"])))
            personal_stats.append({
                "nombre_personal": nombre,
                "pedidos_entregados": data["pedidos_entregados"],
                "tiempo_promedio": tiempo_prom
            })

        reporte = {
            "ventas_del_dia": ventas_dia,
            "pedidos_completados": pedidos_completados,
            "tiempo_promedio_de_entrega": tiempo_promedio_entrega,
            "clientes_atendidos": len(clientes_atendidos),
            "propinas_recibidas": propinas_recibidas,
            "plato_estrella_del_dia": plato_estrella,
            "pedidos_completados_por_hora": pedidos_por_hora,
            "pedidos_completados_por_personal": personal_stats,
            "ventas_por_dia_semana": ventas_por_dia_semana
        }
        return reporte