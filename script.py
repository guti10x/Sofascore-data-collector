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
        #scrape_button.clicked.connect(self.iniciar_scrapear_thread)
        #scrape_button.clicked.connect(self.start_progress)

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

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = SimpleWindow()
    window.show()
    sys.exit(app.exec())