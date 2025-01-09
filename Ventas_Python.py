import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================================================
#  Carga de datos
# ================================================

# Cargo los datos desde los archivos CSV
Ventas = pd.read_csv("Ventas_Combinadas_Agosto.csv")
articulos_oferta = pd.read_csv("Articulos_oferta.csv")

# Convierto las columnas 'CodigoInterno' y 'codigo' a string para evitar inconsistencias
Ventas['CodigoInterno'] = Ventas['CodigoInterno'].astype(str)
articulos_oferta['codigo'] = articulos_oferta['codigo'].apply(
    lambda x: str(int(float(x))) if isinstance(x, (int, float)) else str(x)
)

# Renombro columna 'DescripcionMarca' a 'Marca_producto' en el DataFrame de Ventas
Ventas.rename(columns={'DescripcionMarca': 'Marca_producto'}, inplace=True)

# Convierto las fechas a formato datetime
Ventas['Fecha'] = pd.to_datetime(Ventas['Fecha'])
articulos_oferta['fecha_inicio'] = pd.to_datetime(articulos_oferta['fecha_inicio'])
articulos_oferta['fecha_fin'] = pd.to_datetime(articulos_oferta['fecha_fin'])

# ================================================
#  Combinación y filtrado de datos
# ================================================

# Realizo el merge entre las ventas y los artículos en oferta
merged_df = pd.merge(
    articulos_oferta,
    Ventas,
    left_on=["codigo", "sucursal"],
    right_on=["CodigoInterno", "Sucursal"],
    how="inner"  # Inner join para mantener correspondencias en ambas tablas
)

# Relleno valores NaN en columnas relevantes
merged_df['Total de Ventas por Unidad'].fillna(0, inplace=True)  # Asigno 0 a ventas sin registros
merged_df['Descripcion'] = merged_df['Descripcion'].fillna('Sin descripción')
merged_df['Marca_producto'] = merged_df['Marca_producto'].fillna('Sin marca')

# Filtro las ventas que están dentro del rango de fechas de la oferta
filtered_df = merged_df[
    (merged_df['Fecha'] >= merged_df['fecha_inicio']) &
    (merged_df['Fecha'] <= merged_df['fecha_fin'])
]

# ================================================
#  Agrupamiento y agregación
# ================================================

# Agrupo por producto, sucursal y período de oferta
result_df = filtered_df.groupby(
    ['codigo', 'Descripcion', 'Marca_producto', 'sucursal', 'fecha_inicio', 'fecha_fin', 'stock'],
    as_index=False
).agg({'Total de Ventas por Unidad': 'sum'})

# Renombro la columna para claridad
result_df.rename(
    columns={
        'Descripcion': 'Descripcion_Articulo_Oferta',
        'Total de Ventas por Unidad': 'Total_Ventas_Unidad'
    }, inplace=True
)

# Me aseguro de que el total de ventas sea un entero
result_df['Total_Ventas_Unidad'] = result_df['Total_Ventas_Unidad'].astype(int)

# Guardo el DataFrame resultante en un archivo CSV
result_df.sort_values(by='Descripcion_Articulo_Oferta', inplace=True)
result_df.to_csv("resultado_ventas_oferta.csv", index=False, encoding='utf-8')


# ================================================
#  Lectura del archivo generado
# ================================================

# Leo el archivo guardado para graficar las ventas por período del mes
ventas_oferta = pd.read_csv("resultado_ventas_oferta.csv")
ventas_oferta['fecha_inicio'] = pd.to_datetime(ventas_oferta['fecha_inicio'])


# ================================================
#  Gráfico de barras: Ventas en oferta por período
# ================================================

# Filtro las ventas de agosto
result_df['fecha_inicio'] = pd.to_datetime(result_df['fecha_inicio'])
result_df = result_df[result_df['fecha_inicio'].dt.month == 8]

# Creo una nueva columna para clasificar los períodos
def clasificar_periodo_fecha(date):
    if date.day <= 10:
        return 'Inicio del mes\n01-10'
    elif 11 <= date.day <= 20:
        return 'Mitad del mes\n11-20'
    else:
        return 'Fin del mes\n21-31'

result_df['Periodo'] = result_df['fecha_inicio'].apply(clasificar_periodo_fecha)

# Agrupo por período y calculo la suma de ventas
ventas_por_periodo = result_df.groupby('Periodo')['Total_Ventas_Unidad'].sum().reset_index()

