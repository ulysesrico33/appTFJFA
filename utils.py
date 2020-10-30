from selenium.webdriver.common.by import By
import cassandraSent as bd
import PyPDF2
import uuid
import base64
import time
import json
import os
import sys

download_dir='C:\\Users\\1098350515\\Downloads'

def appendInfoToFile(path,filename,strcontent):
    txtFile=open(path+filename,'a+')
    txtFile.write(strcontent)
    txtFile.close()


"""
processRows:

//*[@id="dtRresul_data"]/tr[1]/td[1]
//*[@id="dtRresul_data"]/tr[1]/td[2]
//*[@id="dtRresul_data"]/tr[1]/td[3]
...
//*[@id="dtRresul_data"]/tr[1]/td[5]
"""

def processRows(browser,row,strSearch):
    pdfDownloaded=False
    for col in range(1,6):
        if col==2:
            namePDF=browser.find_elements_by_xpath('//*[@id="dtRresul_data"]/tr['+str(row)+']/td['+str(col)+']')[0].text
        if col==3:
            dt_date=browser.find_elements_by_xpath('//*[@id="dtRresul_data"]/tr['+str(row)+']/td['+str(col)+']')[0].text
        if col==4:
            region=browser.find_elements_by_xpath('//*[@id="dtRresul_data"]/tr['+str(row)+']/td['+str(col)+']')[0].text
        if col==5:
            court=browser.find_elements_by_xpath('//*[@id="dtRresul_data"]/tr['+str(row)+']/td['+str(col)+']')[0].text                    

        if col==1:
            #This is the xpath of the link : //*[@id="grdSentencias_ctl00__'+str(row)+'"]/td['+str(col)+']/a
            #This find_element method works!
            pdfButton=browser.find_elements_by_xpath('//*[@id="dtRresul_data"]/tr['+str(row)+']/td['+str(col)+']')[0]
            pdfButton.click()
            time.sleep(20)
            #The file is downloaded rare, then just renaming it solves the issue
            for file in os.listdir(download_dir):
                os.rename(download_dir+'\\'+file,download_dir+'\\00000.pdf')

    
       
    #Build the json by row            
    with open('json_sentencia.json') as json_file:
        json_sentencia = json.load(json_file)

    json_sentencia['id']=str(uuid.uuid4())
    json_sentencia['court_room']=court
    json_sentencia['pdfname']=namePDF
    #Working with the date, this field will deliver:
    #1.Date field,2. StrField and 3.year
    # timestamp accepted for cassandra: 
    # yyyy-mm-dd  , yyyy-mm-dd HH:mm:ss
    #In web site, the date comes as 27-10-2020 14:38:00
    data=''
    data=dt_date.split(' ')
    dDate=str(data[0]).split('-')
    dDay=dDate[0]
    dMonth=dDate[1]
    dYear=dDate[2]
    dTime=data[1]
    fullTimeStamp=dYear+'-'+dMonth+'-'+dDay+' '+dTime;
    json_sentencia['year']=int(dYear)
    json_sentencia['region']=region
    json_sentencia['publication_datetime']=fullTimeStamp
    json_sentencia['strpublicationdatetime']=fullTimeStamp
    #Check if a pdf exists                       
    json_sentencia['lspdfcontent'].clear()
                  
    lsContent=[]  
    for file in os.listdir(download_dir):
        pdfDownloaded=True
        strFile=file.split('.')[1]
        if strFile=='PDF' or strFile=='pdf':
            lsContent=readPDF(file)        

    #When pdf is done and the record is in cassandra, delete all files in download folder
    #If the pdf is not downloaded but the window is open, save the data without pdf
    if pdfDownloaded==True:
        for file in os.listdir(download_dir):
            for item in lsContent:
                json_sentencia['lspdfcontent'].append(item)
            for file in os.listdir(download_dir):
                os.remove(download_dir+'\\'+file) 

    #Insert information to cassandra
    res=bd.cassandraBDProcess(json_sentencia)
    if res:
        print('Sentencia added:',str(namePDF))
    else:
        print('Keep going...sentencia existed:',str(namePDF)) 
                    
"""
readPDF is done to read a PDF no matter the content, can be image or UTF-8 text
"""
def readPDF(file):
    lsContent=[]
    with open(download_dir+'\\'+file, "rb") as imageFile:
        bContent = base64.b64encode(imageFile.read()).decode('utf-8')
    
    lsContent.append(bContent)
    return lsContent   
    
                  

def readPyPDF(file):
    #This procedure produces a b'blabla' string, it has UTF-8
    #PDF files are stored as bytes. Therefore to read or write a PDF file you need to use rb or wb.
    lsContent=[]
    pdfFileObj = open(download_dir+'\\'+file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pags=pdfReader.numPages
    for x in range(0,pags):
        pageObj = pdfReader.getPage(x)
        #UTF-8 is the right encodeing, I tried ascii and didn't work
        #1. bContent is the actual byte from pdf with utf-8, expected b'bla...'
        bcontent=base64.b64encode(pageObj.extractText().encode('utf-8'))
        lsContent.append(str(bcontent.decode('utf-8')))
                         
    pdfFileObj.close()    
    return lsContent

"""
This is the method to call when fetching the pdf enconded from cassandra which is a list of text
but that text is really bytes. This will decode any file, whether image or not.
"""
def decodeFromBase64toNormalTxt(b64content):
    normarlText=base64.b64decode(b64content).decode('utf-8')
    return normarlText


    
                               
                                         