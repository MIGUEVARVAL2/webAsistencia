from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time

def test_login():
    driver =webdriver.Edge()
    driver.get("http://127.0.0.1:8000/")  # Reemplaza con la URL de tu página de inicio de sesión
    driver.maximize_window()
    time.sleep(3)


    #Index Registro
    register_button = driver.find_element(By.ID,"register-tab")  # Reemplaza con el nombre del botón de registro
    register_button.click()
    time.sleep(3)
    documento_field = driver.find_element(By.ID,"documento")
    documento_field.send_keys("1020304050")
    nombres_field = driver.find_element(By.ID,"nombres")
    nombres_field.send_keys("Ejemplo de nombres")
    apellidos_field = driver.find_element(By.ID,"apellidos")
    apellidos_field.send_keys("Apellidos con Selenium")
    correo_field = driver.find_element(By.ID,"correo_registro")
    correo_field.send_keys("prueba_selenium@unal.edu.co")
    password_field = driver.find_element(By.ID,"password_registro")   # Reemplaza con el nombre del campo de entrada de la contraseña
    password_field.send_keys("Prueba12345*")
    time.sleep(3)

    login_button = driver.find_element(By.ID,"btnRegistro")  # Reemplaza con el nombre del botón de inicio de sesión
    login_button.click()
    time.sleep(3)


    # Index Inicio de Sesión 
    
    login_button = driver.find_element(By.ID,"login-tab")  # Reemplaza con el nombre del botón de inicio de sesión
    login_button.click()
    time.sleep(3)
    rol_select = driver.find_element(By.ID, "rol")
    select = Select(rol_select)
    select.select_by_value("profesor")
    username_field = driver.find_element(By.ID,"email")  # Reemplaza con el nombre del campo de entrada del nombre de usuario
    password_field = driver.find_element(By.ID,"password")   # Reemplaza con el nombre del campo de entrada de la contraseña
    username_field.send_keys("prueba_selenium@unal.edu.co")
    password_field.send_keys("Prueba12345*")
    time.sleep(3)
    # Encuentra y haz clic en el botón de inicio de sesión
    login_button = driver.find_element(By.ID,"btnInicioSesion")  # Reemplaza con el nombre del botón de inicio de sesión
    login_button.click()
    time.sleep(3)


    #Cursos estudiantes crear curso
    crear_curso = driver.find_element(By.ID,"crear-curso-btn-modal")  # Reemplaza con el nombre del botón de inicio de sesión
    crear_curso.click()
    time.sleep(3)
    nombre_curso = driver.find_element(By.ID,"nombreCurso") 
    nombre_curso.send_keys("Curso de Prueba con Selenium")
    grupo_curso = driver.find_element(By.ID,"grupo_curso") 
    grupo_curso.send_keys("Prueba 1")
    anio_curso = driver.find_element(By.ID,"anio") 
    anio_curso.send_keys("2024")
    semestre_curso =driver.find_element(By.CSS_SELECTOR, "input[type='radio'][id='semestre_curso'][value='2S']") 
    semestre_curso.click()
    archivo_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][id='archivo']")
    archivo_input.send_keys("M:/Convocatoria/WebAplicacion/myapp/test/archivos/report (24).xls")
    time.sleep(3)

    button_crear_curso = driver.find_element(By.ID,"crearCursoBTN")  # Reemplaza con el nombre del botón de inicio de sesión
    button_crear_curso.click()
    time.sleep(3)
    

    #Crear grupo
    crear_grupo_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-outline-success.float-end.crear-grupo")
    crear_grupo_button.click()
    time.sleep(3)
    nombre_grupo = driver.find_element(By.ID,"numero_grupo_nuevo")
    nombre_grupo.send_keys("Prueba 3")
    archivo_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][id='archivo_nuevo_grupo']")
    archivo_input.send_keys("M:/Convocatoria/WebAplicacion/myapp/test/archivos/report (24).xls")
    time.sleep(3)
    button_crear_grupo = driver.find_element(By.ID,"crear_nuevo_grupo")  # Reemplaza con el nombre del botón de inicio de sesión
    button_crear_grupo.click()
    time.sleep(3)

    #Eliminar Grupos








    # Asegúrate de que el inicio de sesión fue exitoso verificando algún elemento en la página de destino
    assert "AsistenciaUN" in driver.title  # Reemplaza con el título de tu página de destino después del inicio de sesión

    driver.close()

if __name__ == "__main__":
    test_login()