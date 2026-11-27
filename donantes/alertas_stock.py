"""Alerta de stock bajo por grupo sanguíneo (H4).

Recibe el stock que calcula Inventario.stock_por_grupo (T4.1) y marca los grupos con pocas unidades.
Solo es lógica: la pantalla que muestra las alertas en rojo se arma en la tarea de interfaz.
"""

UMBRAL_STOCK_BAJO = 5  # criterio de aceptación: alerta si hay menos de 5 unidades


def obtener_alertas_stock_bajo(stock_por_grupo, umbral=UMBRAL_STOCK_BAJO):
    """Devuelve {grupo: bool} con True en los grupos cuyo stock es menor al umbral.

    La comparación es estricta: con umbral 5 alertan 0 a 4 unidades; con 5 ya no.
    El umbral se puede cambiar para que el PO lo configure sin tocar la lógica.
    """
    return {grupo: cantidad < umbral for grupo, cantidad in stock_por_grupo.items()}
