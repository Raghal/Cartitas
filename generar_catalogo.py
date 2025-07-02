# generador_catalogo.py (Versión 2.1 - Parseo Inteligente)

import pandas as pd
import glob
import re

print(">>> Iniciando la creación del catálogo maestro...")

archivos_precios = glob.glob('precios_tienda_*.csv')
if not archivos_precios:
    print("!!! No se encontraron archivos de precios. Ejecuta los scrapers primero.")
    exit()

print(f">>> Encontrados {len(archivos_precios)} archivos de precios...")
df_todos_precios = pd.concat([pd.read_csv(f) for f in archivos_precios], ignore_index=True)
print(f">>> Se encontraron {len(df_todos_precios)} listados de productos en total.")


def limpiar_y_parsear(nombre_completo):
    """
    Función mejorada que primero limpia el nombre y luego lo parsea
    de forma inteligente para diferenciar edición de rareza.
    """
    if not isinstance(nombre_completo, str):
        return pd.Series(["", "N/A", "N/A"])
    
    # 1. Limpieza Inicial: Quitar texto basura
    nombre_limpio = re.sub(r'\s*-\s*SINGLES MITOS Y LEYENDAS', '', nombre_completo, flags=re.IGNORECASE).strip()

    # 2. Parseo del nombre base
    nombre_base = re.sub(r'\(.*\)', '', nombre_limpio).strip()
    
    # 3. Parseo Inteligente de Edición y Rareza
    match = re.search(r'\((.*?)\)', nombre_limpio)
    edicion, rareza = 'N/A', 'Estándar'
    
    if match:
        contenido = match.group(1).strip().lower()
        
        # Lista de palabras clave para identificar una rareza
        palabras_clave_rareza = ['foil', 'legendaria', 'ur', 'real', 'cortesano', 'vasallo', 'promocional', 'dorada', 'secreta', 'buy a box', 'premium']

        if ' - ' in contenido:
            partes = contenido.split(' - ', 1)
            edicion = partes[0].strip()
            rareza = partes[1].strip()
        else:
            # Si no hay guion, comprobamos si el contenido es una rareza conocida
            es_rareza = any(palabra in contenido for palabra in palabras_clave_rareza)
            if es_rareza:
                rareza = contenido
                edicion = 'N/A' # No podemos saber la edición
            else:
                # Si no es una rareza conocida, asumimos que es la edición
                edicion = contenido
                rareza = 'Estándar'
            
    return pd.Series([nombre_base, edicion.title(), rareza.title()])


# Aplicamos la nueva función mejorada
print(">>> Limpiando y parseando nombres de productos...")
df_todos_precios[['nombre_base', 'edicion', 'rareza']] = df_todos_precios['nombre'].apply(limpiar_y_parsear)


# Deduplicación final y precisa (no cambia)
print(">>> Eliminando duplicados...")
df_catalogo = df_todos_precios.drop_duplicates(subset=['nombre_base', 'edicion', 'rareza'])

# Creamos y ordenamos el catálogo final
df_catalogo_final = df_catalogo[['nombre_base', 'edicion', 'rareza']].copy()
df_catalogo_final = df_catalogo_final.rename(columns={'nombre_base': 'nombre_carta'})
df_catalogo_final = df_catalogo_final.sort_values(by=['nombre_carta', 'edicion', 'rareza'])
df_catalogo_final.insert(0, 'ID', range(1, 1 + len(df_catalogo_final)))
df_catalogo_final['url_imagen'] = '' 

print(f"\n>>> Proceso finalizado. Se encontraron {len(df_catalogo_final)} versiones de cartas únicas y limpias.")

# Guardamos el resultado
nombre_archivo_excel = 'catalogo_maestro.xlsx'
df_catalogo_final.to_excel(nombre_archivo_excel, index=False)

print(f"\n¡ÉXITO! Se ha creado el archivo '{nombre_archivo_excel}'.")
print(">>> Revisa el archivo para confirmar la calidad de los datos.")