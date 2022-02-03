# Utilizada para realizar peticiones HTTP.
import requests
# Utilizada para parsear el HTML tipo string recibido de las peticiones HTTP a formato HTML. Tambien facilita enormemente la extraccion de datos de ficheros HTML.
from bs4 import BeautifulSoup
import cv2
# Utilizada para parsear el diccionario que contiene la informacion del proceso consultado (Datos_Proceso) a un objeto JSON.
import sys
# Utilizada para el manejo de logs.
import logging
# Utilizada para implementar delays.
# import time
#Programa disenado para encontrar el texto dentro del string.
import MonoImgTxtv3

class TYBA_Service:
    
###########################################################################################################################################################################################
    def guardar_captcha(self, url_a_extraer, n_proceso, Modo_debug):  
        """Descarga el Captcha que aparece en la pagina web principal del TYBA en el fichero "Captcha.png".
        
        Retorna las cookies de sesion y las variables necesarias para la realizacion de futuras peticiones HTTP.
        
        Parametros:
        
        url_a_extraer -- URL de la pagina principal del TYBA.
        n_proceso     -- Numero de proceso que se quiere consultar.
        Modo_debug    -- Controla si el programa se ejecuta en modo debug o no.
        
        Notas:
        Recordar que si se trata descargar el captcha sin mantener sesion, el captcha descarga vacio.
        
        """
        
        try:

            # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
            # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.
            r = requests.get(url_a_extraer, verify = Modo_debug)
            
            # Convertir de string a html. 
            soup = BeautifulSoup(r.text, "html.parser") 
            
            # Se extraen los valores "_VIEWSTATE", "_VIEWSTATEGENERATOR", "_EVENTVALIDATION", los cuales son necesarios para realizar cualquier peticion HTTP a la pagina web.
            # Los valores de lista fueron obtenidos a prueba y error.
            _VIEWSTATE = soup.find_all("input")[0].get("value")
            _VIEWSTATEGENERATOR = soup.find_all("input")[1].get("value")
            _EVENTVALIDATION = soup.find_all("input")[3].get("value")
            
            #Extraer la URL de donde la pagina web carga el captcha.
            #Si el captcha cambiara, esta URL no existiria mas, por lo que generaria error. Entonces con ese error se puede detectar cuando la pagina web de la rama ha cambiado de tipo de captcha.
            url_captcha = "https://procesojudicial.ramajudicial.gov.co/Justicia21/Administracion/"+ soup.find_all("img")[1].get("src")[2:]
            
       
        except:
            
            # Si existe algun error, se ejecuta la funcion opcion_default.
            Mensaje_Error = 'Primer petición HTTP Get a la página web de la rama - Método: guardar_captcha()'
            raise NameError(Mensaje_Error)
        
        try:
            #Descarga el captcha. Tener cuidado de mantener la sesion de conexion obtenida de la primera URL a la URL donde esta el captcha.
            #Para ello se utilizan las cookies obtenidas con el primer get.
            # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
            # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.
            r2 = requests.get(url_captcha, cookies = r.cookies, verify = Modo_debug) 
    
        except:
            
            # Si existe algun error, se ejecuta la funcion opcion_default.
            Mensaje_Error = 'Intento de descarga de la imagen del captcha de la página web de la rama - Método: guardar_captcha()'
            raise NameError(Mensaje_Error)
            
        #Crear fichero. 'wb' especifica que el fichero se guardara en binario.                                                        
        Captcha = open('Captcha.png', 'wb')       
        
        #Escribe los datos binarios obtenidos del captcha y los guarda en binario en el finchero.      
        Captcha.write(r2.content)           
        
        #cierra la imagen.
        Captcha.close()      
                       
          
        return r.cookies, _VIEWSTATE , _VIEWSTATEGENERATOR, _EVENTVALIDATION
    
    ###########################################################################################################################################################################################                                    
    def obtener_captcha(self):  
        """Devuelve el string del captcha.  
        """
        #Abre el captcha guardado con cv2
        Captcha_original = cv2.imread("Captcha.png")  
        
        #Envia el captcha a la funcion MonoImgTxtv3 y devuelve el string del captcha.
        Captcha_string = MonoImgTxtv3.main(Captcha_original)                                        
        
        #Devuelve el string obtenido             
        return Captcha_string                   
    
    ###########################################################################################################################################################################################
    def obtener_variables(self, url_a_extraer, n_proceso, Modo_debug):
        
        """Descifra el Captcha y obtiene las cookies y valores necesarios para poder realizar futuras peticiones HTTP POST.
        
        Retorna el texto del Captcha, las cookies de sesion, y variables necesarias para realizar la peticion HTTP Post que simula dar click al boton "Consultar".
        
        Parametros:
        
        url_a_extraer -- URL de la pagina principal del TYBA.
        n_proceso     -- Numero de proceso que se quiere consultar.
        Modo_debug    -- Controla si el programa se ejecuta en modo debug o no.
        
        """
        while True: 
            # Bucle que termina cuando se ha obtenido un valor correcto de captcha. Puede terminar algunas veces con un captcha que posea un caracter incorrecto.  
            
            # Variable que permite que el bucle while se reinicie cuando se detecta un valor no alfanumerico dentro del resultado de traduccion del captcha
            repetir = False 
            
            # Metodo que descarga el captcha de la pagina web manteniendo sesion abierta
            rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION = self.guardar_captcha(url_a_extraer, n_proceso, Modo_debug)    
            
            # Devuelve el string del captcha
            Captcha_texto = self.obtener_captcha() 
                    
            # Si el string de la traduccion es mas largo que 8 esta mal, se rompe el bucle y se solicita a la pagina web un nuevo captcha
            if len(Captcha_texto) > 6:          
                print("Error. Captcha largo. Intentando de nuevo")
                continue
                     
            # Se comprueba caracter por caracter si es alphanumerico. Si no, se rompe el bucle for con continue, y el bucle while con "repetir"       
            for character in Captcha_texto:     
                if not character.isalpha() and not character.isdigit():
                    print("Error. Caracter en captcha no deseado. Intentando de nuevo")
                    repetir = True
                    continue
            #End for    
            
            # Si repetir se pone en True, el captcha fue mal traducido por lo que es necesario solicitar un nuevo captcha. Entonces se vuelve al principio
            if repetir == True:                 
                continue
            
            # Como en los captcha no hay ni "Z", "O" o "Q", y estos valores siempre son confundidos con "2", "0" y "9" respectivamente
            Captcha_texto = Captcha_texto.replace("Z", "2") 
            
            # Se decide reemplazar manualmente estos valores siempre.
            Captcha_texto = Captcha_texto.replace("O", "0") 
            
            # Se recomienda crear una funcion que este atenta a si un captcha erroneo es enviado, asi simplemente se solicita uno nuevo.
            Captcha_texto = Captcha_texto.replace("Q", "9") 
                
            break
        
        #End While
        return rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Captcha_texto
    
    ###########################################################################################################################################################################################
    def Click_Consultar(self, n_proceso, url_a_extraer, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Captcha_texto, Modo_debug):
        """Hace una peticion HTTP POST al sitio web simulando dar click al boton "Consultar".
        
        Parametros:
        
        n_proceso                 -- Numero de proceso que se quiere consultar.
        url_a_extraer             -- URL de la pagina principal del TYBA.
        rcookies                  -- Cookies de sesion.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        Captcha_texto             -- String extraido del Captcha.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna el resultado y el mensaje anexo obtenido de la pagina web luego de dar click en el boton "Consultar", y variables necesarias para realizar la peticion HTTP Post
        con el que se simula dar click al primer boton de lupa.
        """
       
        # Se crea el campo de datos de la peticion HTTP POST que simula dar click al boton consultar. Se han recortado los campos innecesarios con el fin de reducir la cantidad de datos enviados al
        # servidor de la pagina web de la rama. Recordar que anteriormente la consulta fue copiada tal cual como un browser Google Chrome haria la peticion HTTP Post. 
        query_consultar = {
    
                 '__VIEWSTATE' : _VIEWSTATE,
                 '__VIEWSTATEGENERATOR' : _VIEWSTATEGENERATOR,
                 '__EVENTVALIDATION' : _EVENTVALIDATION,
                  'ctl00$MainContent$txtCodigoProceso' : n_proceso,
                 'ctl00$MainContent$txtCaptchaText' : Captcha_texto ,
                 'ctl00$MainContent$ctl12' : 'Consultar'
                 }
        try: 
            # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
            # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.
            r3 = requests.post(url_a_extraer, data = query_consultar, cookies = rcookies, verify = Modo_debug) 
            
            # Recordar que luego de dar al boton consultar, la vista de pagina web cambia. Por lo que es necesario extraer nuevamente los valores "VIEWSTATE", "VIEWSTATEGENERATOR", "EVENTVALIDATION"
            
            soup = BeautifulSoup(r3.text, "html.parser") # Convertir de string a html
            
            _VIEWSTATE = soup.find_all("input")[0].get("value")
            _VIEWSTATEGENERATOR = soup.find_all("input")[1].get("value")
            _EVENTVALIDATION = soup.find_all("input")[3].get("value")
        
            Resultado = soup.find_all("span", id="MainContent_UC_MensajeInformativo_lblTitulo")[0].text    
            
            Mensaje = soup.find_all("span", id="MainContent_UC_MensajeInformativo_lblMensajes")[0].text
            
        except:
            # Si existe algun error, se ejecuta la funcion opcion_default.
            Mensaje_Error = 'Respuesta despues de dar click en el boton consultar - Metodo: Click_Consultar()'
            raise NameError(Mensaje_Error)
    
        return Resultado, Mensaje, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION
    
    ###########################################################################################################################################################################################
    def Click_Lupa(self, n_proceso, url_a_extraer, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Modo_debug):
        """Hace una peticion HTTP POST al sitio web simulando dar click al primer boton de Lupa.
        
        Parametros:
        
        n_proceso                 -- Numero de proceso que se quiere consultar.
        url_a_extraer             -- URL de la pagina principal del TYBA.
        rcookies                  -- Cookies de sesion.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna el HTML que contiene toda la informacion de la pagina web secundaria de la rama, y las variables necesarias para realizar la peticion HTTP Post para simular 
        dar click al primer boton de lupa.
        
        """
        
        # Se crea el campo de datos de la peticion HTTP POST que simula darle click al primer bonton de Lupa. Se han recortado los campos innecesarios con el fin de reducir la cantidad de datos enviados al
        # servidor de la pagina web de la rama. Recordar que anteriormente la consulta fue copiada tal cual como un browser Google Chrome haria la peticion HTTP Post. 
    
        query_Lupa = {
             'ctl00$ctl09': 'ctl00$MainContent$UpdatePanel_BaseGrilla|ctl00$MainContent$grdProceso$ctl02$imgbConsultarGrilla',
             '__VIEWSTATE' : _VIEWSTATE,                   
             '__VIEWSTATEGENERATOR' : _VIEWSTATEGENERATOR,
             '__EVENTVALIDATION' : _EVENTVALIDATION,
             'ctl00$MainContent$txtCodigoProceso' : n_proceso,
             ' __ASYNCPOST' : True,
             'ctl00$MainContent$grdProceso$ctl02$imgbConsultarGrilla.x' : '25',   #Coordenada x donde se da click del boton
             'ctl00$MainContent$grdProceso$ctl02$imgbConsultarGrilla.y' : '27'    #Coordenada y donde se da click del boton
             }
        
        try:
            # Esta consulta Hace un POST que simula darle click al primer boton de lupa y retorna la informacion general del proceso.
            # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
            # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.
            r4 = requests.post(url_a_extraer, data = query_Lupa, cookies = rcookies, verify = Modo_debug) #las cookies se mantienen
            
            soup = BeautifulSoup(r4.text, "html.parser") #Convertir de string a html
            _VIEWSTATE = soup.find_all("input")[0].get("value")
            _VIEWSTATEGENERATOR = soup.find_all("input")[1].get("value")
            _EVENTVALIDATION = soup.find_all("input")[3].get("value")
        
        except:
            # Si existe algun error, se ejecuta la funcion opcion_default.
            Mensaje_Error = 'Respuesta a dar click en el primer boton de Lupa - Metodo: Click_Lupa()'
            raise NameError(Mensaje_Error)
        
        return soup, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION 
    
    ###########################################################################################################################################################################################
    def Crear_Dict_P_1(self, soup, url_a_extraer, url_2, n_proceso):  
        """Extrae la informacion general del proceso y sujetos.
        
        Parametros:
        
        soup                      -- HTML obtenido como resultado de dar click en el primer boton de Lupa.
        url_a_extraer             -- URL de la pagina principal del TYBA.
        url_2                     -- URL de la segunda pagina del TYBA.
        n_proceso                 -- Numero de proceso que se quiere consultar.
        
        Retorna un diccionario ordenado con la informacion general del proceso y la informacion de sujetos.
        """
         
        # Se inicializa un diccionario ordenado que contendra la informacion general del proceso y la informacion de sujetos.
        Datos_Proceso = {}
        
        # Extraer Despacho. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Despacho'] = soup.find_all("div", class_= "col-md-4")[10].input["value"]
        except KeyError:
            Datos_Proceso['Despacho'] = ""
            
        # Extraer Corporacion. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Corporacion'] = soup.find_all("div", class_= "col-md-4")[6].input["value"]
        except KeyError:
            Datos_Proceso['Corporacion'] = ""
        
        # Extraer Ciudad. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Ciudad'] = soup.find_all("div", class_= "col-md-4")[5].input["value"]
        except KeyError:
            Datos_Proceso['Ciudad'] = ""
            
        # Extraer Clase Proceso. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['ClaseProceso'] = soup.find_all("div", class_= "col-md-4")[2].input["value"]
        except KeyError:
            Datos_Proceso['ClaseProceso'] = ""
            
        # Extraer Correo Electronico Externo. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['CorreoElectronicoExterno'] = soup.find_all("div", class_= "col-md-4")[14].input["value"]
        except KeyError:
            Datos_Proceso['CorreoElectronicoExterno'] = ""
            
        # Extraer Departamento. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Departamento'] = soup.find_all("div", class_= "col-md-4")[4].input["value"]
        except KeyError:
            Datos_Proceso['Departamento'] = ""
        
        # Extraer Direccion. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Direccion'] = soup.find_all("div", class_= "col-md-4")[11].input["value"]
        except KeyError:
            Datos_Proceso['Direccion'] = ""
            
        # Extraer Distrito_Circuito. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Distrito'] = soup.find_all("div", class_= "col-md-4")[8].input["value"]
        except KeyError:
            Datos_Proceso['Distrito'] = ""
        
        # Extraer Especialidad. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Especialidad'] = soup.find_all("div", class_= "col-md-4")[7].input["value"]
        except KeyError:
            Datos_Proceso['Especialidad'] = ""
            
        # Extraer Fecha Finalizacion. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['FechaFinalizacion'] = soup.find_all("div", class_= "col-md-4")[17].input["value"]
        except KeyError:
            Datos_Proceso['FechaFinalizacion'] = ""
        
        # Extraer Fecha Providencia. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['FechaProvidencia'] = soup.find_all("div", class_= "col-md-4")[16].input["value"]
        except KeyError:
            Datos_Proceso['FechaProvidencia'] = ""
        
        # Extraer Fecha Publicacion. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['FechaPublicacion'] = soup.find_all("div", class_= "col-md-4")[15].input["value"]
        except KeyError:
            Datos_Proceso['FechaPublicacion'] = ""
        
        # Extraer Numero_Despacho. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['NumeroDespacho'] = soup.find_all("div", class_= "col-md-4")[9].input["value"]
        except KeyError:
            Datos_Proceso['NumeroDespacho'] = ""
        
        # Extraer Observaciones. Si esta vacio, se guarda "". Ademas se reemplazan los valores '\r\n' por "".
        try:
            Datos_Proceso['Observaciones'] = soup.find_all("div", class_= "col-md-4")[19].textarea.text
            Datos_Proceso['Observaciones'] = Datos_Proceso['Observaciones'].replace('\r\n', '')
        except KeyError:
            Datos_Proceso['Observaciones'] = ""
        
        # Extraer Subclase Proceso. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['SubClaseProceso'] = soup.find_all("div", class_= "col-md-4")[3].input["value"]
        except KeyError:
            Datos_Proceso['SubClaseProceso'] = ""
        
        # Extraer Telefono. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['Telefono'] = soup.find_all("div", class_= "col-md-4")[12].input["value"]
        except KeyError:
            Datos_Proceso['Telefono'] = ""
            
        # Extraer Tipo_Decision. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['TipoDecision'] = soup.find_all("div", class_= "col-md-4")[18].input["value"]
        except KeyError:
            Datos_Proceso['TipoDecision'] = ""
            
        # Extraer Tipo Proceso. Si esta vacio, se guarda "".
        try:
            Datos_Proceso['TipoProceso'] = soup.find_all("div", class_= "col-md-4")[1].input["value"]
        except KeyError:
            Datos_Proceso['TipoProceso'] = ""
             
        # Se inicializa una lista temporal para Sujetos
        Sujetos = []
        
        # Se inicializa un diccionario ordenado temporal que almacenara la informacion sobre los sujetos. Es necesario este diccionario para poder controlar el orden dentro de las listas
        # que se guardaran dentro del JSON definitivo.
        Sujetos_ordenado = {}
        
        # Se extrae la tabla de Sujetos
        tabla_sujetos = soup.find_all("table", class_="table table-striped table-bordered table-hover")[0]
        
        # Se inicializa la variable que contendra el total de filas de la tabla Sujetos.
        total_Sujetos = 0
        
        # Cada iteracion representa una fila de la tabla.
        for fila in tabla_sujetos.find_all("tr"):
            total_Sujetos += 1
        #End for
        
        # Debido a que el bucle cuenta la cabecera de la tabla, es necesario descontarla del total de Sujetos.
        total_Sujetos -= 1
        
        # Se inicia la variable que ayudara con la serie matematica que da resultado al numero de lista para poder extraer informacion de Sujetos.
        localizador = 0
    
        # Cada iteracion representa una fila.
        for x in range(1, total_Sujetos + 1):
                
                # Cada valor td es una casilla de la fila.           
                # Al tratarse de un diccionario ordenado, la asignacion de variables debe hacerse de la forma larga como se muestra a continuacion.
                Sujetos_ordenado['TipoSujeto'] = soup.find_all('td')[x - 1 + localizador].text
                Sujetos_ordenado['EsEmplazado'] = soup.find_all('td')[x + localizador].text
                Sujetos_ordenado['TipoDocumento'] = soup.find_all('td')[x + 3 + localizador].text
                Sujetos_ordenado['NumeroIdentificacion'] = soup.find_all('td')[x + 4 + localizador].text
                Sujetos_ordenado['NombreApellidosORazonSocial'] = soup.find_all('td')[x + 5 + localizador].text
                Sujetos_ordenado['FechaRegistro'] = soup.find_all('td')[x + 6 + localizador].text
                
                #Se agrega el diccionario ordenado a la lista.
                Sujetos.append(Sujetos_ordenado)                    
    
                # Por razones operativas del programa, se debe reiniciar a 0 el diccionario ordenado.
                Sujetos_ordenado = {}
    
                # Se suma +7 ya que fue el numero identificado para la serie matematica.
                localizador += 7
        #End for
    
        #Se almacena el diccionario ordenado "Sujetos" en el TAG "Sujetos" del diccionario ordenado Datos_Proceso.
        Datos_Proceso['Sujetos'] = Sujetos
          
        return Datos_Proceso
    
    ###########################################################################################################################################################################################
    
    def Click_Siguiente_Pagina(self, n_proceso, Datos_Proceso, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, url_2, rcookies, Modo_debug):   
        """Simula dar click en el boton de siguiente, retorna el html que responde la pagina web con las actuaciones de la siguiente pagina.
        
        Parametros:
           
        n_proceso                 -- Numero de proceso que se quiere consultar.
        Datos_Proceso             -- Diccionario ordenado que contiene la informacion general del proceso y los sujetos.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        url_2                     -- URL de la segunda pagina del TYBA.
        rcookies                  -- Cookies de sesion.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna el HTML con la informacion de la pagina nueva y las variables necesarias para simular un nuevo click en el boton siguiente pagina.
        
        Nota: recordar que es necesario extraer los valores "_VIEWSTATE", "_VIEWSTATEGENERATOR", "_EVENTVALIDATION", los cuales son necesarios para solicitar futuras siguientes paginas.
        """
    
        # Se crea el campo de datos de la peticion HTTP POST que simula dar click al boton Lupa que aparece al lado de cada actuacion. Se han recortado los campos innecesarios con 
        # el fin de reducir la cantidad de datos enviados al servidor de la pagina web de la rama. Recordar que anteriormente la consulta fue copiada tal cual como un browser Google 
        # Chrome haria la peticion HTTP Post.
        query_next_page = {
                            
                              'ctl00$ctl09' : 'ctl00$MainContent$UpdatePanel_Actuaciones|ctl00$MainContent$btnSiguienteGrillaActuaciones',
                              'ctl00$MainContent$txtCodigoProceso' : n_proceso,
                              '__VIEWSTATE' : _VIEWSTATE,
                              '__VIEWSTATEGENERATOR' : _VIEWSTATEGENERATOR,
                              '__EVENTVALIDATION' : _EVENTVALIDATION,
                              '__ASYNCPOST' : True,
                              'ctl00$MainContent$btnSiguienteGrillaActuaciones.x' : '20',
                              'ctl00$MainContent$btnSiguienteGrillaActuaciones.y' : '13'
                               }
        
        # Las cookies se mantienen.
        # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
        # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.    
        r5 = requests.post(url_2, data = query_next_page, cookies = rcookies, verify = Modo_debug) 
        
        # Convertir de string a html.
        soup = BeautifulSoup(r5.text, "html.parser")  
        _VIEWSTATE = soup.find_all("input")[0].get("value")
        _VIEWSTATEGENERATOR = soup.find_all("input")[1].get("value")
        _EVENTVALIDATION = soup.find_all("input")[3].get("value")
        
        return soup, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION 
    
    ###########################################################################################################################################################################################
    def Calcular_paginas(self, soup, n_proceso, Datos_Proceso, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, url_2, rcookies, Modo_debug):
        """Calcula el numero de paginas y cantidad total de actuaciones de forma independiente a los valores enviados por la pagina web.
        
        Parametros:
        
        soup                      -- HTML obtenido como resultado de dar click en el primer boton de Lupa.    
        n_proceso                 -- Numero de proceso que se quiere consultar.
        Datos_Proceso             -- Diccionario ordenado que contiene la informacion general del proceso y los sujetos.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        url_2                     -- URL de la segunda pagina del TYBA.
        rcookies                  -- Cookies de sesion.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna el total de actuaciones contadas y la cantidad de paginas en las que se registran las actuaciones.
        
        NOTA: Pagina anterior se considera a aquella pagina que se tenia antes de dar click en el boton "Siguiente pagina".
        Pagina actual se considera a aquella pagina que se obtiene luego de dar click en el boton "Siguiente pagina".
        Es importante guardar los datos de las variables "_VIEWSTATE", "_VIEWSTATEGENERATOR", "_EVENTVALIDATION", ya que ellas le comunican a la pagina web lo que se esta visualizando
        antes de dar click en cualquier boton. 
        
        """
    
        # Se inicializa variable que contendra la cantidad total de paginas. Se inicializa a 1.
        Total_paginas = 1
        
        # Se inicializan variables que contendran la informacion del primer registro de la pagina actual consultada.
        Ciclo_Actual = None
        Tipo_Actuacion_Actual = None
        Fecha_Actuacion_Actual = None
        Fecha_registro_Actual = None
        
        # Se inicializa la variable temporal que ira almacenando el total de actuaciones contadas por pagina. El valor cambiara cada iteracion del bucle while.
        total_actuaciones_pagina_Actual = 0
        
        
        
        # Esto se hace porque hay procesos que no tienen actuaciones. La primera tabla es sujetos. Se evalúa la segunda. Si no existe segunda tabla, el proceso no tiene actuaciones.
        try:

            tabla_Anterior = soup.find("table", {"id": "MainContent_grdActuaciones"})
            if tabla_Anterior == None:
                #Si tabla_Anterior es None, significa que el proceso no tiene tabla de actuaciones, por lo que se retorna indicando el caso con un 0, 0
                return 0, 0

        except:
            return 0, 0
                       
        # Bucle infinito que termina cuando ya se tengan el numero total de paginas y actuaciones.
        while True:
    
            #Si es la primera pagina, se toma el soup que entra en el metodo, que fue recibido luego de dar click al primer boton de Lupa.
            #Si el total de paginas cambio, significa que la pagina Anterior ya no es la pagina 1. Entonces la pagina actual pasa a ser pagina anterior.
            #Los valores de "total_actuaciones_pagina_Anterior" se pasan a la variable "Total_actuaciones".
            if Total_paginas == 1:
                
                try:
                    #Se extrae la tabla de actuaciones del soup obtenido despues de haber dado click al primer boton de lupa.
                    tabla_Anterior = soup.find("table", {"id": "MainContent_grdActuaciones"})
                    if tabla_Anterior == None:
                        #Si tabla_Anterior es None, significa que el proceso no tiene tabla de actuaciones, por lo que se retorna indicando el caso con un 0, 0
                        return 0, 0
                except:
                    return 0, 0
                    
                #Se inicializa la variable temporal que contendra el valor total de actuaciones de la pagina 1 y se actualizara conforme se vaya cambiando de paginas. 
                total_actuaciones_pagina_Anterior = 0
                
                #Cada iteracion representa una fila de la tabla             
                for fila in tabla_Anterior.find_all("tr"):
                    
                    #Cada fila representa una actuacion. Se suma +1 a "total_actuaciones_pagina_Anterior" por cada iteracion.
                    total_actuaciones_pagina_Anterior += 1   
                
                #End for
                
                #Debido a que el bucle cuenta la cabecera de la tabla, es necesario descontarla del total de actuaciones de pagina anterior.   
                total_actuaciones_pagina_Anterior -= 1
                
                #Se extrae la informacion del primer registro de la primera pagina que se empieza a considerar como pagina anterior.
                Ciclo_Anterior = tabla_Anterior.find_all("tr")[1].find_all("td")[1].text
                Tipo_Actuacion_Anterior = tabla_Anterior.find_all("tr")[1].find_all("td")[2].text
                Fecha_Actuacion_Anterior = tabla_Anterior.find_all("tr")[1].find_all("td")[3].text
                Fecha_registro_Anterior = tabla_Anterior.find_all("tr")[1].find_all("td")[4].text
                
                #El total de actuaciones de pagina anterior se acumulan en la variable del total de actuaciones.
                Total_actuaciones = total_actuaciones_pagina_Anterior
            
            else:
                
                #Los datos de la pagina actual de la iteracion anterior pasan a ser los datos de pagina anterior.
                Ciclo_Anterior = Ciclo_Actual
                Tipo_Actuacion_Anterior = Tipo_Actuacion_Actual
                Fecha_Actuacion_Anterior = Fecha_Actuacion_Actual
                Fecha_registro_Anterior = Fecha_registro_Actual
                total_actuaciones_pagina_Anterior = total_actuaciones_pagina_Actual
                Total_actuaciones += total_actuaciones_pagina_Actual
            
            # Si el numero de actuaciones de pagina anterior es igual a 10, puede existir una pagina siguiente. Entonces se corrobora.
            # Si el numero de actuaciones de pagina anterior es menor a 10, no hay paginas siguientes por lo que ya se puede finalizar la ejecucion del metodo.    
            if total_actuaciones_pagina_Anterior == 10:
                
                # Se solicita siguiente pagina. Recordar que es necesario extraer los valores "_VIEWSTATE", "_VIEWSTATEGENERATOR", "_EVENTVALIDATION",
                # los cuales son necesarios para solicitar futuras siguientes paginas.
                soup_Actual, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION  = self.Click_Siguiente_Pagina(n_proceso,Datos_Proceso,_VIEWSTATE,_VIEWSTATEGENERATOR,_EVENTVALIDATION, url_2, rcookies, Modo_debug)
                
                #Se extrae la tabla de actuaciones de la pagina actual.
                tabla_Actual = soup_Actual.find("table", {"id": "MainContent_grdActuaciones"})
                
                # Se extraen los datos de la primera actuacion de la pagina actual.
                Ciclo_Actual = tabla_Actual.find_all("tr")[1].find_all("td")[1].text
                Tipo_Actuacion_Actual = tabla_Actual.find_all("tr")[1].find_all("td")[2].text
                Fecha_Actuacion_Actual = tabla_Actual.find_all("tr")[1].find_all("td")[3].text
                Fecha_registro_Actual = tabla_Actual.find_all("tr")[1].find_all("td")[4].text
    
                #Se compara la informacion de la primera actuacion de la pagina anterior y la pagina actual.
                #Si la primera actuacion de la pagina anterior es igual a la de la pagina actual, pagina anterior y actual son la misma y se puede terminar la ejecucion del metodo.
                #Si ambas actuaciones son diferentes, significa que pagina actual existe, por lo que se hace el conteo de actuaciones.
                if Ciclo_Actual == Ciclo_Anterior and Tipo_Actuacion_Actual == Tipo_Actuacion_Anterior and Fecha_Actuacion_Actual == Fecha_Actuacion_Anterior and Fecha_registro_Actual == Fecha_registro_Anterior:
                    
                    # Finaliza la funcion, retornando los valores de total de paginas y total de actuaciones.
                    return Total_paginas, Total_actuaciones
                
                else:
                    
                    # Se inicializa el contador que contendra el total de actuaciones de la pagina actual.
                    total_actuaciones_pagina_Actual = 0
                    
                    # Cada iteracion representa una fila de la tabla   
                    for fila in tabla_Actual.find_all("tr"):
                        
                        #Cada fila representa una actuacion. Se suma +1 a "total_actuaciones_pagina_Anterior" por cada iteracion.
                        total_actuaciones_pagina_Actual += 1 
                    
                    #End for
                    
                    # Debido a que el bucle cuenta la cabecera de la tabla, es necesario descontarla del total de actuaciones de pagina actual.
                    total_actuaciones_pagina_Actual -= 1
                    
                    # Como se determino que la pagina actual existe, entonces se suma al total de paginas.
                    Total_paginas += 1
                    
                    # Si el total de actuaciones de la pagina actual es menor a 10, no existe una pagina siguiente.
                    # Entonces se puede finalizar la funcion retornando el valor de paginas totales, y el valor total de actuaciones sumando las actuaciones de pagina actual.
                    # Si el total de actuaciones de la pagina actual es 10, puede existir una siguiente pagina, por lo que se deja reiniciar el bucle "while".
                    if total_actuaciones_pagina_Actual < 10:
                        
                        # Se finaliza la funcion retornando el valor de paginas totales, y el valor total de actuaciones sumando las actuaciones de pagina actual.
                        return Total_paginas, Total_actuaciones + total_actuaciones_pagina_Actual
                    
            else:
                
                # Si el numero de actuaciones de pagina anterior es menor a 10, no hay paginas siguientes por lo que ya se puede finalizar la ejecucion del metodo. 
                return Total_paginas , Total_actuaciones

    ###########################################################################################################################################################################################
    def Obtener_Informacion(self, boton, n_proceso, Datos_Proceso, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, url_2, rcookies, Modo_debug):
        """Retorna una lista con los datos de todas las actuacion obtenidos luego de dar click lupa por lupa.
        
        Parametros:
        
        boton                     -- Contiene el numero identificador del boton de lupa al que se dara click.   
        n_proceso                 -- Numero de proceso que se quiere consultar.
        Datos_Proceso             -- Diccionario ordenado que contiene la informacion general del proceso y los sujetos.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        url_2                     -- URL de la segunda pagina del TYBA.
        rcookies                  -- Cookies de sesion.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna un diccionario ordenado con los datos de todas las actuacion obtenidos luego de dar click lupa por lupa.
        
        """
        # Se convierte la variable boton a formato string "00".
        if boton < 10:
            boton = '0' + str(boton)
        else:
            boton = str(boton)
       
        # Se debe recordar que se empieza por el boton 02.
        # Se crea el campo de datos de la peticion HTTP POST que simula dar click al boton Lupa que aparece al lado de cada actuacion. Se han recortado los campos innecesarios con 
        # el fin de reducir la cantidad de datos enviados al servidor de la pagina web de la rama. Recordar que anteriormente la consulta fue copiada tal cual como un browser Google 
        # Chrome haria la peticion HTTP Post. 
        query_lupa = {
                            
                     'ctl00$ctl09':'ctl00$MainContent$UpdatePanel_Actuaciones|ctl00$MainContent$grdActuaciones$ctl'+boton+'$imgbConsultarGrilla',
                     'ctl00$MainContent$txtCodigoProceso' : n_proceso,                      
                     '__VIEWSTATE' : _VIEWSTATE,
                     '__VIEWSTATEGENERATOR' : _VIEWSTATEGENERATOR,
                     '__EVENTVALIDATION' : _EVENTVALIDATION,
                     '__ASYNCPOST' : True,
                     'ctl00$MainContent$grdActuaciones$ctl'+boton+'$imgbConsultarGrilla.x' : '28',
                     'ctl00$MainContent$grdActuaciones$ctl'+boton+'$imgbConsultarGrilla.y' : '22'
                     }
        # Las cookies se mantienen.
        # Obtener el html de la pagina web. Si "verify" es "True", python verificara los certificados, pero no permitira el uso de la herramienta "Fiddler" para el analisis de trafico HTTPS.
        # Si "verify" es "False", python no verificara certificados, permitiendo el uso de "Fiddler", sin embargo representa un problema de seguridad.
        r6 = requests.post(url_2, data = query_lupa, cookies = rcookies, verify = Modo_debug)

        #print(r6.status_code)

        # Verificar si es un caso de error 500 ('Internal Server Error') de la pagina. Fallo temporal del servidor de rama y que impide mostrar detalle de la actuacion
        if r6.status_code == 500:

            #Mensaje = 'Se detecta status_code 500 Internal Server Error al intentar ingresar a la lupa de detalle de la actuacion - Metodo: Obtener_Informacion()'
            #print(Mensaje)

            Informacion_Actuacion = {}

            # Existen varios tipos de estructura de actuacion, por lo tanto, se crea el tipo 500 para los casos en los
            # que la pagina regresa un error y no puede mostrar el detalle de la actuacion de tal manera que sirva
            # como condicion para recolectar la informacion de la actuacion directamente desde la tabla de actuaciones
            # principal
            Informacion_Actuacion['Tipo'] = '500'

        else:

            #Mensaje = 'No se detecta status_code 500 Internal Server Error al intentar ingresar a la lupa de detalle de la actuacion - Metodo: Obtener_Informacion()'
            #print(Mensaje)
        
            # Convertir de string a html.
            soup = BeautifulSoup(r6.text, "html.parser")

            #Se cuenta el valor total de campos y se restan 20 que son los campos que vienen al incio de la informacion del proceso.
            Total_campos = len(soup.find_all("div", class_= "col-md-4"))-20

            # Se inicializa el diccionario temporal que contendra los detalles de las actuaciones.
            Informacion_Actuacion = {}

            # Extraer Fecha Registro dentro de Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['FechaRegistro'] = soup.find("input", {"id": "MainContent_txtFechaRegistro"})["value"]
            except:
                Informacion_Actuacion ['FechaRegistro'] = ""

            # Extraer Estado Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['EstadoActuacion'] = soup.find("input", {"id": "MainContent_txtEstadoActuacion"})["value"]
            except:
                Informacion_Actuacion ['Estado_Actuacion'] = ""

            # Extraer Ciclo dentro de Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['Ciclo'] = soup.find("input", {"id": "MainContent_txtCiclo"})["value"]
            except:
                Informacion_Actuacion ['Ciclo'] = ""

            # Extraer Tipo Actuacion dentro de Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['TipoActuacion'] = soup.find("input", {"id": "MainContent_txtTipoActuacion"})["value"]
            except:
                Informacion_Actuacion ['TipoActuacion'] = ""

            # Extraer Etapa Procesal Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['EtapaProcesal'] = soup.find("input", {"id": "MainContent_txtEtapaProcesal"})["value"]
            except:
                Informacion_Actuacion ['EtapaProcesal'] = ""

            # Extraer Fecha Actuacion dentro de Actuacion. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['FechaActuacion'] = soup.find("input", {"id": "MainContent_txtFechaActuacion"})["value"]
            except:
                Informacion_Actuacion ['FechaActuacion'] = ""

            # Extraer Anotacion Actuacion. Si esta vacio, se guarda "". CUIDADO: los valores pueden traer "\n" al comienzo. Cuidado, el id se llama DescripcionActuacion en lugar de Anotacion.
            try:
                Informacion_Actuacion ['Anotacion'] = soup.find("textarea", {"id": "MainContent_txtDescripcionActuacion"}).text.replace('\r\n', '')
            except:
                Informacion_Actuacion ['Anotacion'] = ""

            # Extraer Nombre del Archivo. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['NombreArchivo'] = soup.find("table", {"id": "MainContent_grdArchivosActuaciones"}).find_all("td")[1].text
            except:
                Informacion_Actuacion ['NombreArchivo'] = ""

            # Extraer Termino Actuacion. Si esta vacio, se guarda "". Algunas actuaciones pueden no tener todos los campos, por lo que aparece un IndexError.
            try:
                Informacion_Actuacion ['Termino'] = soup.find("input", {"id": "MainContent_txtTermino"})["value"]
            except:
                Informacion_Actuacion ['Termino'] = ""

            # Extraer Calendario Actuacion. Si esta vacio, se guarda "". Algunas actuaciones pueden no tener todos los campos, por lo que aparece un IndexError.
            try:
                Informacion_Actuacion ['Calendario'] = soup.find("input", {"id": "MainContent_txtCalendario"})["value"]
            except:
                Informacion_Actuacion ['Calendario'] = ""

            # Extraer Dias Termino Actuacion. Si esta vacio, se guarda "". Algunas actuaciones pueden no tener todos los campos, por lo que aparece un IndexError.
            try:
                Informacion_Actuacion ['DiasDelTermino'] = soup.find("input", {"id": "MainContent_txtDiasTermino"})["value"]
            except:
                Informacion_Actuacion ['DiasDelTermino'] = ""

            # Extraer Fecha Inicio Termino Actuacion. Si esta vacio, se guarda "". Algunas actuaciones pueden no tener todos los campos, por lo que aparece un Error.
            try:
                Informacion_Actuacion ['FechaInicioTermino'] = soup.find("input", {"id": "MainContent_txtFechaInicioTermino"})["value"]
            except:
                Informacion_Actuacion ['FechaInicioTermino'] = ""

            # Extraer Fecha Fin Termino Actuacion. Si esta vacio, se guarda "". Algunas actuaciones pueden no tener todos los campos, por lo que aparece un Error.
            try:
                Informacion_Actuacion ['FechaFinTermino'] = soup.find("input", {"id": "MainContent_txtFechaFinTermino"})["value"]
            except:
                Informacion_Actuacion ['FechaFinTermino'] = ""

            # Extraer Providencia. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['Providencia'] = soup.find("input", {"id": "MainContent_txtProvidencia"})["value"]
            except:
                Informacion_Actuacion ['Providencia'] = ""

            # Extraer Tipo Decision. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['TipoDecision'] = soup.find("input", {"id": "MainContent_txtNombreTipoDecision"})["value"]
            except:
                Informacion_Actuacion ['TipoDecision'] = ""

            # Extraer Numero Providencia. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['NumeroProvidencia'] = soup.find("input", {"id": "MainContent_txtNumeroProvidencia"})["value"]
            except:
                Informacion_Actuacion ['NumeroProvidencia'] = ""

            # Extraer Fecha Ejecutoria. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['FechaEjecutoria'] = soup.find("input", {"id": "MainContent_txtFechaProvidenciaAct"})["value"]
            except:
                Informacion_Actuacion ['FechaEjecutoria'] = ""

            # Extraer Numero de Dias. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['NumeroDeDias'] = soup.find("input", {"id": "MainContent_txtNumeroDias"})["value"]
            except:
                Informacion_Actuacion ['NumeroDeDias'] = ""

            # Extraer Enfoque Diferencial. Si esta vacio, se guarda "".
            try:
                Informacion_Actuacion ['EnfoqueDiferencial'] = soup.find("input", {"id": "MainContent_txtEnfoqueDiferencial"})["value"]
            except:
                Informacion_Actuacion ['EnfoqueDiferencial'] = ""

            try:
                Informacion_Actuacion ['DescripcionAnulacion'] = soup.find("textarea", {"id": "MainContent_txtDescripcionAnulacionActuacion"}).text.replace('\r\n', '')
            except:
                Informacion_Actuacion ['DescripcionAnulacion'] = ""

            # Se encontraron tres tipos de estructura de actuacion. Tipo 0 con 7 campos, Tipo 1 con 13 campos, y Tipo 2 con 12 campos. Tipo 0 y Tipo 2 pueden agruparse en un solo elif.
            # Si se detecta un Tipo con diferente numero de campos, se ejecuta la funcion opcion_default() que generara alerta critica y dentendra la ejecuccion del programa.
            #De aquí para abajo es código a mejorar, sin embargo no ha podido ser mejorado porque no se ha encontrado actuaciones con las que se puedan obtener los ids y se pueda testear.
            if Total_campos == 7:
                Informacion_Actuacion['Tipo'] = '0'

            elif Total_campos in (13,14,20):

                Informacion_Actuacion['Tipo'] = '1'

                if Total_campos == 14:
                    Informacion_Actuacion['Tipo'] = '3'
                    # Extraer ValorCondenaEnPesos. Si esta vacio, se guarda "".
                    try:
                        Informacion_Actuacion ['ValorCondenaEnPesos'] = soup.find_all("div", class_= "col-md-4")[33].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['ValorCondenaEnPesos'] = ""

                if Total_campos == 20:

                    Informacion_Actuacion['Tipo'] = '5'

                    #Extraer FechaHoraInicioAudiencia
                    try:
                        Informacion_Actuacion ['FechaHoraInicioAudiencia'] = soup.find_all("div", class_= "col-md-4")[33].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['FechaHoraInicioAudiencia'] = ""

                    #Extraer FechaHoraFinAudiencia
                    try:
                        Informacion_Actuacion ['FechaHoraFinAudiencia'] = soup.find_all("div", class_= "col-md-4")[34].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['FechaHoraFinAudiencia'] = ""

                    #Extraer DepartamentoDentroActuacion
                    try:
                        Informacion_Actuacion ['DepartamentoDentroActuacion'] = soup.find_all("div", class_= "col-md-4")[35].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['DepartamentoDentroActuacion'] = ""

                    #Extraer CiudadDentroActuacion
                    try:
                        Informacion_Actuacion ['CiudadDentroActuacion'] = soup.find_all("div", class_= "col-md-4")[36].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['CiudadDentroActuacion'] = ""

                    #Extraer CorporacionDentroActuacion
                    try:
                        Informacion_Actuacion ['CorporacionDentroActuacion'] = soup.find_all("div", class_= "col-md-4")[37].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['CorporacionDentroActuacion'] = ""

                    #Extraer EspecialidadDentroActuacion
                    try:
                        Informacion_Actuacion ['EspecialidadDentroActuacion'] = soup.find_all("div", class_= "col-md-4")[38].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['EspecialidadDentroActuacion'] = ""

                    #Extraer DespachoDentroActuacion
                    try:
                        Informacion_Actuacion ['DespachoDentroActuacion'] = soup.find_all("div", class_= "col-md-4")[39].input["value"]
                    except KeyError:
                        Informacion_Actuacion ['DespachoDentroActuacion'] = ""

            elif Total_campos == 12:
                Informacion_Actuacion['Tipo'] = '2'
                  #Los campos ya fueron pasados para ser extraidos por Id.
            elif Total_campos == 8:
                Informacion_Actuacion['Tipo'] = '4'

                try:
                    a = soup.find_all("div", class_= "col-md-4")[27]
                    Informacion_Actuacion ['TipoRecurso'] = soup.find_all("div", class_= "col-md-4")[27].input["value"]

                except:
                    Informacion_Actuacion ['TipoRecurso'] = ""

            elif Total_campos == 9:
                Informacion_Actuacion['Tipo'] = '6'

                try:
                    Informacion_Actuacion ['ClaseProceso'] = soup.find_all("div", class_= "col-md-4")[27].input["value"]
                except KeyError:
                    Informacion_Actuacion ['ClaseProceso'] = ""

                try:
                    Informacion_Actuacion ['SubClaseProceso'] = soup.find_all("div", class_= "col-md-4")[28].input["value"]
                except (KeyError, TypeError) as e:
                    Informacion_Actuacion ['SubClaseProceso'] = ""


            else:
                Mensaje_Error = 'Fallo con seleccion tipo de actuaciones - Metodo: Obtener_Informacion()'
                print(Mensaje_Error)
                raise NameError(Mensaje_Error)
           
              
        return Informacion_Actuacion
    
    ###########################################################################################################################################################################################
    def Obtener_Actuaciones(self, soup, n_proceso, Datos_Proceso, Cantidad_Paginas , total_actuaciones, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, url_2, rcookies, Modo_debug):
        """Extrae el numero total de actuaciones de la pagina web, realiza conteo de actuaciones y paginas, y obtiene la informacion detallada de las actuaciones del proceso consultado.
        
        Parametros:
        
        soup                      -- HTML obtenido como resultado de dar click en el primer boton de Lupa.    
        n_proceso                 -- Numero de proceso que se quiere consultar.
        Datos_Proceso             -- Diccionario ordenado que contiene la informacion general del proceso y los sujetos.
        Cantidad_Paginas          -- Numero de paginas de actuaciones contadas en TYBA.
        total_actuaciones         -- Numero total de actuaciones contadas en TYBA.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        url_2                     -- URL de la segunda pagina del TYBA.
        rcookies                  -- Cookies de sesion.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        Retorna un listado con la informacion detallada de las actualizaciones, total de actuaciones contadas y numero total de actuaciones registrado en la pagina web de la rama.
        
        """
        # Se inicializa la lista que contendra las Actuaciones.
        Actuaciones = []
    
        # Se obtiene el numero total de actuaciones registrado en la pagina web de la rama.
        Total_Registros_Web = soup.find_all("span", class_="label label-default")[1].text
        
        # Se inicializa variable que tendra el total de registros contados con el programa,
        total_registros = 0 
           
        # Cada iteracion representa una pagina.
        for pagina in range(1,Cantidad_Paginas+1):    
                          
            # Esta variable almacena la tabla completa.
            tabla = soup.find("table", {"id": "MainContent_grdActuaciones"})
            
            
            # Se inicializa la variable temporal que contendra el total de actuaciones por pagina.
            total_registros_pagina = 0
            
            # Cada iteracion representa una fila de la tabla.
            filas = []
            for fila in tabla.find_all("tr"):
                total_registros_pagina += 1
            #End for
            
            # Debido a que el bucle cuenta la cabecera de la tabla, es necesario descontarla del total de actuaciones por pagina.
            total_registros_pagina -= 1
            
            # Cada iteracion representa un registro de la tabla. Itera hasta el numero total contado de actuaciones por pagina.
            for x in range(1, total_registros_pagina + 1):
                
                # Cada valor td es una casilla de la actuacion. La casilla 0 es el boton, por eso se empieza desde 1. Se suma total_registros a X para asegurar que el nombre Actuacion cuenta mas haya de 10 actuaciones.

                # Retorna un diccionario ordenado con los datos de todas las actuacion obtenidos luego de dar click lupa por lupa.
                Informacion_Actuacion_Returned = self.Obtener_Informacion(x + 1, n_proceso, Datos_Proceso, _VIEWSTATE, _VIEWSTATEGENERATOR,
                                         _EVENTVALIDATION, url_2, rcookies, Modo_debug)

                # Para controlar cuando la pagina falla y no permite ingresar a los detalles de una actuacion se evalua
                # si la información devuelta corresponde a una estructura de actuacion de Tipo 500 es decir que el
                # servidor regresó un Error 500 'Internal Server Error' y si es así se recolecta la información de las
                # actuaciones desde la pagina de actuaciones que tiene informacion basica, especificamente ciclo,
                # tipo actuacion, fecha actuacion y fecha de registro
                if Informacion_Actuacion_Returned['Tipo'] == '500':

                    # Armamos la actuacion solo con la información base
                    Informacion_Actuacion = {}

                    actuacion = tabla.find_all("tr")[x]
                    campos = actuacion.find_all("td")

                    # Extraer Ciclo dentro de Actuacion. Si esta vacio, se guarda "".
                    try:
                        Informacion_Actuacion['Ciclo'] = campos[1].text
                    except:
                        Informacion_Actuacion['Ciclo'] = ""

                    # Extraer Tipo Actuacion dentro de Actuacion. Si esta vacio, se guarda "".
                    try:
                        Informacion_Actuacion['TipoActuacion'] = campos[2].text
                    except:
                        Informacion_Actuacion['TipoActuacion'] = ""

                    # Extraer Fecha Actuacion dentro de Actuacion. Si esta vacio, se guarda "".
                    try:
                        Informacion_Actuacion['FechaActuacion'] = campos[3].text
                    except:
                        Informacion_Actuacion['FechaActuacion'] = ""

                    # Extraer Fecha Registro dentro de Actuacion. Si esta vacio, se guarda "".
                    try:
                        Informacion_Actuacion['FechaRegistro'] = campos[4].text
                    except:
                        Informacion_Actuacion['FechaRegistro'] = ""

                    Actuaciones.append(Informacion_Actuacion)

                    # Se vuelve a colocar el diccionario en vacio para evitar posibles comportamientos no deseados
                    Informacion_Actuacion = {}

                else:

                    Actuaciones.append(Informacion_Actuacion_Returned)

            #Â¿Queda aun alguna pagina por revizar? Si: Click boton siguiente pagina. No: deja terminar el bucle
            if pagina < Cantidad_Paginas:                   
                #Realiza POST simulando boton siguiente, retorna el html que responde la pagina web con los registros de la siguiente pagina
                soup, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION = self.Click_Siguiente_Pagina(n_proceso,Datos_Proceso,_VIEWSTATE,_VIEWSTATEGENERATOR,_EVENTVALIDATION, url_2, rcookies, Modo_debug)
                       
            #Almacena la cantidad total de registros contados hasta el momento
            total_registros += total_registros_pagina
        #End for
        
        #Se corrobora que se hayan contado bien los registros
        if total_registros == total_actuaciones and ((int(Total_Registros_Web) == total_actuaciones and int(Total_Registros_Web) == total_registros) or int(Total_Registros_Web) == 0):
            return Actuaciones, total_registros, Total_Registros_Web
        else:
            Mensaje_Error = 'Fallo en comparacion de conteo de actuaciones - Metodo: Obtener_Actuaciones()'
            raise NameError(Mensaje_Error)
        
    
    ###########################################################################################################################################################################################
    def opcion_correcto(self, Mensaje, n_proceso, n_actuaciones_actual, url_a_extraer, url_2, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Modo_debug):
        """Se encarga de extraer la informacion del proceso consultado y guardarlo en un formato JSON ordenado.
        
        Parametros:
        
        Mensaje                   -- Mensaje que TYBA arroja cuando el estado de consulta es ¡Correcto!.
        n_proceso                 -- Numero de proceso que se quiere consultar.
        n_actuaciones_actual      -- Numero de actuaciones que se sabe que el proceso tiene actualmente.
        url_a_extraer             -- URL de la pagina principal del TYBA.
        url_2                     -- URL de la segunda pagina del TYBA.
        rcookies                  -- Cookies de sesion.
        _VIEWSTATE                -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _VIEWSTATEGENERATOR       -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        _EVENTVALIDATION          -- Variable extraida de ultima peticion HTTP Post necesaria para realizar futuras peticiones HTTP.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        """
        
        # Se inicializa un diccionario ordenado que contendra toda la informacion sobre el proceso consultado.
        Datos_Proceso = {}
        
        print('Modo de acceso: ¡Correcto!')
           
        try:
            # Hace un POST al sitio web simulando dar click al boton lupa. Devuelve el html con la informacion sobre el proceso
            soup, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION = self.Click_Lupa(n_proceso, url_a_extraer, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Modo_debug)
            
        except:

            # Se detalla la ubicacion.
            ubicacion = 'Accion hacer click en el primer boton de lupa - Metodo: Click_Lupa()'           
                       
            # Se guarda un JSON vacio.
            
            return {}, "Error_Programa", sys.exc_info(), ubicacion, False  
        
        
        # Se calcula la cantidad de paginas y el total de actuaciones.
        Cantidad_Paginas , total_actuaciones = self.Calcular_paginas(soup,n_proceso,Datos_Proceso,_VIEWSTATE,_VIEWSTATEGENERATOR,_EVENTVALIDATION, url_2, rcookies, Modo_debug)
        print("Total de paginas: %d" % Cantidad_Paginas)
        print("Total actuaciones contadas en el TYBA: {0}".format(total_actuaciones))
        print("Total actuaciones registradas en Monolegal: {0}".format(n_actuaciones_actual))
        if n_actuaciones_actual == total_actuaciones :
            
            print("No ha habido cambios en proceso {0}".format(n_proceso))
            
            return None, None, None, None, False
            
        else:
            print("Detectados cambios en el proceso {0}".format(n_proceso))
            try:
                # Extrae la informacion basica del proceso y sujetos      
                Datos_Proceso['Info'] = self.Crear_Dict_P_1(soup, url_a_extraer, url_2, n_proceso)
                
            except:
    
                # Se detalla la ubicacion.
                ubicacion = 'Extraccion de informacion de Segunda pagina de la rama - Metodo: Crear_Dict_P_1()'
                                                
                # Se guarda un JSON vacio.
                
                return {}, "Error_Programa", sys.exc_info(), ubicacion, False 
            
            try: 
                #Si el total de actuaciones encontradas es 0 y el total de páginas encontradas también es 0, se retorna con un listado de actuaciones vacío, indicando que total de registros en tyba y total de registros web fue igual a 0.
                if total_actuaciones == 0 and Cantidad_Paginas == 0:
                    total_registros = 0
                    Total_Registros_Web = 0
                    Datos_Proceso["Info"]['Actuaciones'] = []
                    
                else:    
                    # Se almacena el directorio temporal Actuaciones de la funcion "Obtener_Actuaciones()" dentro del directorio Datos de Proceso
                    Datos_Proceso["Info"]['Actuaciones'], total_registros, Total_Registros_Web = self.Obtener_Actuaciones(soup, n_proceso, Datos_Proceso, Cantidad_Paginas , total_actuaciones, _VIEWSTATE , _VIEWSTATEGENERATOR, _EVENTVALIDATION, url_2, rcookies, Modo_debug)    
                

            except:
                
                # Se detalla la ubicacion.
                ubicacion = 'Extracion de informacion de actuaciones - Metodo: Obtener_Actuaciones()'                
                
                # Se escribe la alerta critica en el LOG.
                #self.logger.critical('Codigo de proceso: '+ n_proceso +' - EXTRANO COMPORTAMIENTO. Por favor consultar inmediatamente con Administrador de Sistema! - '+'Ubicacion: ' + ubicacion + ' - ' + str(Mensaje))
                
                # Se guarda un JSON vacio.
                                
                return {}, "Error_Programa", sys.exc_info(), ubicacion, False 
                    
            print("Total actuaciones existentes que dice la pagina Web: %s" % Total_Registros_Web)
            print("Total actuaciones contadas: %d" % total_registros)
            
            #parsea el diccionario ordenado Datos_Proceso a un fichero JSON.
    
            #JSON = json.dumps(Datos_Proceso, ensure_ascii = False)
            
            #print(type(Datos_Proceso))
            return Datos_Proceso, '¡Correcto!', Mensaje, None, True
        
