import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =======================================================
# Cargar datos y manejar errores
# =======================================================
ventas_oferta = pd.read_csv("resultado_ventas_oferta.csv")

# =======================================================
# Calcular el porcentaje de stock vendido
# =======================================================
ventas_oferta['Porcentaje_Vendido'] = ventas_oferta.apply(
    lambda row: round((row['Total_Ventas_Unidad'] / row['stock']) * 100, 2) if row['stock'] > 0 else 0,
    axis=1
)

# Guardo resultados
ventas_oferta.to_csv("resultado_stock_vendido.csv", index=False, encoding='utf-8')
print("Cálculo de porcentaje vendido completado y guardado en 'resultado_stock_vendido.csv'.")


# =======================================================
# Calculo días de la oferta
# =======================================================
ventas_oferta['fecha_inicio'] = pd.to_datetime(ventas_oferta['fecha_inicio'], errors='coerce')
ventas_oferta['fecha_fin'] = pd.to_datetime(ventas_oferta['fecha_fin'], errors='coerce')
ventas_oferta['Dias_Oferta'] = (ventas_oferta['fecha_fin'] - ventas_oferta['fecha_inicio']).dt.days + 1

# ============================================================
#Query para el grafico en Metabase de stock_sucursal vendido
# ============================================================

stock_sucursal = """

SELECT 
    sucursal,
    CASE 
        WHEN SUM(stock) > 0 THEN ROUND((SUM(Total_Ventas_Unidad) / SUM(stock)) * 100, 2)
        ELSE 0
    END AS porcentaje_vendido
FROM 
    "DBA".resultado_ventas_oferta
GROUP BY 
    sucursal
ORDER BY 
    porcentaje_vendido DESC;

"""

# =======================================================
# Cálculo de efectividad de las ventas por dia
# =======================================================
efectividad_por_periodo = ventas_oferta.groupby(
    ['codigo', 'sucursal', 'fecha_inicio', 'fecha_fin']
).apply(
    lambda df: df['Total_Ventas_Unidad'].sum() / df['Dias_Oferta'].sum() if df['Dias_Oferta'].sum() > 0 else 0
).reset_index(name='Efectividad_Ventas_por_Dia')

efectividad_por_periodo['Efectividad_Ventas_por_Dia'] = efectividad_por_periodo['Efectividad_Ventas_por_Dia'].round(2)

ventas_oferta = ventas_oferta.merge(
    efectividad_por_periodo, 
    on=['codigo', 'sucursal', 'fecha_inicio', 'fecha_fin'], 
    how='left'
)

# ===========================================================
# Elimino la columna Porcentaje_Vendido que no debe aparecer
# ===========================================================

ventas_oferta = ventas_oferta.drop(columns=['Porcentaje_Vendido'])

# ===========================================================
# Guardo el archivo 
# ===========================================================

ventas_oferta.to_csv("resultado_efectividad_por_dia.csv", index=False, encoding='utf-8')
print("Archivo 'resultado_efectividad_por_dia.csv' generado exitosamente.")  

