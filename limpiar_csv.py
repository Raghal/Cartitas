import pandas as pd
import sys
import re

# Verificamos si se nos dio un nombre de archivo para limpiar
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el nombre del archivo CSV a limpiar.")
    print("Ejemplo: python limpiar_csv.py precios_tienda_3.csv")
    sys.exit()

# El nombre del archivo es el primer argumento que pasamos al script
archivo_a_limpiar = sys.argv[1]
texto_a_quitar = "- SINGLES MITOS Y LEYENDAS"

print(f">>> Iniciando limpieza para el archivo: {archivo_a_limpiar}")

try:
    # Leemos el archivo CSV
    df = pd.read_csv(archivo_a_limpiar)

    # Creamos una copia de la columna 'nombre' por si acaso
    df['nombre_original'] = df['nombre']

    # --- LÓGICA DE LIMPIEZA ---
    # Usamos expresiones regulares para una limpieza más robusta
    # re.sub() reemplaza el patrón con una cadena vacía
    # flags=re.IGNORECASE hace que no le importen mayúsculas o minúsculas
    # .str.strip() quita cualquier espacio en blanco que quede al principio o al final
    df['nombre'] = df['nombre'].str.replace(texto_a_quitar, '', case=False).str.strip()

    # Guardamos el archivo CSV modificado, sobrescribiendo el original
    df.to_csv(archivo_a_limpiar, index=False, encoding='utf-8')

    print(f"\n¡Éxito! El archivo '{archivo_a_limpiar}' ha sido limpiado.")
    print("\nPrimeras 5 filas del archivo limpio:")
    print(df[['nombre', 'precio', 'tienda']].head())


except FileNotFoundError:
    print(f"!!! ERROR: No se pudo encontrar el archivo '{archivo_a_limpiar}'. Asegúrate de que el nombre esté bien escrito.")
except Exception as e:
    print(f"!!! Ocurrió un error inesperado: {e}")