# app.py (Versión 2.1 - Corrección Final del Pivot)

from flask import Flask, render_template, request
import pandas as pd
import glob
from unidecode import unidecode
import re

app = Flask(__name__)

def normalizar_texto_base(texto):
    if not isinstance(texto, str):
        return ""
    nombre_base = re.sub(r'\(.*\)', '', texto).strip()
    return unidecode(nombre_base.lower())

@app.route('/')
def inicio():
    try:
        # 1. Leer Catálogo Maestro
        df_catalogo = pd.read_excel('catalogo_maestro.xlsx')
        # Renombramos 'nombre_carta' a 'nombre_base' para consistencia
        df_catalogo = df_catalogo.rename(columns={'nombre_carta': 'nombre_base'})
        df_catalogo['nombre_base_normalizado'] = df_catalogo['nombre_base'].apply(normalizar_texto_base)

        # 2. Leer y combinar TODOS los archivos de precios
        archivos_precios = glob.glob('precios_tienda_*.csv')
        if not archivos_precios:
            raise Exception("No se encontraron archivos de precios. Ejecuta los scrapers primero.")

        lista_dfs_precios = [pd.read_csv(f) for f in archivos_precios]
        df_todos_precios = pd.concat(lista_dfs_precios, ignore_index=True)

        # 3. Procesar datos scrapeados
        df_todos_precios['nombre_base'] = df_todos_precios['nombre'].apply(lambda x: re.sub(r'\(.*\)', '', str(x)).strip())
        df_todos_precios['nombre_base_normalizado'] = df_todos_precios['nombre_base'].apply(normalizar_texto_base)
        
        # 4. Pivotear para crear la tabla comparativa - ¡CON LA CORRECCIÓN!
        # Añadimos 'nombre_base' al 'index' para que no se pierda en el proceso.
        df_pivot = df_todos_precios.pivot_table(
            index=['nombre_base_normalizado', 'nombre_base'], 
            columns='tienda', 
            values='precio',
            aggfunc='min'
        ).reset_index()
        
        # 5. Merge final
        df_final = pd.merge(
            df_pivot,
            df_catalogo.drop(columns=['nombre_base']), # Evitamos duplicar la columna nombre_base
            on='nombre_base_normalizado',
            how='left' # Usamos left para mantener todas las cartas encontradas, incluso si no están en el catálogo
        )

        # 6. Lógica de búsqueda
        termino_buscado = request.args.get('busqueda')
        if termino_buscado:
            termino_normalizado = unidecode(termino_buscado.lower().strip())
            df_final = df_final[df_final['nombre_base_normalizado'].str.contains(termino_normalizado, na=False)]
        
        # Rellenamos datos faltantes para que el HTML no falle
        df_final.fillna({'edicion': 'N/A', 'rareza': 'N/A', 'url_imagen': ''}, inplace=True)
        
        lista_de_cartas = df_final.to_dict('records')

    except Exception as e:
        print(f">>> ERROR CRÍTICO: {e}")
        lista_de_cartas = []
        
    return render_template('index.html', titulo_web="Comparador de Precios MyL", cartas=lista_de_cartas)