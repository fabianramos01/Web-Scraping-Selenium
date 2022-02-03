# from pytesseract import image_to_string

# text = image_to_string('captcha.PNG', config="--psm 6")
# print(text.splitlines()[0])
import cv2
import MonoImgTxtv3


def obtener_captcha():
    """Devuelve el string del captcha.
    """
    # Abre el captcha guardado con cv2
    Captcha_original = cv2.imread("captcha.PNG")

    # Envia el captcha a la funcion MonoImgTxtv3 y devuelve el string del captcha.
    Captcha_string = MonoImgTxtv3.main(Captcha_original)

    # Devuelve el string obtenido
    return Captcha_string

# def obtener_variables():
#     """Descifra el Captcha y obtiene las cookies y valores necesarios para poder realizar futuras peticiones HTTP POST.
#
#     Retorna el texto del Captcha, las cookies de sesion, y variables necesarias para realizar la peticion HTTP Post que simula dar click al boton "Consultar".
#
#     Parametros:
#
#     url_a_extraer -- URL de la pagina principal del TYBA.
#     n_proceso     -- Numero de proceso que se quiere consultar.
#     Modo_debug    -- Controla si el programa se ejecuta en modo debug o no.
#
#     """
#     while True:
#         # Bucle que termina cuando se ha obtenido un valor correcto de captcha. Puede terminar algunas veces con un captcha que posea un caracter incorrecto.
#
#         # Variable que permite que el bucle while se reinicie cuando se detecta un valor no alfanumerico dentro del resultado de traduccion del captcha
#         repetir = False
#
#         # Metodo que descarga el captcha de la pagina web manteniendo sesion abierta
#
#         # Devuelve el string del captcha
#         Captcha_texto = obtener_captcha()
#
#         # Si el string de la traduccion es mas largo que 8 esta mal, se rompe el bucle y se solicita a la pagina web un nuevo captcha
#         if len(Captcha_texto) > 6:
#             print("Error. Captcha largo. Intentando de nuevo")
#             continue
#
#         # Se comprueba caracter por caracter si es alphanumerico. Si no, se rompe el bucle for con continue, y el bucle while con "repetir"
#         for character in Captcha_texto:
#             if not character.isalpha() and not character.isdigit():
#                 print("Error. Caracter en captcha no deseado. Intentando de nuevo")
#                 repetir = True
#                 continue
#         # End for
#
#         # Si repetir se pone en True, el captcha fue mal traducido por lo que es necesario solicitar un nuevo captcha. Entonces se vuelve al principio
#         if repetir == True:
#             continue
#
#         # Como en los captcha no hay ni "Z", "O" o "Q", y estos valores siempre son confundidos con "2", "0" y "9" respectivamente
#         Captcha_texto = Captcha_texto.replace("Z", "2")
#
#         # Se decide reemplazar manualmente estos valores siempre.
#         Captcha_texto = Captcha_texto.replace("O", "0")
#
#         # Se recomienda crear una funcion que este atenta a si un captcha erroneo es enviado, asi simplemente se solicita uno nuevo.
#         Captcha_texto = Captcha_texto.replace("Q", "9")
#
#         break
#
#     # End While
#     return Captcha_texto

# print(obtener_variables())
print(obtener_captcha())