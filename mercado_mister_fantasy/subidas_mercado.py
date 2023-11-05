# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 12:51:14 2023

@author: alvar
"""

from selenium import webdriver
import time
import pandas as pd

driver = webdriver.Chrome('chromedriver.exe')
url = 'https://mister.mundodeportivo.com/new-onboarding/'

driver.get(url)
driver.maximize_window()
time.sleep(1)

boton = driver.find_element_by_id('didomi-notice-agree-button')

boton.click()
time.sleep(1)

boton_2 = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div[2]/button')
boton_2.click()
time.sleep(0.5)
boton_2.click()
time.sleep(0.5)
boton_2.click()
time.sleep(0.5)
boton_2.click()

# Localiza el elemento del input gmail

boton_3 = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/button[3]')
boton_3.click()

inputgmail = driver.find_element_by_xpath('//*[@id="email"]')
# Borra cualquier contenido existente en la caja de texto (opcional)
inputgmail.clear()

# Ingresa texto en la caja de texto
inputgmail.send_keys("m31_grupo6@outlook.com")

# Localiza el elemento del input gmail
inputpsw = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/form/div[2]/input')

# Borra cualquier contenido existente en la caja de texto (opcional)
inputpsw.clear()

# Ingresa texto en la caja de texto
inputpsw.send_keys("Chocoflakes2")

# Encuentra el botón de "sing con gmail" 
button = driver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/form/div[3]/button')
button.click()

time.sleep(2)

boton_4 = driver.find_element_by_xpath('/html/body/div[3]/header/div[2]/ul/li[5]/a')
boton_4.click()

time.sleep(2)

boton_evolucion_mercado = driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[1]/button[4]')
boton_evolucion_mercado.click()

time.sleep(2)

jugadores = driver.find_elements_by_xpath('//table[@class="thin-scrollbar"]/tbody/tr/td[3]/a')
subida = driver.find_elements_by_xpath('//table[@class="thin-scrollbar"]/tbody/tr/td[4]')
subida_en_porcentaje = driver.find_elements_by_xpath('//table[@class="thin-scrollbar"]/tbody/tr/td[5]')
valor = driver.find_elements_by_xpath('//table[@class="thin-scrollbar"]/tbody/tr/td[6]')

#creamos una lista vacía
datos = []

for i in range(len(subida)):
    temporary_data = {'Jugador': jugadores[i].text, 
                      'Subida': subida[i].text,
                      'Subida en porcentaje': subida_en_porcentaje[i].text,
                      'Valor': valor[i].text} 
    datos.append(temporary_data)

df_datos = pd.DataFrame(datos)
df_datos

#juntamos todo a un archivo excel
df_datos.to_excel('datos_subida_mercado.xlsx', index=False)