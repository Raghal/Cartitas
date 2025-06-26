from flask import Flask, render_template, request
import pandas as pd
# Paso 2.1: Importamos la nueva librería que acabamos de instalar.
from unidecode import unidecode

app = Flask(__name__)

# --- INICIO DE LA NUEVA FUNCIÓN DE NORMALIZACIÓN ---
def normalizar_texto(texto):
    """
    Esta función toma un texto, lo convierte a minúsculas y le quita las tildes.
    Regresa None si el texto de entrada no es válido.
    """
    if not isinstance(texto, str):
        return ""
    # Convierte a minúsculas -> le quita las tildes -> quita espacios en blanco al inicio/final
    return unidecode(texto.lower().strip())
# --- FIN DE LA NUEVA FUNCIÓN DE NORMALIZACIÓN ---


@app.route('/')
def inicio():
    print(">>> Petición recibida en la página principal.")
    
    termino_buscado = request.args.get('busqueda')

    try:
        df_cartas = pd.read_excel('catalogo_cartas.xlsx')

        if termino_buscado:
            print(f">>> Buscando cartas que contengan: '{termino_buscado}'")

            # Paso 2.2: Normalizamos el término que el usuario buscó.
            termino_normalizado = normalizar_texto(termino_buscado)

            # Paso 2.3: Creamos una nueva columna TEMPORAL en nuestra tabla
            # con todos los nombres de las cartas normalizados.
            # La función .apply() ejecuta nuestra función 'normalizar_texto' para cada fila.
            df_cartas['nombre_normalizado'] = df_cartas['nombre_carta'].apply(normalizar_texto)

            # Paso 2.4: Ahora la búsqueda se hace comparando las dos columnas normalizadas.
            df_cartas = df_cartas[df_cartas['nombre_normalizado'].str.contains(termino_normalizado, na=False)]
        
        else:
            print(">>> No hay término de búsqueda, mostrando todas las cartas.")
        
        lista_de_cartas = df_cartas.to_dict('records')

    except FileNotFoundError:
        print(">>> ERROR: No se encontró el archivo 'catalogo_cartas.xlsx'.")
        lista_de_cartas = []

    return render_template('index.html', titulo_web="Mi Catálogo de MyL", cartas=lista_de_cartas)