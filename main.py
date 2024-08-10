import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

# Función para leer los datos desde un archivo CSV
def cargar_datos_csv(archivo_csv):
    datos = []
    try:
        # Intenta abrir el archivo CSV con la codificación 'utf-8'
        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                datos.append({
                    "dni": row["DNI"],
                    "nombres": row["Nombres"],
                    "apellido_paterno": row["Apellido Paterno"],
                    "apellido_materno": row["Apellido Materno"]
                })
    except UnicodeDecodeError:
        # Si ocurre un error, intenta con una codificación alternativa
        with open(archivo_csv, newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                datos.append({
                    "dni": row["DNI"],
                    "nombres": row["Nombres"],
                    "apellido_paterno": row["Apellido Paterno"],
                    "apellido_materno": row["Apellido Materno"]
                })
    return datos

# Ruta del archivo CSV con los datos de DNI y nombre
archivo_csv = 'dni_data.csv'
archivo_no_coincidentes = 'no_coincidentes.csv'

# Cargar datos desde el archivo CSV
dni_list = cargar_datos_csv(archivo_csv)

# URL de la web específica
url = "https://eldni.com/pe/buscar-datos-por-dni"

# Inicializa el controlador del navegador (Chrome en este caso)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Lista para almacenar los resultados no coincidentes
no_coincidentes = []

# Número máximo de reintentos
max_reintentos = 1

for entry in dni_list:
    dni = entry["dni"]
    nombres_csv = entry["nombres"]
    apellido_paterno_csv = entry["apellido_paterno"]
    apellido_materno_csv = entry["apellido_materno"]

    intento = 0
    encontrado = False

    while intento < max_reintentos and not encontrado:
        try:
            # Abre la web
            driver.get(url)

            # Encuentra el campo de texto del DNI e ingresa el número
            dni_field = driver.find_element(By.ID, "dni")
            dni_field.clear()
            dni_field.send_keys(dni)

            # Hacer clic en el botón de búsqueda
            buscar_button = driver.find_element(By.ID, "btn-buscar-datos-por-dni")
            buscar_button.click()

            # Espera a que se cargue la tabla con los resultados
            time.sleep(1)  # Ajusta el tiempo si es necesario

            # Verifica si se ha cargado la tabla con los datos
            try:
                # Busca la tabla dentro del div con id "column-center"
                column_center = driver.find_element(By.ID, "column-center")
                tables = column_center.find_elements(By.TAG_NAME, "table")
                if not tables:
                    raise Exception("No se encontró ninguna tabla en el div con id 'column-center'.")

                table = tables[0]  # Obtiene la primera tabla
                tbody = table.find_element(By.TAG_NAME, "tbody")
                filas = tbody.find_elements(By.TAG_NAME, "tr")

                encontrado = False

                # Extrae los datos del nombre en la tabla
                for fila in filas:
                    columnas = fila.find_elements(By.TAG_NAME, "td")
                    if len(columnas) >= 4:
                        dni_result = columnas[0].text.strip()
                        nombres_result = columnas[1].text.strip()
                        apellido_paterno_result = columnas[2].text.strip()
                        apellido_materno_result = columnas[3].text.strip()

                        # Mostrar los valores obtenidos de la web
                        print(f"Valores obtenidos de la web: DNI: {dni_result}, Nombres: {nombres_result}, Apellido Paterno: {apellido_paterno_result}, Apellido Materno: {apellido_materno_result}")

                        if (dni == dni_result and
                            nombres_csv == nombres_result and
                            apellido_paterno_csv == apellido_paterno_result and
                            apellido_materno_csv == apellido_materno_result):
                            encontrado = True
                            break

                        # Actualiza los datos en caso de discrepancia
                        if (dni == dni_result):
                            no_coincidentes.append({
                                "dni": dni_result,
                                "nombres": nombres_result,
                                "apellido_paterno": apellido_paterno_result,
                                "apellido_materno": apellido_materno_result
                            })
                            print(f"Valor no coincidente almacenado: DNI {dni_result}, Nombres {nombres_result}, Apellido Paterno {apellido_paterno_result}, Apellido Materno {apellido_materno_result}")

                if encontrado:
                    print(f"Coincide: DNI {dni} ({nombres_csv} {apellido_paterno_csv} {apellido_materno_csv})")
                else:
                    print(f"No coincide: DNI {dni} ({nombres_csv} {apellido_paterno_csv} {apellido_materno_csv})")
                    no_coincidentes.append({
                        "dni": dni,
                        "nombres": nombres_csv,
                        "apellido_paterno": apellido_paterno_csv,
                        "apellido_materno": apellido_materno_csv
                    })
                    print(f"Valor no coincidente almacenado: DNI {dni}, Nombres {nombres_csv}, Apellido Paterno {apellido_paterno_csv}, Apellido Materno {apellido_materno_csv}")

            except Exception as e:
                print(f"Error al procesar el DNI {dni}: {e}")
                intento += 1
                time.sleep(1)  # Pausa antes del siguiente intento

        except Exception as e:
            print(f"Error al procesar el DNI {dni}: {e}")
            intento += 1
            time.sleep(1)  # Pausa antes del siguiente intento

# Cierra el navegador
driver.quit()

# Guardar los resultados no coincidentes en un nuevo archivo csv
with open(archivo_no_coincidentes, mode="w", newline='', encoding='utf-8') as csvfile:
    fieldnames = ["dni", "nombres", "apellido_paterno", "apellido_materno"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for entry in no_coincidentes:
        writer.writerow(entry)

    print("Datos no coincidentes guardados en el archivo:", archivo_no_coincidentes)
    for entry in no_coincidentes:
        print(f"DNI {entry['dni']} ({entry['nombres']} {entry['apellido_paterno']} {entry['apellido_materno']}) no coincide.")
