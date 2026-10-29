from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Abre o Chrome
driver = webdriver.Chrome()

# Acessa um site
driver.get("https://www.google.com")

# Espera 3 segundos (apenas para você ver)
time.sleep(3)

# Fecha o navegador
driver.quit()