# Ordeno los períodos lógicamente
ventas_por_periodo['Periodo'] = pd.Categorical(
    ventas_por_periodo['Periodo'],
    categories=['Inicio del mes\n01-10', 'Mitad del mes\n11-20', 'Fin del mes\n21-31'],
    ordered=True
)
ventas_por_periodo.sort_values('Periodo', inplace=True)

# Gráfico de barras con fechas detalladas
plt.figure(figsize=(12, 6))
plt.bar(ventas_por_periodo['Periodo'], ventas_por_periodo['Total_Ventas_Unidad'], color=['skyblue', 'lightgreen', 'lightcoral'])
plt.title('Ventas Totales en los Diferentes Períodos de Agosto')
plt.xlabel('Período del Mes')
plt.ylabel('Total de Ventas por Unidad')
plt.xticks(rotation=45, ha='right')  # Roto etiquetas para mejor visualización
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()


# ===================================================
#  Calcular la tasa de ventas en oferta por sucursal
# ===================================================

# Ventas totales de agosto por sucursal
ventas_totales = Ventas.groupby('Sucursal')['Total de Ventas por Unidad'].sum().reset_index()
ventas_totales.rename(columns={'Total de Ventas por Unidad': 'Ventas_Totales'}, inplace=True)

# Ventas en oferta por sucursal
ventas_oferta_sucursal = ventas_oferta.groupby('sucursal')['Total_Ventas_Unidad'].sum().reset_index()
ventas_oferta_sucursal.rename(columns={'Total_Ventas_Unidad': 'Ventas_Oferta'}, inplace=True)

# Combinar ambos DataFrames
tasa_ventas = pd.merge(ventas_oferta_sucursal, ventas_totales, left_on='sucursal', right_on='Sucursal', how='inner')

# Calcular la tasa de ventas en oferta
tasa_ventas['Tasa_Ventas_Oferta'] = tasa_ventas['Ventas_Oferta'] / tasa_ventas['Ventas_Totales']

# ================================================
#  Gráfico: Tasa de ventas en oferta por sucursal
# ================================================

# Configuración del gráfico de barras comparativo
plt.figure(figsize=(10, 6))
sns.barplot(
    data=tasa_ventas, 
    x='Sucursal', 
    y='Tasa_Ventas_Oferta', 
    palette='viridis'
)
plt.title('Tasa de Ventas en Oferta por Sucursal (Agosto)', fontsize=14)
plt.xlabel('Sucursal', fontsize=12)
plt.ylabel('Tasa de Ventas en Oferta', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.show()

crespo_oferta = ventas_oferta[ventas_oferta['sucursal'] == 'Crespo']['Total_Ventas_Unidad'].sum()
crespo_totales = Ventas[Ventas['Sucursal'] == 'Crespo']['Total de Ventas por Unidad'].sum()
tasa_crespo = crespo_oferta / crespo_totales
print(crespo_oferta)
print(crespo_totales)
print(tasa_crespo)

# =======================================================
#  Consulta creada para obtener las ventas por sucursal
# =======================================================

ventas_sucursal = """
SELECT
    rvo.sucursal AS Sucursal,
    ROUND(
        SUM(rvo.Total_Ventas_Unidad) / vt.Ventas_Totales,
        4
    ) AS Tasa_Ventas_Oferta
FROM
    "DBA".resultado_ventas_oferta rvo
INNER JOIN (
    SELECT 
        Sucursal, 
        SUM(total_ventas_unidad) AS Ventas_Totales
    FROM 
        "DBA".ventas
    GROUP BY 
        Sucursal
) vt ON rvo.sucursal = vt.Sucursal
GROUP BY
    rvo.sucursal, vt.Ventas_Totales
ORDER BY
    Tasa_Ventas_Oferta DESC;
"""


# ================================================
#  Gráfico: Top 5 productos más vendidos
# ================================================

# Agrupo por producto y sumo las ventas totales para obtener los 5 productos más vendidos
top_5_productos = result_df.groupby(['codigo', 'Descripcion_Articulo_Oferta'])[
    'Total_Ventas_Unidad'
].sum().nlargest(5).reset_index()

# Creo el gráfico de barras
plt.figure(figsize=(12, 6))
sns.barplot(
    data=top_5_productos,
    x='Descripcion_Articulo_Oferta',
    y='Total_Ventas_Unidad',
    palette='viridis'
)
plt.title('Top 5 Productos Más Vendidos')
plt.xlabel('Descripción del Artículo')
plt.ylabel('Total de Ventas por Unidad')
plt.xticks(rotation=45, ha='right')  # Roto etiquetas para mejor visualización
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()