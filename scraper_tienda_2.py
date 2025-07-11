# scraper_tienda_2.py (CON PAGINACIÓN)

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL_BASE = 'https://mylserena.cl/singles-pb-1' 

edge_options = Options()
edge_options.add_argument("--log-level=3") 
servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)

resultados = []
numero_pagina = 1

while True:
    url_pagina_actual = f"{URL_BASE}?page={numero_pagina}"
    print(f"\n>>> Scrapeando Página {numero_pagina}: {url_pagina_actual}")

    try:
        driver.get(url_pagina_actual)
        time.sleep(3) # Pausa para que cargue

        html_final = driver.page_source
        soup = BeautifulSoup(html_final, 'html.parser')
        
        contenedores_de_cartas = soup.find_all('article', class_='product-block')
        print(f">>> Se encontraron {len(contenedores_de_cartas)} productos en la página actual.")

        if len(contenedores_de_cartas) == 0:
            print(">>> No se encontraron más productos. Finalizando scraping para esta tienda.")
            break

        for contenedor in contenedores_de_cartas:
            nombre_tag = contenedor.find('a', class_='product-block__name')
            precio_tag = contenedor.find('div', class_='product-block__price')
            if nombre_tag and precio_tag:
                nombre = nombre_tag.get_text(strip=True)
                precio_texto = precio_tag.get_text(strip=True).replace('$', '').replace('.', '')
                if precio_texto.isdigit():
                    precio_num = int(precio_texto)
                    resultados.append({'nombre': nombre, 'precio': precio_num, 'tienda': 'MyL Serena'})
        
        numero_pagina += 1

    except Exception as e:
        print(f">>> Ocurrió un error en la página {numero_pagina}: {e}")
        break

if 'driver' in locals() and driver:
    print("\n>>> Cerrando el navegador.")
    driver.quit()

if resultados:
    print(f"\nEn total, se recolectaron {len(resultados)} cartas. Guardando en archivo...")
    df_resultados = pd.DataFrame(resultados)
    nombre_archivo = 'precios_tienda_2.csv'
    df_resultados.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print(f"¡Éxito! Datos guardados en el archivo '{nombre_archivo}'")
else:
    print("\nNo se encontraron cartas con precio para guardar.")

print("=" * 50)
print("Script de Tienda 2 finalizado.")