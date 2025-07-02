# scraper_tienda_3.py (Paginación y Selectores Corregidos Definitivamente)

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL_BASE = 'https://www.pandorastore.cl/singles-primer-bloque-myl'

edge_options = Options()
edge_options.add_argument("--log-level=3")
edge_options.add_argument("--disable-blink-features=AutomationControlled")
edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
edge_options.add_experimental_option('useAutomationExtension', False)

servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})

resultados = []
numero_pagina = 1

while True:
    url_pagina_actual = f"{URL_BASE}?page={numero_pagina}"
    
    print(f"\n>>> Scrapeando Página {numero_pagina}: {url_pagina_actual}")

    try:
        driver.get(url_pagina_actual)
        time.sleep(4)

        html_final = driver.page_source
        soup = BeautifulSoup(html_final, 'html.parser')
        
        # Usamos los selectores correctos que encontramos en tu archivo pagina_pandora_final.html
        contenedores_de_cartas = soup.find_all('article', class_='product-block')
        print(f">>> Se encontraron {len(contenedores_de_cartas)} productos en la página actual.")

        if not contenedores_de_cartas:
            print(">>> No se encontraron más productos. Finalizando scraping.")
            break

        for contenedor in contenedores_de_cartas:
            nombre_tag = contenedor.find('a', class_='product-block__name')
            precio_tag = contenedor.find('div', class_='product-block__price')
            
            if nombre_tag and precio_tag:
                nombre = nombre_tag.get_text(strip=True)
                texto_a_quitar = "- SINGLES MITOS Y LEYENDAS"
                nombre_limpio = nombre.upper().replace("- SINGLES MITOS Y LEYENDAS", "").strip()
                precio_texto = precio_tag.get_text(strip=True).replace('$', '').replace('.', '')
                if precio_texto.isdigit():
                    precio_num = int(precio_texto)
                    resultados.append({'nombre': nombre, 'precio': precio_num, 'tienda': 'Pandora Store'})
        
        numero_pagina += 1

    except Exception as e:
        print(f">>> Ocurrió un error en la página {numero_pagina}: {e}")
        break

if 'driver' in locals() and driver:
    driver.quit()

if resultados:
    print(f"\nTotal recolectado: {len(resultados)} cartas. Guardando...")
    df_resultados = pd.DataFrame(resultados)
    nombre_archivo = 'precios_tienda_3.csv'
    df_resultados.to_csv(nombre_archivo, index=False, encoding='utf-8')
    print(f"¡Éxito! Datos guardados en '{nombre_archivo}'")
else:
    print("\nNo se encontraron cartas con precio para guardar.")

print("=" * 50)
print("Script de Tienda 3 (Pandora Store) finalizado.")