import psycopg2
import pandas as pd

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
        
        # Ejecutar la consulta y cargar los datos en un DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")

# Configurar Pandas para que muestre todas las columnas
pd.set_option('display.max_columns', None)


# Consulta para conectar la tabla listas_oferta con articulos
query_articulos = """
SELECT a.codigo, lo.barras, a.descripcion, lo.fecha_inicio, lo.fecha_fin, 0.0 AS porcentaje_descuento
	FROM "DBA".listas_oferta lo
	JOIN "DBA".articulos a ON a.barras = lo.barras
"""
result_articulos1 = execute_query(query_articulos)


# Consulta para conectar la familia de tablas fac_descuentas con articulos
query_articulos = """
SELECT a.codigo, a.barras, a.descripcion, fd.fecha_inicio, fd.fecha_fin,
    CASE WHEN fd.porcentaje != 0 THEN fd.porcentaje ELSE fda.porcentaje END AS porcentaje_descuento
	FROM "DBA".fac_descuentos fd
	JOIN "DBA".fac_descuentos_detalle_aplicacion fda ON fd.codigo = fda.codigo
    JOIN "DBA".articulos a ON fda.articulo = a.codigo 
    AND a.enganchado != 'E'
"""
result_articulos_2 = execute_query(query_articulos)



#Coneccion de las tablas listas_oferta y fac_descuentos 
query_combined = """
WITH normalizacion AS (
    SELECT a.codigo, lo.barras, a.descripcion, lo.fecha_inicio, lo.fecha_fin, 0.0 AS porcentaje_descuento
    FROM "DBA".listas_oferta lo
    JOIN "DBA".articulos a ON a.barras = lo.barras
    WHERE lo.fecha_inicio >= '2024-08-01'
    AND lo.fecha_fin <= '2024-08-31'
    
    UNION
    
    SELECT a.codigo, a.barras, a.descripcion, fd.fecha_inicio, fd.fecha_fin,
        CASE WHEN fd.porcentaje != 0 THEN fd.porcentaje ELSE fda.porcentaje END AS porcentaje_descuento
    FROM "DBA".fac_descuentos fd
    JOIN "DBA".fac_descuentos_detalle_aplicacion fda ON fd.codigo = fda.codigo
    JOIN "DBA".articulos a ON fda.articulo = a.codigo
    WHERE fd.fecha_inicio >= '2024-08-01'
    AND fd.fecha_fin <= '2024-08-31'
    AND a.enganchado != 'E'
)

SELECT * FROM normalizacion;
"""
# Ejecuto la consulta combinada y obtengo los resultados
resultado_combinado = execute_query(query_combined)


# Muestro el número de filas (cantidad de datos)
print(f"Número de filas1: {len(resultado_combinado)}")

resultado_combinado.to_csv('resultado_combinado.csv', index=False)


query_consulta_final = """
WITH normalizacion AS (
    SELECT a.codigo, lo.barras, a.descripcion, lo.fecha_inicio, lo.fecha_fin, 0.0 AS porcentaje_descuento
    FROM "DBA".listas_oferta lo
    JOIN "DBA".articulos a ON a.barras = lo.barras
    WHERE lo.fecha_inicio >= '2024-08-01'
    AND lo.fecha_fin <= '2024-08-31'
    
    UNION
    
    SELECT a.codigo, a.barras, a.descripcion, fd.fecha_inicio, fd.fecha_fin,
        CASE WHEN fd.porcentaje != 0 THEN fd.porcentaje ELSE fda.porcentaje END AS porcentaje_descuento
    FROM "DBA".fac_descuentos fd
    JOIN "DBA".fac_descuentos_detalle_aplicacion fda ON fd.codigo = fda.codigo
    JOIN "DBA".articulos a ON fda.articulo = a.codigo
    WHERE fd.fecha_inicio >= '2024-08-01'
    AND fd.fecha_fin <= '2024-08-31'
    AND a.enganchado != 'E'
),
precio_minorista AS (
    SELECT barras, fecha_vigencia_desde, fecha_vigencia_hasta, precio_minorista
    FROM "DBA"."Precios_y_costos"
    WHERE fecha_vigencia_desde <= '2024-08-31'
    AND fecha_vigencia_hasta >= '2024-08-01'
) 

SELECT 
    n.codigo,
    n.barras,
    n.descripcion,
    n.fecha_inicio, 
    n.fecha_fin, 
	ROUND(
	    COALESCE(
	        NULLIF(n.porcentaje_descuento, 0) * 100,
	        ((p.precio_minorista - lo.precio) / p.precio_minorista) * 100,
	        0.0
	    ), 2
	) AS porcentaje_descuento,  -- Aquí agregamos la coma
    COALESCE(ss.sucursal, '') AS sucursal, 
    ROUND(COALESCE(ss.existencia, 0)) AS stock

FROM normalizacion n 
LEFT JOIN "DBA".stock_sucursal ss ON n.codigo = ss.codigo_art AND ss.fecha = n.fecha_inicio - 1
LEFT JOIN precio_minorista p ON n.barras = p.barras AND n.fecha_inicio - 1 BETWEEN p.fecha_vigencia_desde AND p.fecha_vigencia_hasta
LEFT JOIN "DBA".listas_oferta lo ON n.barras = lo.barras AND n.fecha_inicio = lo.fecha_inicio
ORDER BY n.codigo;

"""

# Ejecuto la consulta combinada 
result_final = execute_query(query_consulta_final)

# Muestro el número de filas (cantidad de datos)
print(f"Número de filas1: {len(result_final)}")

result_final.to_csv('dataset_final.csv', index=False)





