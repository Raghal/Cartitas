# scraper_tienda_4.py (CON LIMPIEZA DE NOMBRES)

import time
import pandas as pd
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_BASE = 'https://jpstore.cl/categoria-producto/ediciones-2/ediciones/primer-bloque-ediciones/'

# ... (la configuración de Selenium se mantiene igual) ...
edge_options = Options()
edge_options.add_argument("--log-level=3")
servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)

resultados = []
numero_pagina = 1

while True:
    url_pagina_actual = f"{URL_BASE}page/{numero_pagina}/"
    print(f"\n>>> Scrapeando Página {numero_pagina} en JP Store...")
    # ... (el resto del bucle se mantiene igual hasta el for) ...
    try:
        driver.get(url_pagina_actual)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "products")))
        
        html_final = driver.page_source
        soup = BeautifulSoup(html_final, 'html.parser')
        
        contenedores_de_cartas = soup.find_all('li', class_='product')
        print(f">>> Se encontraron {len(contenedores_de_cartas)} productos.")

        if not contenedores_de_cartas:
            print(">>> Fin de la paginación.")
            break

        for contenedor in contenedores_de_cartas:
            nombre_tag = contenedor.find('h3', class_='products-title')
            precio_tag = contenedor.find('span', class_='price')
            
            if contenedor.find('a', class_='add_to_cart_button') and nombre_tag and precio_tag:
                # --- LÓGICA DE LIMPIEZA APLICADA AQUÍ TAMBIÉN ---
                nombre_sucio = nombre_tag.find('a').get_text(strip=True)
                nombre_limpio = nombre_sucio # JP Store parece no tener el texto extra, pero lo dejamos por si acaso
                
                precio_span = precio_tag.find('span', class_='woocommerce-Price-amount')
                if precio_span:
                    precio_texto = precio_span.get_text(strip=True).replace('$', '').replace('.', '')
                    if precio_texto.isdigit():
                        precio_num = int(precio_texto)
                        resultados.append({'nombre': nombre_limpio, 'precio': precio_num, 'tienda': 'JP Store'})
        
        numero_pagina += 1
        time.sleep(random.uniform(4, 8))

    except Exception as e:
        print(f">>> Ocurrió un error: {e}")
        break

# ... (el resto del código para guardar el CSV se mantiene igual) ...
if 'driver' in locals() and driver: driver.quit()
if resultados:
    print(f"\nTotal: {len(resultados)} cartas. Guardando...")
    pd.DataFrame(resultados).to_csv('precios_tienda_4.csv', index=False, encoding='utf-8')
    print("¡Éxito! Archivo 'precios_tienda_4.csv' creado/actualizado.")
else:
    print("\nNo se encontraron cartas.")
print("=" * 50)