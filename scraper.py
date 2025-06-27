# Paso 1: Importar todas las herramientas que necesitamos
import time
import pandas as pd # <-- Añadimos pandas para poder guardar el archivo CSV
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# La URL que sabemos que funciona
URL_OBJETIVO = 'https://el-senor-de-la-challa.jumpseller.com/mitos-y-leyendas/singles-primer-bloque-reedit-20' 

# Configuración de Selenium (no cambia)
edge_options = Options()
edge_options.add_argument("--log-level=3") 
servicio = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=servicio, options=edge_options)

print(f">>> Abriendo navegador MS Edge y conectando con: {URL_OBJETIVO}")

# Creamos una lista vacía al principio para guardar los resultados
resultados = []

try:
    driver.get(URL_OBJETIVO)

    # Lógica para aceptar cookies y esperar a que carguen los productos (no cambia)
    try:
        boton_cookies = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "accept-cookies")))
        print(">>> Banner de cookies encontrado. Haciendo clic en 'Aceptar'...")
        boton_cookies.click()
        time.sleep(1)
    except Exception as e:
        print(">>> No se encontró el banner de cookies, o ya fue aceptado. Continuando...")

    selector_contenedor = 'div.custom-col-4-in-row'
    print(f">>> Esperando a que los productos con el selector '{selector_contenedor}' aparezcan...")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector_contenedor)))
    print(">>> ¡Productos encontrados!")
    
    html_final = driver.page_source
    
    # Lógica de análisis con BeautifulSoup (no cambia)
    soup = BeautifulSoup(html_final, 'html.parser')
    contenedores_de_cartas = soup.find_all('div', class_='custom-col-4-in-row')
    print(f">>> Se encontraron {len(contenedores_de_cartas)} productos en la página.")

    for contenedor in contenedores_de_cartas:
        nombre_tag = contenedor.find('a', class_='title')
        precio_tag = contenedor.find('div', class_='current')
        if nombre_tag and precio_tag:
            nombre = nombre_tag.get_text(strip=True)
            precio_texto = precio_tag.get_text(strip=True).replace('$', '').replace('.', '')
            if precio_texto.isdigit():
                precio_num = int(precio_texto)
                # En lugar de imprimir aquí, guardamos en la lista 'resultados'
                resultados.append({'nombre': nombre, 'precio': precio_num})

except Exception as e:
    print(f">>> Ocurrió un error general durante el scraping: {e}")

finally:
    # Cerramos el navegador siempre
    if 'driver' in locals() and driver:
        print(">>> Cerrando el navegador.")
        driver.quit()

# --- ESTA ES LA PARTE NUEVA Y FINAL ---
# Paso 2: Después de cerrar el navegador, revisamos si tenemos resultados y los guardamos.
if resultados:
    print(f"\nSe recolectaron {len(resultados)} cartas con precio. Guardando en archivo...")
    
    # Convertimos nuestra lista de resultados a un DataFrame de pandas
    df_resultados = pd.DataFrame(resultados)
    
    # Definimos el nombre de nuestro "archivador"
    nombre_archivo = 'precios_tienda_1.csv'
    
    # Usamos la función to_csv de pandas para guardar los datos.
    df_resultados.to_csv(nombre_archivo, index=False, encoding='utf-8')
    
    print(f"¡Éxito! Datos guardados en el archivo '{nombre_archivo}'")
    
else:
    print("\nNo se encontraron cartas con precio para guardar.")

print("=" * 50)
print("Script finalizado.")