###########################################################################################################################################################################################
    def Consulta(self, url_a_extraer, url_2, n_proceso, n_actuaciones_actual, Modo_debug = True):
        """Extrae de la pagina web del TYBA toda la informacion sobre el proceso "n_proceso".
        
        Puede imprimir por pantalla:
        
        - Codigo de proceso.
        - Modo de acceso.
        - El numero total de actuaciones que dice la pagina web.
        - El numero total de actuaciones contadas con el programa.
        
        Parametros:
        url_a_extraer             -- URL de la pagina principal del TYBA.
        url_2                     -- URL de la segunda pagina del TYBA.
        n_proceso                 -- Numero de proceso que se quiere consultar.
        n_actuaciones_actual      -- Numero de actuaciones que se sabe que el proceso tiene actualmente.
        Modo_debug                -- Controla si el programa se ejecuta en modo debug o no.
        
        NOTA: Modo debug se define como "True" por defecto. NOTA: recordar que anteriormente la variable "Modo_debug" fue negada, por ello ahora con el valor "True" se desactiva el modo debug.
        La negacion de la variable Modo debug se realizo por razones operativas del programa. 
        """  
        
        print('Codigo de Proceso: ' + n_proceso)
        print('Actuaciones registradas en Monolegal: {0}'.format(n_actuaciones_actual))
        
        try: 
 
            # Obtiene las cookies de sesion, resuelve el captcha y obtiene el texto, obtiene las variables "_VIEWSTATE", "_VIEWSTATEGENERATOR", "_EVENTVALIDATION"
            # que serviran para poder realizar futuras peticiones HTTP POST.
            rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Captcha_texto = self.obtener_variables(url_a_extraer, n_proceso, Modo_debug) 
            
        except:
            
            # Se detalla la ubicacion.
            ubicacion = 'Extracion de informacion de pagina principal de la rama - Metodo: obtener_variables()'            
            
            # Se guarda un JSON vacio.
            
            return {}, "Error_Programa", sys.exc_info(), ubicacion, False
        
           
        try:    
            # Hace un HTTP POST al sitio web simulando dar click al boton "Consultar". Devuelve los nuevos valores de vista que se utilizan posteriormente para simular dar click al boton lupa
            Resultado, Mensaje, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION = self.Click_Consultar(n_proceso, url_a_extraer, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Captcha_texto, Modo_debug)
            
        except:

            # Se detalla la ubicacion.
            ubicacion = 'Accion de Click al boton Consultar - Metodo: Click_Consultar()'

            # Se guarda un JSON vacio.
            
            return {}, "Error_Programa", sys.exc_info(), ubicacion, False              
        
        # Se intento aplicar la estructura de Switch para python, pero se encontro la obligacion de pasar variables innecesarias a cada una de las opciones.
        # Hablando con Ivan, se llego a la decision de implementar estructuras if-elif, que simplifican el programa y al no ser demasiadas opciones, no agregan sobrecarga a la ejecucion del metodo.
        # De la pagina web se pueden recibir 4 estados, mas un estado default que se ha estipulado para activarse frente a cualquier error o comportamiento extraÃ±o.
        # La opcion "¡Correcto!" se recibe cuando el codigo de proceso y el captcha han podido ser registrados correctamente.
        # La opcion "¡Advertencia!", hasta ahora, se ha recibido cuando la pagina web responde que el codigo de proceso debe ser consultado personalmente en el despacho judicial correspondiente.
        # La opcion "¡Aviso!", hasta ahora, se ha recibido cuando el codigo de proceso ha sido ingresado erroneamente.
        # La opcion "¡Error!", hasta ahora, se ha recibido cuando se ha ingresado un captcha erroneo.
        # Si ninguna de las anteriores opciones se cumple o si se registra algun error, se emite alerta crítica, se crea un JSON vacio   
        
        if Resultado == '¡Correcto!' :
            JSON, Resultado, Mensaje, Ubicacion, cambio = self.opcion_correcto(Mensaje, n_proceso, n_actuaciones_actual, url_a_extraer, url_2, rcookies, _VIEWSTATE, _VIEWSTATEGENERATOR, _EVENTVALIDATION, Modo_debug)

            if Resultado == 'Error_Programa':

                # Se detalla la ubicacion.
                ubicacion = 'Estado resultado de boton Consultar - Metodo: Consulta()'
                
                # Se copia el mensaje de error.
                Mensaje_error = "Aparicion de nuevo estado en pagina web"
            
                # Se guarda un JSON vacio.            
                return {}, "Error_Programa", Mensaje_error, ubicacion, False 
            
            Resultado = 'ok'
            return JSON, Resultado, Mensaje, Ubicacion, cambio
        
        elif Resultado == '¡Advertencia!' :

            Resultado = 'ok_nopublico'
            
            return {}, Resultado, Mensaje, None, False
        
        elif Resultado == '¡Aviso!' :

            Resultado = 'ko'
            return {}, Resultado, Mensaje, None, False
        
        elif Resultado == '¡Error!' :


            return {}, Resultado, Mensaje, None, False
        
        else :
            print("error")
            # Se detalla la ubicacion.
            ubicacion = 'Estado resultado de boton Consultar - Metodo: Consulta()'
            
            # Se copia el mensaje de error.
            Mensaje_error = "Aparicion de nuevo estado en pagina web"
            
            # Se guarda un JSON vacio.            
            return {}, "Error_Programa", Mensaje_error, ubicacion, False 
                               
###########################################################################################################################################################################################    
    def __init__(self, n_proceso, n_actuaciones_actual, Modo_debug):

   
        # Se ejecuta el metodo Core de la clase. Se le pasan la URL de la pagina principal del TYBA, la URL de la pagina secundaria, el codigo de proceso a consultar, 
        # y el objeto que maneja la escritura de log.
        self.JSON, self.Estado, self.Mensaje, self.Ubicacion, self.cambio = self.Consulta('https://procesojudicial.ramajudicial.gov.co/Justicia21/Administracion/Ciudadanos/frmConsulta', 'https://procesojudicial.ramajudicial.gov.co/Justicia21/Administracion/Ciudadanos/frmConsultaProceso', n_proceso, n_actuaciones_actual, Modo_debug)   
        

                


