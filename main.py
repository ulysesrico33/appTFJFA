from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert 
from selenium import webdriver
import utils as tool
import chromedriver_autoinstaller
import json
import time
import os
import requests 
import sys
import cassandraSent as bd


pathToHere=os.getcwd()

options = webdriver.ChromeOptions()

download_dir='C:\\Users\\1098350515\\Downloads'
profile = {"plugins.plugins_list": [{"enabled": True, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": download_dir , 
               "download.prompt_for_download": False,
               "download.directory_upgrade": True,
               "download.extensions_to_open": "applications/pdf",
               "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
               }
options.add_experimental_option("prefs", profile)
#Erase every file in download folder at the beginning to avoid mixed files
for file in os.listdir(download_dir):
    os.remove(download_dir+'\\'+file)

print('Download folder empty...')
chromedriver_autoinstaller.install()
browser=webdriver.Chrome(options=options)
#Since here both versions (heroku and desktop) are THE SAME
url="http://sentencias.tfjfa.gob.mx:8080/SICSEJLDOC/faces/content/public/consultasentencia.xhtml"
response= requests.get(url)
status= response.status_code
if status==200:  
    #Read the information of query and page 
    lsInfo=[]
    #1.Topic, 2. Page
    lsInfo=bd.getPageAndTopic()
    topic=str(lsInfo[0])
    page=str(lsInfo[1])
    startPage=int(page)
    
    browser.get(url)
    time.sleep(3)  
    #class names for li: rtsLI rtsLast
    btnBuscar=browser.find_elements_by_xpath("//*[@id='formBusqueda:btnBuscar']")[0].click()
    time.sleep(6)
    strSearch=" "
    txtBuscar=browser.find_elements(By.XPATH,"//*[@id='formBusqueda:textToSearch']")[0].send_keys(strSearch)
    btnBuscaTema=browser.find_elements(By.XPATH,'//*[@id="formBusqueda:btnBuscar"]')[0].click()
    #WAit X secs until query is loaded.
    time.sleep(10)
    print('Start reading the page...')
    #Control the page
    #Page identention
    while (startPage<=143):
        countRow=0
        for row in range(1,8):
            tool.processRows(browser,row,strSearch)
            countRow=countRow+1

        #Page control
        print('Count of Rows:',str(countRow)) 
        #Update the info in file
        print('Page already done:...',str(startPage))   
        control_page=int(startPage)+1
        startPage=control_page
        bd.updatePage(topic,control_page)
        #Change the page with next
        btnnext=browser.find_elements_by_xpath('//*[@id="dtRresul_paginator_top"]/span[4]')[0].click()
        time.sleep(5) 
        

browser.quit()
                           