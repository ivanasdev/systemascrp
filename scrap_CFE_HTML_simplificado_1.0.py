'''
Librerías necesarias
'''
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
import pandas as pd
import time
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil import parser

#Dirección url de la página a escrapear
web = 'https://msc.cfe.mx/Aplicaciones/NCFE/Concursos/'
#Ruta donde se encuentre descargado chromedriver. 
#ruta = 'Users/administrador/Downloads/chromedriver_mac64' #Ruta Camilo
ruta = '/home/serverholos/Licy/chromedriver_linux64 # Ruta JM
#Ruta donde se guardarán los archivos html de los detalles extraídos
ruta_servidor = '/cfe/html/'

#Se crea una instancia al objeto webdriver, se le pasa el driver (chromedriver) como parámetro
driver = webdriver.Chrome(ruta)
#Se ejecuta la instancia y se pide abra el navegador
driver.get(web)

'''
    Parámetros de configuración de búsqueda y filtrado de datos
    La página que se escrapea posee algunos filtros para buscar las licitaciones.
    tipo_proc es un selector de la página web, si se desea consultar otro tipo de licitaciones
    cambiar Concurso abierto por el de su interés, por ejemplo 'Adjudicación directa, Concurso simplificado, etc.'
    Otro selector es el Estado. Igual que el anterior, puede cambiar el valor por uno correspon-
    diente a su necesidad: Adjudicado, Suspendido...
    Cuidar que el texto sea tal cual se encuentre en los selectores, respetando mayúsculas, minúsculas, etc. 
    De lo contrario la búsqueda no funcionará
    ****************************************************
    Para el caso de los días, es el número de días atrás que necesita consultar los registros
    Si la fecha actual es 24 de abril de 2023, y coloca 1, entonces buscará los registros del dia
    actual y el dia de ayer. Cambie por el número de días anteriores a los que desea consultar.
'''
tipo_proc = 'Concurso simplificado'
state = 'Vigente'
dias = 15

#Obtener el botón tipoProcedimiento y una vez localizado hacer click en él
tipo_procedimiento = driver.find_element(By.ID,'tipoProcedimiento')
tipo_procedimiento.click()
list_tipo_procedimiento = Select(driver.find_element(By.ID,'tipoProcedimiento'))
list_tipo_procedimiento.select_by_visible_text(tipo_proc)

#Obtener el botón estado de la página y dar click en él
estado = driver.find_element(By.ID,'estado')
estado.click()
list_estado = Selicitaciónlect(driver.find_element(By.ID,'estado'))
list_estado.select_by_visible_text(state)

#Obtener el botón buscar y dar click en él
tipo_procedimiento = driver.find_element(By.ID,'buscar')
tipo_procedimiento.click()
 
'''
    Código para obtener la fecha actual y realizar la diferencia de días, para poder obtener
    los registros que se encuentren en el rango [fecha actual, fecha final] 
'''
today = datetime.now()
hace_una_semana = today - timedelta(days=dias)
#hace_una_semana= hace_una_semana.strftime("%d-%m-%Y")
hace_una_semana = hace_una_semana.isoformat()
hace_una_semana = parser.parse(hace_una_semana)
hace_una_semana = str(hace_una_semana)
today = str(today)
#print("Día anterior: ")
#print(hace_una_semana)
#print('Hoy: ')
#print(today)


#Obtener la primera tabla de los headers
col_names = ['Número de Procedimiento','Testigo Social','Entidad Federativa', 'Descripción','Tipo de procedimiento','Tipo contratación','Fecha Publicación','Estado', 'Adjudicado A','Monto Adjudicado En Pesos','Detalle']
licitaciones = []
file_name = str(tipo_proc)+'.csv'
print(file_name)
#Localizar y extraer la tabla de los headers.
data = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="gridProcesos"]/table'))).get_attribute("outerHTML")
#Convertir la tabla en un dataframe para trabajar con los datos que contiene
data2  = pd.read_html(data, header=None, index_col=None) 
df1 = data2[0]
#print(df1.head(2))

#Convertir la columna Fecha de publicación como un bojeto de tipo fecha y tiempo
df1['Fecha Publicación'] = pd.to_datetime(df1['Fecha Publicación'],dayfirst=True)
#Obtener la fecha actual del sistema
today = datetime.now()
#Calcular la fecha del día final al que se desea realizar la consulta.
hace_una_semana = today - timedelta(days=dias)
hace_una_semana = hace_una_semana.isoformat()
today = str(today)
today = today[0:10]
print('hoy: ')
print(today)
hace_una_semana = parser.parse(hace_una_semana)
hace_una_semana = str(hace_una_semana)
hace_una_semana = hace_una_semana[0:10]
print('hace unos dias: ')
print(hace_una_semana)

