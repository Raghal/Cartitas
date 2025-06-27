# app.py (Versión Final con Parseo de Nombres)

from flask import Flask, render_template, request
import pandas as pd
from unidecode import unidecode
import math
import re # Importamos la librería de expresiones regulares para el parseo

app = Flask(__name__)

def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    # Quitamos paréntesis antes de normalizar para la búsqueda
    texto_sin_parentesis = re.sub(r'\(.*\)', '', texto)
    return unidecode(texto_sin_parentesis.lower().strip())

# --- INICIO DE LA NUEVA FUNCIÓN DE PARSEO ---
def parsear_nombre_producto(nombre_completo):
    """
    Esta función toma el nombre completo del producto y lo descompone en
    nombre base, edición y rareza.
    """
    nombre_base = re.sub(r'\(.*\)', '', nombre_completo).strip()
    
    # Buscamos el contenido dentro de los paréntesis
    match = re.search(r'\((.*?)\)', nombre_completo)
    
    edicion = 'N/A'
    rareza = 'N/A'
    
    if match:
        contenido_parentesis = match.group(1).strip()
        # Intentamos dividir por el guion
        if ' - ' in contenido_parentesis:
            partes = contenido_parentesis.split(' - ', 1)
            edicion = partes[0]
            rareza = partes[1]
        else:
            # Si no hay guion, asumimos que todo es la rareza/edición
            rareza = contenido_parentesis
            
    return pd.Series([nombre_base, edicion, rareza])
# --- FIN DE LA NUEVA FUNCIÓN DE PARSEO ---

@app.route('/')
def inicio():
    try:
        # 1. Leer Catálogo Maestro (SOLO para las imágenes)
        df_catalogo = pd.read_excel('catalogo_cartas.xlsx')
        # Creamos una columna normalizada para unir
        df_catalogo['nombre_base_normalizado'] = df_catalogo['nombre_carta'].apply(normalizar_texto)

        # 2. Leer Precios de TODAS las tiendas
        lista_dfs_precios = []
        try:
            lista_dfs_precios.append(pd.read_csv('precios_tienda_1.csv'))
        except FileNotFoundError:
            print("ADVERTENCIA: No se encontró precios_tienda_1.csv")
        try:
            lista_dfs_precios.append(pd.read_csv('precios_tienda_2.csv'))
        except FileNotFoundError:
            print("ADVERTENCIA: No se encontró precios_tienda_2.csv")
        
        if not lista_dfs_precios:
            raise Exception("No se encontraron archivos de precios. Ejecuta los scrapers primero.")

        # 3. Combinamos todos los precios en una sola tabla
        df_todos_precios = pd.concat(lista_dfs_precios, ignore_index=True)

        # 4. ¡LA NUEVA MAGIA! Aplicamos el parseo para crear nuevas columnas
        print(">>> Parseando nombres de productos para extraer data...")
        df_todos_precios[['nombre_base', 'edicion', 'rareza']] = df_todos_precios['nombre'].apply(parsear_nombre_producto)
        df_todos_precios['nombre_base_normalizado'] = df_todos_precios['nombre_base'].apply(normalizar_texto)
        print(">>> Parseo finalizado.")

        # 5. Unimos con el catálogo para obtener la URL de la imagen
        df_completo = pd.merge(
            df_todos_precios,
            df_catalogo[['nombre_base_normalizado', 'url_imagen']],
            on='nombre_base_normalizado',
            how='left'
        )
        
        # 6. Lógica de búsqueda del usuario
        termino_buscado = request.args.get('busqueda')
        if termino_buscado:
            termino_normalizado = normalizar_texto(termino_buscado)
            # Buscamos en la columna ya normalizada
            df_completo = df_completo[df_completo['nombre_base_normalizado'].str.contains(termino_normalizado, na=False)]
        
        lista_de_cartas = df_completo.to_dict('records')

    except Exception as e:
        print(f">>> ERROR CRÍTICO: {e}")
        lista_de_cartas = []
        
    return render_template('index.html', titulo_web="Agregador de Precios MyL", cartas=lista_de_cartas)