# app.py (Versión Final con Todos los Cálculos)

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
        df_catalogo = pd.read_excel('catalogo_maestro.xlsx')
        df_catalogo['nombre_base_normalizado'] = df_catalogo['nombre_carta'].apply(normalizar_texto_base)

        archivos_precios = glob.glob('precios_tienda_*.csv')
        if not archivos_precios:
            raise Exception("No se encontraron archivos de precios.")

        lista_dfs_precios = [pd.read_csv(f) for f in archivos_precios]
        df_todos_precios = pd.concat(lista_dfs_precios, ignore_index=True)
        
        df_todos_precios['nombre_base'] = df_todos_precios['nombre'].apply(lambda x: re.sub(r'\(.*\)', '', str(x)).strip())
        df_todos_precios['nombre_base_normalizado'] = df_todos_precios['nombre_base'].apply(normalizar_texto_base)
        
        df_pivot = df_todos_precios.pivot_table(
            index='nombre_base_normalizado', 
            columns='tienda', 
            values='precio',
            aggfunc='min'
        ).reset_index()

        # --- LÓGICA DE CÁLCULO DE PROMEDIO Y MÍNIMO ---
        columnas_tiendas = [col for col in df_pivot.columns if col != 'nombre_base_normalizado']
        
        df_pivot['precio_promedio'] = df_pivot[columnas_tiendas].mean(axis=1, skipna=True)
        df_pivot['precio_minimo'] = df_pivot[columnas_tiendas].min(axis=1, skipna=True)
        df_pivot['mejor_tienda'] = df_pivot[columnas_tiendas].idxmin(axis=1)
        
        df_final = pd.merge(
            df_catalogo,
            df_pivot,
            on='nombre_base_normalizado',
            how='inner'
        )
        
        termino_buscado = request.args.get('busqueda')
        if termino_buscado:
            termino_normalizado = normalizar_texto_base(termino_buscado)
            df_final = df_final[df_final['nombre_carta'].str.contains(termino_normalizado, case=False, na=False)]
        
        lista_de_cartas = df_final.to_dict('records')

    except Exception as e:
        print(f">>> ERROR CRÍTICO: {e}")
        lista_de_cartas = []
        
    return render_template('index.html', titulo_web="Comparador de Precios MyL", cartas=lista_de_cartas)