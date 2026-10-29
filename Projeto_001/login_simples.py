import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# (opcional) reduz ruído de logs do Selenium
logging.getLogger("selenium").setLevel(logging.ERROR)

driver = webdriver.Chrome()
try:
    driver.get("https://the-internet.herokuapp.com/login")

    driver.find_element(By.ID, "username").send_keys("tomsmith")
    driver.find_element(By.ID, "password").send_keys("SuperSecretPassword!")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    flash = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".flash.success"))
    )

    # pega só o texto, sem o "×"
    texto = driver.execute_script(
        "return arguments[0].childNodes[0].textContent.trim();", flash
    )

    assert "You logged into a secure area!" in texto
    print("✅ Login OK:", texto)
finally:
    driver.quit()