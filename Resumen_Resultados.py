import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ================================================
#  Cargar los datos
# ================================================

# Cargo ventas_oferta y Ventas
ventas_oferta = pd.read_csv("resultado_ventas_oferta.csv")
Ventas = pd.read_csv("Ventas_Combinadas_Agosto.csv")

# Convierto las fechas a formato datetime
Ventas['Fecha'] = pd.to_datetime(Ventas['Fecha'])
ventas_oferta['fecha_inicio'] = pd.to_datetime(ventas_oferta['fecha_inicio'])
ventas_oferta['fecha_fin'] = pd.to_datetime(ventas_oferta['fecha_fin'])

# ================================================
#  Calcular ventas normales y aumento de ventas
# ================================================

def calcular_ventas_normales(row):
    """
    Calcula las ventas normales y el aumento de ventas para un producto en una sucursal y periodo dados.
    Compara al menos 5 días si es posible. Si hay menos días, considera los dias disponibles.
    """
    codigo = row['codigo']
    sucursal = row['sucursal']
    fecha_inicio_oferta = row['fecha_inicio']
    fecha_fin_oferta = row['fecha_fin']
    
    # Filtro ventas normales (fuera del rango de la oferta)
    ventas_normales = Ventas[
        (Ventas['CodigoInterno'] == str(codigo)) & 
        (Ventas['Sucursal'] == sucursal) & 
        ((Ventas['Fecha'] < fecha_inicio_oferta) | (Ventas['Fecha'] > fecha_fin_oferta)) & 
        (Ventas['Fecha'].dt.year == 2024)
    ]
    
    # Calculo el número de días en la oferta
    dias_oferta = (fecha_fin_oferta - fecha_inicio_oferta).days + 1
    
    # Determino el número mínimo de días para comparar
    dias_comparacion = min(dias_oferta, 5)
    
    # Selecciono las fechas de ventas normales
    fechas_normales = ventas_normales['Fecha'].sort_values().unique()[:dias_comparacion]
    
    # Verifico si hay suficientes fechas normales
    if len(fechas_normales) < dias_comparacion:
        dias_comparacion = len(fechas_normales)
    
    # Filtro las ventas normales con las fechas seleccionadas
    ventas_normales = ventas_normales[ventas_normales['Fecha'].isin(fechas_normales)]
    
    # Calculo la suma total de ventas normales
    total_ventas_normal = ventas_normales['Total de Ventas por Unidad'].sum()
    
    # Calculo el aumento de ventas
    aumento = ((row['Total_Ventas_Unidad'] - total_ventas_normal) / total_ventas_normal * 100
               if total_ventas_normal > 0 else np.nan)
    
    return pd.Series({
        'cantidad_ventas_normal': total_ventas_normal,
        'fechas_normal': ', '.join([str(fecha.date()) for fecha in fechas_normales]),
        'aumento_ventas': round(aumento, 2),
        'cantidad_dias': dias_comparacion
    })

# Aplico la función y agrego las columnas al dataset existente
ventas_normales_info = ventas_oferta.apply(calcular_ventas_normales, axis=1)
comparacion_ventas = pd.concat([ventas_oferta, ventas_normales_info], axis=1)

# ================================================
#  Guardo el dataset final
# ================================================

# Guardo el DataFrame final
comparacion_ventas.to_csv("comparacion_ventas.csv", index=False, encoding='utf-8')
print("Archivo comparacion_ventas.csv generado con éxito.")

# ================================================
#  Verificacion Ventas_combinadas
# ================================================

# Cargo los datos desde el archivo CSV
ventas_oferta = pd.read_csv("resultado_ventas_oferta.csv")

# Cargo los datos desde los archivos CSV
Ventas = pd.read_csv("Ventas_Combinadas_Agosto.csv")

# Filtro los datos según los criterios especificados
filtro = (Ventas['Fecha'] == '2024-08-01') & (Ventas['CodigoInterno'] == '9038') & (Ventas['Sucursal'] == 'Crespo')
Ventas_filtradas = Ventas[filtro]

# Calculo el total de ventas por unidad
total_ventas_unidad = Ventas_filtradas['Total de Ventas por Unidad'].sum()

print("El Total de Ventas por Unidad es:", total_ventas_unidad)

# ================================================
#  Estadísticas y visualización
# ================================================

# Redondeo los valores de aumento_ventas a 2 decimales
comparacion_ventas['aumento_ventas'] = comparacion_ventas['aumento_ventas'].round(2)

# Cuento las categorías de aumento de ventas
aumentos_positivos = comparacion_ventas[comparacion_ventas['aumento_ventas'] > 0].shape[0]
disminuciones_ventas = comparacion_ventas[comparacion_ventas['aumento_ventas'] < 0].shape[0]
aumentos_sin_dato = comparacion_ventas['aumento_ventas'].isna().sum()
aumento_en_0 = comparacion_ventas[comparacion_ventas['aumento_ventas'] == 0].shape[0]


# Creo el DataFrame para el gráfico
categorias = pd.DataFrame({
    'Categoria': ['Aumento > 0', 'Aumento < 0', 'Sin Dato', 'Aumento = 0'],
    'Cantidad': [aumentos_positivos, disminuciones_ventas, aumentos_sin_dato, aumento_en_0]
})

# Grafico
plt.figure(figsize=(8, 6))
sns.barplot(data=categorias, x='Cantidad', y='Categoria', palette='viridis')
plt.title('Categorías del Aumento de Ventas', fontsize=16)
plt.xlabel('Cantidad')
plt.ylabel('Categoría')
plt.show()


# ================================================
#  Graficar aumento de ventas por sucursal
# ================================================

# Agrupo por sucursal y calculo el promedio del aumento de ventas
aumento_por_sucursal = comparacion_ventas.groupby('sucursal')['aumento_ventas'].mean().reset_index()

# Redondo los valores a 2 decimales
aumento_por_sucursal['aumento_ventas'] = aumento_por_sucursal['aumento_ventas'].round(2)

# Ordeno por aumento de ventas
aumento_por_sucursal = aumento_por_sucursal.sort_values(by='aumento_ventas', ascending=False)

# Creo el gráfico de barras
plt.figure(figsize=(12, 8))
sns.barplot(
    data=aumento_por_sucursal,
    x='aumento_ventas',
    y='sucursal',
    palette='coolwarm'
)

# Configuro título y etiquetas
plt.title('Aumento Promedio de Ventas por Sucursal (%)', fontsize=16)
plt.xlabel('Aumento Promedio en Ventas (%)', fontsize=12)
plt.ylabel('Sucursal', fontsize=12)

plt.show()