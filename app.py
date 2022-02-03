import os

from past.builtins import raw_input
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import json

from pytesseract import image_to_string


def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = document.querySelector('downloads-manager')
            .shadowRoot.getElementById('downloadsList').items;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.fileUrl || e.file_url);
        """)


def download_files(driver):
    table = WebDriverWait(driver, 50).until(
        expected_conditions.presence_of_element_located(
            (By.ID, 'MainContent_grdArchivos')))
    count = 2
    state = True
    while state:
        state = False
        for i in table.find_elements_by_tag_name('input'):
            i.click()
        paginator = table.find_element_by_tag_name('table')
        for a in paginator.find_elements_by_tag_name('a'):
            if a.text == str(count):
                print(a.text)
                state = True
                count += 1
                a.click()
                table = WebDriverWait(driver, 50).until(
                    expected_conditions.presence_of_element_located(
                        (By.ID, 'MainContent_grdArchivos')))
                break
    # waits for all the files to be completed and returns the paths
    paths = WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
    print('Dirección del archivo', paths)
    print('Cantidad de archivoa', len(paths))


def load_json(url):
    with open(url) as f:
        data = json.load(f)
    return data


def submit_form(driver):
    state = False
    count = 0
    while not state and count < 5:
        # Input image captcha
        driver.find_element_by_id("MainContent_imgCaptcha").screenshot('captcha.PNG')
        text = image_to_string('captcha.PNG', config="--psm 7")
        driver.find_element_by_name('ctl00$MainContent$txtCaptchaText').send_keys(text.splitlines()[0])

        # Input submit
        driver.find_element_by_name("ctl00$MainContent$btnConsultar").click()

        # Download file
        print('----------')
        try:
            element = WebDriverWait(driver, 100).until(
                expected_conditions.presence_of_element_located(
                    (By.ID, 'MainContent_UC_MensajeInformativo_divAdvertencia')))
            print(element.find_element_by_id('MainContent_UC_MensajeInformativo_lblTitulo').text)
            print(element.find_element_by_id('MainContent_UC_MensajeInformativo_lblMensajes').text)
            if 'alert-info' in element.get_attribute("class"):
                # No se encontraron registros.
                # Registros Coincidentes
                state = True
            elif 'alert-success' in element.get_attribute("class"):
                download_files(driver)
                return True
            elif 'alert-danger' in element.get_attribute(
                    "class") and 'El valor de la Capcha no coincide.' == element.find_element_by_id(
                'MainContent_UC_MensajeInformativo_lblMensajes').text:
                # El valor de la Capcha no coincide.
                state = False
            else:
                state = True
        except TimeoutException as ex:
            print("Excepción. " + str(ex))
            state = False
        finally:
            print('Proceso finalizado')
        count += 1
    return state


def execute_process(data):
    url = 'https://procesojudicial.ramajudicial.gov.co/Justicia21/Administracion/Descargas/frmArchivosEstados.aspx'
    # Driver instance
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    driver = webdriver.Chrome(chromedriver_path)
    driver.implicitly_wait(10)
    driver.get(url)

    # Input process code
    driver.find_element_by_name('ctl00$MainContent$txtCodigoProceso').send_keys(data['NumProceso'])

    # Select identification type
    identification_type = Select(driver.find_element_by_name('ctl00$MainContent$ddlTipoDocumento'))
    # identification_type = identification_type.select_by_value("1")

    # Input identification number
    driver.find_element_by_name('ctl00$MainContent$txtNumeroIdentificacion').send_keys(
        data['identification_number'] if 'identification_number' in data else '')

    # Input first name
    driver.find_element_by_name('ctl00$MainContent$txtPrimerNombre').send_keys(
        data['first_name'] if 'first_name' in data else '')

    # Input second name
    driver.find_element_by_name('ctl00$MainContent$txtSegundoNombre').send_keys(
        data['second_name'] if 'second_name' in data else '')

    # Input first surname
    driver.find_element_by_name('ctl00$MainContent$txtPrimerApellido').send_keys(
        data['first_surname'] if 'first_surname' in data else '')

    # Input second surname
    driver.find_element_by_name('ctl00$MainContent$txtSegundoApellido').send_keys(
        data['second_surname'] if 'second_surname' in data else '')

    # Input social reason
    driver.find_element_by_name('ctl00$MainContent$txtRazonSocial').send_keys(
        data['social_reason'] if 'social_reason' in data else '')

    # Select department
    # department_id = '3'
    # department_name = 'BOGOTA 11'
    # department_select = Select(driver.find_element_by_name('ctl00$MainContent$ddlDepartamento'))
    # department_select.select_by_visible_text(data['NombreDepartamento'])
    # department_select.select_by_value(department_id)

    department_select = driver.find_element_by_name('ctl00$MainContent$ddlDepartamento')
    for i in department_select.find_elements_by_tag_name('option'):
        if data['NombreDepartamento'] in i.text:
            i.click()
            break

    # Select city
    # city_id = '149'
    # city_name = 'BOGOTA, D.C. 11001'
    city_select = WebDriverWait(driver, 100).until(
        expected_conditions.element_to_be_clickable((By.NAME, 'ctl00$MainContent$ddlCiudad')))
    # city_select = Select(city)
    # city_select.select_by_visible_text(data['NombreCiudad'])
    for i in city_select.find_elements_by_tag_name('option'):
        if data['NombreCiudad'] in i.text:
            i.click()
            break
    # city_select.select_by_value(city_id)

    # Select corporation
    # corporation_id = '13'
    # corporation_name = 'JUZGADO DE CIRCUITO 31'
    corporation_select = WebDriverWait(driver, 100).until(
        expected_conditions.element_to_be_clickable((By.NAME, 'ctl00$MainContent$ddlCorporacion')))
    # corporation_select = Select(corporation)
    # corporation_select.select_by_visible_text(data['NombreCorporacion'])
    # corporation_select.select_by_value(corporation_id)
    for i in corporation_select.find_elements_by_tag_name('option'):
        if data['NombreCorporacion'] in i.text:
            i.click()
            break

    # Select speciality
    # speciality_id = '54'
    # speciality_name = 'JUZGADO DE CIRCUITO  FAMILIA 10'
    speciality_select = WebDriverWait(driver, 100).until(
        expected_conditions.element_to_be_clickable((By.NAME, 'ctl00$MainContent$ddlEspecialidad')))
    # speciality_select = Select(speciality)
    # speciality_select.select_by_visible_text(data['NombreEspecialidad'])
    # speciality_select.select_by_value(speciality_id)
    for i in speciality_select.find_elements_by_tag_name('option'):
        if data['NombreEspecialidad'] in i.text:
            i.click()
            break

    # Select office
    office_id = '478'
    # office_name = 'juzgado de circuito - familia 023 bogota dc 023'
    office_select = WebDriverWait(driver, 100).until(
        expected_conditions.element_to_be_clickable((By.NAME, 'ctl00$MainContent$ddlDespacho')))
    # office_select = Select(office)
    # office_select.select_by_visible_text(data['Despacho'])
    # office_select.select_by_value(office_id)
    for i in office_select.find_elements_by_tag_name('option'):
        if data['Despacho'].upper() in i.text:
            i.click()
            break

    # Start date
    driver.execute_script(
        "document.getElementById('MainContent_txtFechaInicio').setAttribute('value', '" + data['FechaInicio'] + "')")

    # End date
    driver.execute_script(
        "document.getElementById('MainContent_txtFechaFin').setAttribute('value', '" + data['FechaFin'] + "')")

    # Submit form
    state = submit_form(driver)

    # Close connection
    driver.close()
    driver.quit()

    return state


def run_app(url):
    data = load_json(url)
    for item in data['procesos']['proceso']:
        execute_process(item)

try:
    data = os.path.join(os.getcwd(), 'data/pruebas.json')
    run_app('C:/Users/maqui/Documentos/webScraping/data/pruebas.json')
except Exception as e:
    print('Unexpected error:' + str(e))
finally:
    raw_input('Presione Enter para terminar')

# pyinstaller -F --add-binary "./chromedriver.exe";"." app.py
