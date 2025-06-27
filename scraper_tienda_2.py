# scraper_tienda_2.py (Versión Corregida)

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL_OBJETIVO = 'https://mylserena.cl/singles-pb-1' 

edge_options = Options()
edge_options.add_argument("--log-level=3") 
servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)

print(f">>> Abriendo navegador para Tienda 2: {URL_OBJETIVO}")

resultados = []

try:
    driver.get(URL_OBJETIVO)

    print(">>> Esperando 5 segundos a que la página cargue...")
    time.sleep(5) 

    html_final = driver.page_source

    soup = BeautifulSoup(html_final, 'html.parser')

    # --- CAMBIO CLAVE 1: Usamos el selector correcto que encontramos en el HTML. ---
    contenedores_de_cartas = soup.find_all('article', class_='product-block')
    print(f">>> Se encontraron {len(contenedores_de_cartas)} productos en la página.")

    for contenedor in contenedores_de_cartas:
        # --- CAMBIO CLAVE 2: Usamos los selectores correctos para nombre y precio. ---
        nombre_tag = contenedor.find('a', class_='product-block__name')
        precio_tag = contenedor.find('div', class_='product-block__price')

        if nombre_tag and precio_tag:
            nombre = nombre_tag.get_text(strip=True)
            precio_texto = precio_tag.get_text(strip=True).replace('$', '').replace('.', '')

            if precio_texto.isdigit():
                precio_num = int(precio_texto)
                resultados.append({'nombre': nombre, 'precio': precio_num, 'tienda': 'MyL Serena'})

except Exception as e:
    print(f">>> Ocurrió un error general durante el scraping: {e}")

finally:
    if 'driver' in locals() and driver:
        print(">>> Cerrando el navegador.")
        driver.quit()

if resultados:
    print(f"\nSe recolectaron {len(resultados)} cartas. Guardando en archivo...")
    df_resultados = pd.DataFrame(resultados)

    nombre_archivo = 'precios_tienda_2.csv'

    df_resultados.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print(f"¡Éxito! Datos guardados en el archivo '{nombre_archivo}'")
else:
    print("\nNo se encontraron cartas con precio para guardar.")

print("=" * 50)
print("Script de Tienda 2 finalizado.")