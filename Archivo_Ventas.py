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
        print("Conexión exitosa a la base de datos.")
        
        # Ejecuto la consulta y cargo los datos en un DataFrame
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error al conectarse a la base de datos: {e}")

query_ventas = """

WITH ventas_filtradas AS (
    SELECT 
        a.codigo, 
        a.descripcion AS Descripcion_Articulo_Oferta,  
        a.sucursal, 
        a.fecha_inicio, 
        a.fecha_fin,
        COALESCE(SUM(v."total_ventas_unidad"), 0) AS Total_Ventas_Unidad, 
        a.stock
    FROM 
        "DBA"."articulos_of" a
    INNER JOIN 
        "DBA"."ventas" v 
        ON a.codigo = v.codigointerno AND a.sucursal = v.sucursal
    WHERE
        v.fecha >= a.fecha_inicio AND v.fecha <= a.fecha_fin
    GROUP BY 
        a.codigo, 
        a.descripcion, 
        a.sucursal, 
        a.fecha_inicio, 
        a.fecha_fin,
        a.stock
)
SELECT * 
FROM ventas_filtradas
ORDER BY Descripcion_Articulo_Oferta, sucursal;

"""