# scraper_tienda_1.py (CON PAGINACIÓN)

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL Base, sin el número de página
URL_BASE = 'https://el-senor-de-la-challa.jumpseller.com/mitos-y-leyendas/singles-primer-bloque-reedit-20' 

edge_options = Options()
edge_options.add_argument("--log-level=3") 
servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)

# La lista de resultados se define AFUERA del bucle para que acumule todas las cartas
resultados = []
numero_pagina = 1

# --- INICIO DEL BUCLE DE PAGINACIÓN ---
while True:
    # Construimos la URL para la página actual
    url_pagina_actual = f"{URL_BASE}?page={numero_pagina}"
    print(f"\n>>> Scrapeando Página {numero_pagina}: {url_pagina_actual}")

    try:
        driver.get(url_pagina_actual)
        
        # En la primera página, manejamos las cookies
        if numero_pagina == 1:
            try:
                boton_cookies = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "accept-cookies")))
                print(">>> Banner de cookies encontrado. Haciendo clic...")
                boton_cookies.click()
                time.sleep(1)
            except Exception as e:
                print(">>> No se encontró el banner de cookies. Continuando...")
        else:
            # Para las páginas siguientes, una pequeña pausa es suficiente
            time.sleep(2)

        html_final = driver.page_source
        soup = BeautifulSoup(html_final, 'html.parser')
        
        contenedores_de_cartas = soup.find_all('div', class_='custom-col-4-in-row')
        print(f">>> Se encontraron {len(contenedores_de_cartas)} productos en la página actual.")

        # --- Condición de salida del bucle ---
        # Si no se encuentran productos, significa que llegamos al final.
        if len(contenedores_de_cartas) == 0:
            print(">>> No se encontraron más productos. Finalizando scraping para esta tienda.")
            break # Rompemos el bucle while

        for contenedor in contenedores_de_cartas:
            nombre_tag = contenedor.find('a', class_='title')
            precio_tag = contenedor.find('div', class_='current')
            if nombre_tag and precio_tag:
                nombre = nombre_tag.get_text(strip=True)
                precio_texto = precio_tag.get_text(strip=True).replace('$', '').replace('.', '')
                if precio_texto.isdigit():
                    precio_num = int(precio_texto)
                    resultados.append({'nombre': nombre, 'precio': precio_num, 'tienda': 'El Señor de la Challa'})
        
        # Pasamos a la siguiente página para la próxima iteración
        numero_pagina += 1

    except Exception as e:
        print(f">>> Ocurrió un error en la página {numero_pagina}: {e}")
        break # Si hay un error grave, también salimos del bucle
# --- FIN DEL BUCLE DE PAGINACIÓN ---

# Cerramos el navegador una vez que el bucle termina
if 'driver' in locals() and driver:
    print("\n>>> Cerrando el navegador.")
    driver.quit()

# Guardamos TODOS los resultados recolectados
if resultados:
    print(f"\nEn total, se recolectaron {len(resultados)} cartas. Guardando en archivo...")
    df_resultados = pd.DataFrame(resultados)
    nombre_archivo = 'precios_tienda_1.csv'
    df_resultados.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print(f"¡Éxito! Datos guardados en el archivo '{nombre_archivo}'")
else:
    print("\nNo se encontraron cartas con precio para guardar.")

print("=" * 50)
print("Script de Tienda 1 finalizado.")