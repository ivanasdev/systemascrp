# PROCESO DE EJECUCIÓN DE SCRAPING

# Extrae los archivos HTML de Concurso abierto
python3 /home/jmorozco/python/Licy/scrap_CFE_HTML_abierto_1.0.py

# Extrae los archivos HTML de Concurso simplificado
python3 /home/jmorozco/python/Licy/scrap_CFE_HTML_simplificado_1.0.py

# Crea los archivos de datos en base a los htmls
python3 /home/jmorozco/python/Licy/parse_CFE_Detail_1.0.py

# Mueve los archivos extraidos a la carpeta de respaldo HTMLs
python3 /home/jmorozco/python/Licy/mueve_htmls.py
