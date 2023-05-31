# *** MUEVE TODOS LOS HTML DEL SCRAPING A LA CARPETA HTMLs ***

import os
import shutil

# Ruta de la carpeta actual
carpeta_actual = os.getcwd()

# Ruta de la carpeta "HTMLs"
carpeta_destino = os.path.join(carpeta_actual, "HTMLs")

# Crear la carpeta "HTMLs" si no existe
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Obtener la lista de archivos en la carpeta actual
archivos = os.listdir(carpeta_actual)

# Mover los archivos HTML a la carpeta "HTMLs"
for archivo in archivos:
    if archivo.endswith(".html"):
        # Ruta completa del archivo de origen
        ruta_origen = os.path.join(carpeta_actual, archivo)
        
        # Ruta completa del archivo de destino
        ruta_destino = os.path.join(carpeta_destino, archivo)
        
        # Mover el archivo, sobrescribiendo si existe
        shutil.move(ruta_origen, ruta_destino)
        print(f"Se movió {archivo} a la carpeta 'HTMLs'.")

print("Proceso completado.")