#Crear un nuevo dataframe con los registros filtrados y que pertenecen al rango de fechas
#[díaFinal, hoy], fue necesario cambiar la fecha como index del dataframe para poder 
#realizar el filtrado
df2 = df1.set_index('Fecha Publicación')
print(df2)
#df2 = df2.loc[hace_una_semana:today]
#print(df2)
#Obtener el número de filas del nuevo dataframe, para saber cuantos registros se filtraron
rows_num = df2.shape[0]
#print('Num de filas '+str(rows_num))

'''
    Dado que se van a trabajar con distintas pestañas, una por cada registro de la tabla de los headers
    y poder cambiar el foco del driver a la nueva ventana abierta, y una vez extraídos los datos de los anexos,
    cerrar la pestaña se lleva un registro de la pestaña actual y la nueva.
'''
#Obtengo el id de la pestaña actual
window_after = driver.window_handles[0]

'''
    El siguiente bloque da click en los primeros registros de las licitaciones de la primera
    página de la tabla de los headers. De tal manera que extraiga los html de cada detalle de su
    respectiva licitación.
'''
aux=0
for i in range(rows_num):    
    aux+=1
    window_before = driver.window_handles[0]
    driver.switch_to.window(window_before)
    #Clic in detail
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div[16]/div/div[1]/table/tbody/tr['+str(aux)+']/td[11]/center/a/img').click()
    window_now = driver.window_handles[1]
    #switch to tab number i
    driver.switch_to.window(window_now)
    url_ = driver.current_url
    print(url_)
    time.sleep(4)
    html = driver.execute_script("return document.documentElement.outerHTML;")
    #obtener el código html de la página y se guarda en un objeto soup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #localicar y obtener el id de la licitación
    caja = soup.find('div', class_='page-header')
    id = caja.find('small').get_text()
    print(id)
    #Guardar la página html, cuyo nombre es el id de la licitación, actualmente se guarda
    #en la carpeta donde se guardan es en la carpeta donde se tenga el script
    #si se desea cambiar la ruta por /cfe/html/ comentar la línea siguiente y quitar el comentario a la línea 144
    with open("File"+id+".html", "w", encoding='utf-8') as file:
    #with open("/cfe/html/File"+id+".html", "w") as file:
        file.write(str(soup))
    file.close()
    driver.close()
window_before = driver.window_handles[0]
driver.switch_to.window(window_before)
time.sleep(1)


if (rows_num >= 10):
    while (rows_num >= 10):
        wait = WebDriverWait(driver, 20)
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div/div[16]/div/div[1]/div/a[3]/span")))
        next_button = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div[16]/div/div[1]/div/a[3]/span')
        driver.execute_script('arguments[0].click()',next_button)
        data = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="gridProcesos"]/table'))).get_attribute("outerHTML")
        data2  = pd.read_html(data, header=None, index_col=None) 
        df1 = data2[0]
        #print(df1.head(2))

        df1['Fecha Publicación'] = pd.to_datetime(df1['Fecha Publicación'], dayfirst=True)
        today = datetime.now()
        hace_una_semana = today - timedelta(days=dias)
        hace_una_semana = hace_una_semana.isoformat()
        today = str(today)
        today = today[0:10]
        print('hoy: ')
        print(today)
        hace_una_semana = parser.parse(hace_una_semana)
        hace_una_semana = str(hace_una_semana)
        hace_una_semana = hace_una_semana[0:10]
        print('hace unos dias: ')
        print(hace_una_semana)

        df2 = df1.set_index('Fecha Publicación')
        #df2 = df2.loc[hace_una_semana:today]

        rows_num = df2.shape[0]

        window_after = driver.window_handles[0]
        time.sleep(1)
        aux1=0
        for i in range(rows_num):    #Cambiar el 5 por 10
            aux1+=1
            window_before = driver.window_handles[0]
            driver.switch_to.window(window_before)
            #Clic in detail
            time.sleep(1)
            lupa = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div[16]/div/div[1]/table/tbody/tr['+str(aux1)+']/td[11]/center/a/img')
            driver.execute_script('arguments[0].click()',lupa)
            window_now = driver.window_handles[1]
            #switch to tab number i
            driver.switch_to.window(window_now)
            time.sleep(9)
            html = driver.execute_script("return document.documentElement.outerHTML;")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            caja = soup.find('div', class_='page-header')
            id = caja.find('small').get_text()
            print(id)
            print(soup.prettify())
            # with open("File"+id+".html", "w") as file:
            with open("File"+id+".html", "w", encoding='utf-8') as file:
                file.write(str(soup))
            file.close()
            driver.close()
        window_before = driver.window_handles[0]
        driver.switch_to.window(window_before)
        
'''


with open('arch2.json', 'w') as f:  
    writer = csv.writer(f)
    for licitacion in licitaciones:
        for k in licitaciones:
            writer.writerow([k])

'''
driver.quit()
# input("Esperando que no se cierre webdriver: ")