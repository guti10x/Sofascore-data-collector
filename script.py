# Dependencias
from PyQt6.QtWidgets import QApplication, QDialog, QGridLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QFileDialog, QWidget, QTextEdit, QProgressBar, QVBoxLayout, QTextEdit, QComboBox
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtCore import QMetaObject, Qt, pyqtSignal, Q_ARG
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import threading
import os
import regex 
import json
import time

headers = {
    "X-RapidAPI-Key": "11822210cdmsha855c4a12c471b5p18100fjsn3972b17b3be8",
    "X-RapidAPI-Host": "sofascore.p.rapidapi.com"
}

class SimpleWindow(QDialog):
    def __init__(self, parent=None):
        super(SimpleWindow, self).__init__(parent)

        self.progress = 0
        self.ruta_jornada=""
        self.slugJson=""

        # Crear un diseño de cuadrícula
        layout = QGridLayout(self)
        # Establecer el tamaño máximo de la segunda columna
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)

        # Variables para almacenar la carpeta y la ruta seleccionadas
        self.selected_folder = ""
        self.selected_path = ""
        
        self.driver = None

        ### SELECCIONAR EQUIPO INPUT ####################################################
        # INPUT NOMBRRE EQUIPO 
        label_equipo = QLabel("Equipo a scrapear:")
        # Aliniación
        layout.addWidget(label_equipo, 0, 0)

        # Lista de equipos
        teams = ["Real Madrid", "Barcelona", "Atl. de Madrid", "Valencia", "Sevilla", "Villarreal",
                 "Real Sociedad", "Real Betis", "Athletic Club", "Celta Vigo", "Almeria", "Getafe",
                 "Mallorca", "Girona", "Granada", "", "Alavés", "Rayo Vallecano", "Osasuna", "Las Palmas"]

        # Crear un QComboBox y agregar los equipos
        self.team_combobox = QComboBox(self)
        self.team_combobox.addItems(teams)
        # Aliniación
        layout.addWidget(self.team_combobox, 0, 1)
        # Estilos 
        self.team_combobox.setFixedWidth(120)
        
        ### SELECCIONAR JORNADA INPUT ####################################################
        # INPUT NÚMERO JORNADA 
        label_number = QLabel("Jornada a scrapear:")
        layout.addWidget(label_number, 1, 0)
        # Estilos 
        self.number_input = QSpinBox(self)
        self.number_input.setMinimum(11)  # Establecer el valor mínimo (jornada 1)
        self.number_input.setMaximum(38)  # Establecer el valor máximo (Jornada 36)
        self.number_input.setSingleStep(2)  # Establecer el paso
        self.number_input.setMaximumSize(45, 20)
        self.number_input.setMinimumSize(45, 20)
        # Aliniación
        layout.addWidget(self.number_input, 1, 1)
        

        #------- GAP vacio -----------------------------------------
        empty_widget = QWidget()
        empty_widget.setFixedHeight(10)  # Tamaño del gap (10 px)
        layout.addWidget(empty_widget, 2, 0)
        #-----------------------------------------------------------


        ###  SELECCIONAR RUTA DONDE GUARDAR EL EXCEL OUTPUT DEL SCRAPER  #################
        # LABEL TEXTO 
        label_text = QLabel("Ruta output scraper:")
        layout.addWidget(label_text, 3, 0)

        # INPUT TEXTO (QLineEdit en lugar de QSpinBox)
        self.text_input = QLineEdit(self)
        # Alineación
        layout.addWidget(self.text_input, 3, 1)
        # Estilos 
        self.text_input.setMinimumWidth(350)
        

        # BOTÓN PARA SELECCIONAR CARPETA
        select_folder_button = QPushButton("Seleccionar Carpeta")
        select_folder_button.clicked.connect(self.select_folder)
        # Alineación  
        layout.addWidget(select_folder_button, 4, 1, alignment=Qt.AlignmentFlag.AlignRight)
        # Estilos 
        select_folder_button.setMinimumWidth(140)

        #------- GAP vacio -----------------------------------------
        empty_widget = QWidget()
        empty_widget.setFixedHeight(20)  # Tamaño del gap (10 px)
        layout.addWidget(empty_widget, 5, 0)
        #-----------------------------------------------------------


        ###  BOTÓN PARA INICIAR SCRAPER  ################################################
        # Crear un botón llamado "Scrapear"
        scrape_button = QPushButton("Scrapear")

        # Conectar la señal clicked del botón a la función iniciar_scrapear_thread e iniciar barra progreso
        scrape_button.clicked.connect(self.iniciar_scrapear_thread)
        scrape_button.clicked.connect(self.start_progress)

        # Alineación 
        layout.addWidget(scrape_button, 6, 0)
        # Estilos
        self.number_input.setMaximumSize(38, 20)


        ###  BARRA DE PROGRESO  ################################################
        # Crear Barra de progreso
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)


        ###  VENTANA OUTPUT SCRAPER  ####################################################
        # Crear un QTextEdit para la salida
        self.output_textedit = QTextEdit(self)
        layout.addWidget(self.output_textedit, 7, 0, 2, 0)  # row, column, rowSpan, columnSpan


        ###  ESTABLECER DISEÑO DE LA VENTANA  ###########################################
        self.setMinimumSize(500, 500) # Configurar el tamaño mínimo de la ventana
        # Configurar el diseño para la ventana
        self.setLayout(layout)

        # Configurar el título de la ventana
        self.setWindowTitle("Mister Fantasy Mundo Deportivo Scraper")

        # Evento cerrar ventana 
        self.destroyed.connect(self.cleanup)

    def select_folder(self):
        # Obtener el directorio del script de Python
        script_directory = os.path.dirname(__file__)
        
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", script_directory)
        if folder_path:
            # Actualizar las variables de clase con la carpeta y la ruta seleccionadas
            self.selected_folder = folder_path
            self.selected_path = folder_path

            # Actualizar el QLineEdit con la ruta seleccionada
            self.text_input.setText(self.selected_path)

    def cleanup(self):
        # Realizar cualquier limpieza necesaria aquí
        QApplication.quit()

    def start_progress(self):
        # Establecer el rango de la barra de progreso según tus necesidades
        self.progress_bar.setRange(0, 511)

        ruta_output = self.text_input.text()
        if ruta_output!="":
            self.progress_bar.setValue(0)

    def iniciar_scrapear_thread(self):  
        # Crear un hilo y ejecutar la función en segundo plano
        thread = threading.Thread(target=self.scrapear_funcion)
        thread.start()

    def invocar_actualizacion(self, nuevo_valor):
        QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.ConnectionType.QueuedConnection, Q_ARG(int, nuevo_valor))


    def performance_to_json(self,JsonJugador):
        
        # Crear carpeta para la jornada
        if not os.path.exists(self.ruta_jornada):
            os.makedirs(self.ruta_jornada)

        nombre_archivo = f"performance_jugadores_partido_{self.slugJson}.json"
        ruta_completa_archivo = os.path.join(self.ruta_jornada, nombre_archivo)
        
        # Verificar si el archivo JSON existe
        if os.path.exists(ruta_completa_archivo):
            # Si el archivo existe, cargar su contenido
            with open(ruta_completa_archivo, 'r') as archivo:
                datos = json.load(archivo)
        else:
            # Si el archivo no existe, crear un diccionario vacío
            datos = {}
        # Actualizar el diccionario existente con la nueva entrada
        datos.update(JsonJugador)
        
        # Guardar los datos actualizados en el archivo JSON
        if not os.path.exists(ruta_completa_archivo):
            with open(ruta_completa_archivo, 'w') as archivo:
                archivo.write("{}")  # Crea un archivo vacío si no existe
        with open(ruta_completa_archivo, 'w') as archivo:
            json.dump(datos, archivo, indent=4)

    def obtener_informacion_jugador(self):

        # Obtiene el contenido HTML de la página
        pagina_html = self.driver.page_source
        #print(pagina_html)

        # Utiliza BeautifulSoup para analizar el HTML
        soup = BeautifulSoup(pagina_html, 'html.parser')

        try:        
            nombre= self.driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[3]/div/div/div/div[1]/div/div[1]/a/div')
            self.output_textedit.append("_______________________________")
            self.output_textedit.append(nombre.text)
            
            try:
                puntuacion= self.driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[3]/div/div/div/div[1]/div/div[2]/div/span')
                self.output_textedit.append(puntuacion.text)

                self.output_textedit.append("_______________________________")

                # DEVOLVER TODOS LOS PARÁMETROS DE RENDIMIENTO DEL JUGADOR: encontrar todos los div con la clase "sc-fqkvVR sc-dcJsrY litZes eFJwJL"
                entradas = []
                goal_elements = soup.find_all('div', class_='sc-fqkvVR sc-dcJsrY litZes eFJwJL')
                for element in goal_elements:
                    
                    # Encuentra el div con la clase "sc-jEACwC hFGVAX" y el span con la clase "sc-jEACwC jnyhQn" dentro de este div
                    div_goal = element.find('div', class_='sc-jEACwC hFGVAX')
                    span_goal = element.find('span', class_='sc-jEACwC jnyhQn')
                    if div_goal and span_goal:
                        self.output_textedit.append(div_goal.text)
                        self.output_textedit.append(span_goal.text)

                        estadisticas = {}
                        clave = div_goal.text
                        valor = span_goal.text
                        estadisticas[clave] = valor

                        entrada = {
                            clave: valor
                        }

                        # Agrega la entrada JSON a la lista
                        entradas.append(entrada)
                        
                    nombreJson=nombre.text
                    puntuaciónJson=puntuacion.text
            
                    # Crear el diccionario para el jugador
                    JsonJugador = {
                        nombreJson: {
                            "puntuacion": puntuaciónJson,
                            "estadisticas": entradas
                        }
                    }
                    
                    self.performance_to_json(JsonJugador)

            except NoSuchElementException as e:
                self.output_textedit.append("Sin jugar")
                self.output_textedit.append("_______________________________")
                
                entradas = []
                estadisticas = {}
                clave = "Minutes played"
                valor = 0
                estadisticas[clave] = valor

                entrada = {
                    clave: valor
                }

                # Agrega la entrada JSON a la lista
                entradas.append(entrada)
                
                nombreJson=nombre.text
                puntuaciónJson=None
            
                # Crear el diccionario para el jugador
                JsonJugador = {
                        nombreJson: {
                            "puntuacion": puntuaciónJson,
                            "estadisticas": entradas
                        }
                }
                
                self.performance_to_json(JsonJugador)
                
                return

        except NoSuchElementException as e:
            try:
                manager= self.driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[2]/div/div/div[1]/div[1]/div/div[2]/div[2]/div/div/span')
                self.output_textedit.append("Entrenador")
            except:
                self.output_textedit.append("No convocado")
        self.output_textedit.append("_______________________________")

    def scrapear_funcion(self):
        self.output_textedit.append("Conecting to API...")

        # GESTIÓN DEL INPUT DEL USUARIO
        selected_team = self.team_combobox.currentText()
        ruta_output = self.text_input.text()
        jornada=int(self.number_input.value())

        # Mostrar el valor en el QTextEdit
        self.output_textedit.append(f"Equipo seleccionado: {selected_team}")
        self.output_textedit.append(f"Jornada seleccionada: {jornada}")
        self.output_textedit.append(f"Ruta para la salida del scraper selecionada: {ruta_output}")

        if ruta_output=="":
            output_textedit = self.output_textedit
            color_rojo = QColor(255, 0, 0)  # Valores RGB para rojo
            formato_rojo = QTextCharFormat()
            formato_rojo.setForeground(color_rojo)
            output_textedit.mergeCurrentCharFormat(formato_rojo)
            output_textedit.insertPlainText("\n¡La jornada no está inicializada!, Configúrala antes de empezar a scrapear")
            formato_negro = QTextCharFormat()
            formato_negro.setForeground(QColor(0, 0, 0))
            output_textedit.mergeCurrentCharFormat(formato_negro)
            return
        
        ############################################  eliminar excell a scrapear si ya existe !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ##############################################################################################################################################################
        # FASE 1: Obtener la url de la pagina web de Sofaescore de todas los partidos de LaLiga                                                                      #
        ##############################################################################################################################################################

        #######################################################################################################################################################
        #  PARTE 1 : Mediante una request a la API de Sofaescore obtenemos el id de todos los equipos de LaLiga para posteriores cnsultas                     #
        #######################################################################################################################################################

        url = "https://sofascore.p.rapidapi.com/teams/search"

        id_equipo = None
        valor_round = None
        slugJson = None

        self.output_textedit.append(f"________________________________________________________________________________________")
        self.output_textedit.append("Obteniendo id del equipo de LaLiga...")

        response = requests.get(url, headers=headers, params={"name": selected_team})
        data = response.json()
        if data['teams']:
            id_equipo = data['teams'][0]['id']
            self.output_textedit.append(f"GET ID {selected_team}: {id_equipo}")  

        #######################################################################################################################################################
        #  PARTE 2 : Mediante una request a la API de Sofaescore obtenemos informacion de todos los equipos de LaLiga                                         #
        #######################################################################################################################################################
        time.sleep(1)
        url = "https://sofascore.p.rapidapi.com/teams/get-last-matches"
        ultimo_partido_equipos = None
        liga="LaLiga"
        ulimo_partido=None

        self.output_textedit.append(f"________________________________________________________________________________________")  
        self.output_textedit.append(f"Obteniendo partido de la jornada {jornada} del {liga}...")

        querystring = {"teamId": str(id_equipo), "pageIndex": "0"}

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            partido=0
            while True: 
                valor_round = data['events'][partido]['roundInfo']['round']
                tournament = data['events'][partido]['tournament']['name']
                        
                if valor_round==jornada and tournament==liga:
                    nombre=data['events'][partido]['slug']
                    self.output_textedit.append(f"GET partido: {nombre}")
                    
                    ulimo_partido=data['events'][partido]

                    valor_round = data['events'][partido]['roundInfo']['round']
                    break
                partido+=1
        else:
             self.output_textedit.append(f"Error al obtener datos para el equipo {selected_team}. Código de estado: {response.status_code}")
                
        nombre_carpeta_jornada = "jornada_" + str(valor_round)
        self.ruta_jornada = os.path.join(ruta_output, nombre_carpeta_jornada,"json")
        
        ##########################################3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1revisar nombre output

        #######################################################################################################################################################       
        #  PARTE 3 : Mediante los datos obtenidos de la API cosntruimos la url de cada patido de todos los equipos de LaLiga                                  #
        #######################################################################################################################################################
        time.sleep(1)
        #Obtener componenets de la url   
        id = ulimo_partido.get('id')
        slug = ulimo_partido.get('slug')
        customId = ulimo_partido.get('customId')

        base_url = "https://www.sofascore.com/{}/{}#{}"

        self.output_textedit.append(f"________________________________________________________________________________________")  
        self.output_textedit.append("Generando urls del último partido de cada equipo...")

        #Fusionar elementos de la url
        url = base_url.format(id,customId,slug)
        self.output_textedit.append(url)

        ##############################################################################################################################################################
        # FASE 2: "Acceder y hacer scraping de todos las urls de todos los partidos de LaLiga                                                                        #
        ##############################################################################################################################################################

        #######################################################################################################################################################
        #  PARTE 1 : obtener el performance de los 22 jugadores titulares del partido                                                                         # 
        #    -abre la web                                                                                                                                     #
        #    -acepta las cookies                                                                                                                              #
        #    -hace click sobre de cada jugador para que emerja la tarjeta con los datos del performance del partido asociados a cada jugador y los extrae)    #
        #######################################################################################################################################################
        self.output_textedit.append(f"________________________________________________________________________________________")  
        self.output_textedit.append("Starting scraper...")

        self.driver = webdriver.Chrome()

        # Maximizar la ventana del navegador
        self.driver.maximize_window()
        
        # Navega a la página web que deseas hacer scraping
        self.driver.get(url)

        # Espera a que se cargue la página
        self.driver.implicitly_wait(20)

        # Encuentra el botón de "Consentir" 
        button = self.driver.find_element(By.XPATH, '//button[@aria-label="Consentir"]')
        # Haz clic en el botón de "Consentir" 
        button.click()
        try:
            # Encuentra el botón de "Ask me later" 
            button = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[2]/button')
            # Haz clic en el botón de "Consentir" 
            button.click()
        except:
            pass
        
        # Encuentra el nombre del partido" 
        local = self.driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[1]/div/a/div/div/bdi')
        visitante = self.driver.find_element(By.XPATH, '//*[@id="__next"]/main/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div/div[3]/div/a/div/div/bdi')
        # Concatenar los nombres para formar slugJson
        slugJsonConcatenado = f"{local.text}_{visitante.text}"
        self.slugJson = slugJsonConcatenado.replace(" ", "_")
        self.output_textedit.append(f"Scraping {self.slugJson}...")

        # Encuentra todos los elementos 
        divSuplentes1 = self.driver.find_elements(By.XPATH, '//div[@display="flex" and contains(@class, "sc-fqkvVR sc-dcJsrY bASBgQ kHiXJe")]')
        divSuplentes2 = self.driver.find_elements(By.XPATH, '//div[@display="flex" and contains(@class, "sc-fqkvVR sc-dcJsrY bphgaj kHiXJe")]')
        
        # Crear un nuevo array y combinar los elementos de divSuplentes1 y divSuplentes2
        divSuplentes = []
        divSuplentes.extend(divSuplentes1)
        divSuplentes.extend(divSuplentes2)
        
        tamaño_divSuplentes = len(divSuplentes)+22
        self.output_textedit.append(f"Total de jugadores a scrapear: {tamaño_divSuplentes}")
        self.progress_bar.setRange(0, tamaño_divSuplentes)
        self.invocar_actualizacion(self.progress)
        
        self.driver.quit()

        indexTitulares=0
        while indexTitulares<=22:
            
            self.driver = webdriver.Chrome()

            # Maximizar la ventana del navegador
            self.driver.maximize_window()

            # Navega a la página web que deseas hacer scraping
            self.driver.get(url)

            # Espera a que se cargue la página
            self.driver.implicitly_wait(45)

            # Encuentra el botón de "Consentir" 
            button = self.driver.find_element(By.XPATH, '//button[@aria-label="Consentir"]')
            # Haz clic en el botón de "Consentir" 
            button.click()

            try:
                # Encuentra el botón de "Ask me later" 
                button = self.driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div[2]/button')
                # Haz clic en el botón de "Consentir" 
                button.click()
            except:
                pass

            time.sleep(45)
                        
            # Encuentra todos los elementos <a> con la clase 'sc-3937c22d-0 jrbLdB'
            divJugadores = self.driver.find_elements(By.XPATH, '//a[@class="sc-3937c22d-0 jrbLdB"]')
                
            numTitulares=len(divJugadores)
            self.output_textedit.append(f"{indexTitulares+1}/{numTitulares}")
            divJugadores[indexTitulares].click()
            time.sleep(5)
            self.obtener_informacion_jugador()
            
            indexTitulares+=1
            self.progress+=1
            self.invocar_actualizacion(self.progress)
            self.driver.quit()
        

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    sys.exit(app.exec())