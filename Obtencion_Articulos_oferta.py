import psycopg2
import pandas as pd

# ================================================
#  Conexion a la base de datos
# ================================================


# Función para ejecutar una consulta y cargar los resultados en un DataFrame
def execute_query(query):
    try:
        # Establecer la conexión
        conn = psycopg2.connect(
            dbname='LAR_TablasStock',
            user='postgres',
            password='123',
            host='localhost',
            port='5432'
        )
        
        # Ejecuto la consulta y cargo los datos en un DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")

# ================================================
#  Consulta para obtener los articulos en oferta
# ================================================


query_consulta_final = """
WITH ofertas AS (
    SELECT 
        a.codigo, 
        lo.barras, 
        a.descripcion, 
        lo.fecha_inicio, 
        lo.fecha_fin, 
        0.0 AS porcentaje_descuento
    FROM 
        "DBA".listas_oferta lo
    JOIN 
        "DBA".articulos a ON a.barras = lo.barras
    WHERE 
        lo.fecha_inicio >= '2024-08-01'
        AND lo.fecha_fin <= '2024-08-31'
),
precio_minorista AS (
    SELECT 
        barras, 
        fecha_vigencia_desde, 
        fecha_vigencia_hasta, 
        precio_minorista
    FROM 
        "DBA"."Precios_y_costos"
    WHERE 
        fecha_vigencia_desde <= '2024-08-31'
        AND fecha_vigencia_hasta >= '2024-08-01'
)

SELECT 
    o.codigo,
    o.barras,
    o.descripcion,
    o.fecha_inicio, 
    o.fecha_fin, 
    CASE 
        WHEN p.precio_minorista IS NULL OR lo.precio IS NULL THEN NULL
        ELSE ROUND(((p.precio_minorista - lo.precio) / p.precio_minorista) * 100, 2)
    END AS porcentaje_descuento,
    COALESCE(ss.sucursal, '') AS sucursal, 
    ROUND(COALESCE(ss.existencia, 0)) AS stock
FROM 
    ofertas o
LEFT JOIN 
    "DBA".stock_sucursal ss ON o.codigo = ss.codigo_art AND ss.fecha = o.fecha_inicio - 1
LEFT JOIN 
    precio_minorista p ON o.barras = p.barras AND o.fecha_inicio - 1 BETWEEN p.fecha_vigencia_desde AND p.fecha_vigencia_hasta
LEFT JOIN 
    "DBA".listas_oferta lo ON o.barras = lo.barras AND o.fecha_inicio = lo.fecha_inicio
ORDER BY 
    o.descripcion;

"""

# Ejecuto la consulta combinada 
result_final = execute_query(query_consulta_final)

# Muestro el número de filas
print(f"Número de filas: {len(result_final)}")

# Exporto los resultados a un archivo csv
result_final.to_csv('Articulos_oferta.csv', index=False)


# ===========================================================
#  Consulta para obtener la cantidad de articulos diferentes 
# ===========================================================

cant_articulos  = """
WITH ofertas AS (
    SELECT 
        a.codigo, 
        lo.barras, 
        a.descripcion, 
        lo.fecha_inicio, 
        lo.fecha_fin, 
        0.0 AS porcentaje_descuento
    FROM 
        "DBA".listas_oferta lo
    JOIN 
        "DBA".articulos a ON a.barras = lo.barras
    WHERE 
        lo.fecha_inicio >= '2024-08-01'
        AND lo.fecha_fin <= '2024-08-31'
)

SELECT 
    COUNT(DISTINCT o.barras) AS total_articulos_oferta
FROM 
    ofertas o;
"""


# ================================================
#  Cargar los datos de stock y articulos oferta
# ================================================

# Cargo los archivos CSV
articulos_of = pd.read_csv("Articulos_oferta.csv")


# ====================================================================
#  Cambiar nombres de sucursal para que coincidan con el csv de venta
# ====================================================================

# Cambios de nombres
cambios_nombres = {
    'CRESPO-CCC': 'Crespo',
    'HERNANDEZ-SMINO': 'Hernandez',
    'NOGOYA SUR-CONSUMO': 'Nogoya Sur',
    'NOGOYA ITALIA-SMINO': 'Nogoya Italia'
}

# Cambio los nombres en la columna 'sucursal' de articulos_of
if 'sucursal' in articulos_of.columns:
    articulos_of['sucursal'] = articulos_of['sucursal'].replace(cambios_nombres)

print("Nombres de sucursales actualizados correctamente.")



