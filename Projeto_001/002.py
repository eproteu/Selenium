import os

for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
            "ALL_PROXY", "all_proxy"):
    os.environ.pop(var, None)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument("--no-proxy-server")
options.add_argument("--start-maximized")

with webdriver.Chrome(options=options) as driver:
    wait = WebDriverWait(driver, 10)
    driver.get("https://duckduckgo.com")

    print("1) Página aberta:", driver.title)
    time.sleep(2)
    driver.save_screenshot("01_google_aberto.png")

    # Aceita cookies (várias versões de texto possíveis)
    for texto in ["Aceitar tudo", "Aceitar", "Accept all", "Accept", "Eu concordo"]:
        try:
            botao = driver.find_element(
                By.XPATH, f"//button[contains(., '{texto}')]"
            )
            botao.click()
            print(f"2) Cookie aceito: '{texto}'")
            time.sleep(1)
            break
        except:
            pass
    driver.save_screenshot("02_apos_cookies.png")

    # Caixa de busca
    caixa = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    caixa.clear()
    caixa.send_keys("Python Selenium")
    print("3) Texto digitado:", caixa.get_attribute("value"))
    driver.save_screenshot("03_digitado.png")

    caixa.send_keys(Keys.ENTER)
    print("4) ENTER enviado. URL agora:", driver.current_url)
    time.sleep(3)
    driver.save_screenshot("04_apos_busca.png")

    # Tenta achar resultados (h3 ou h2)
    print("5) Procurando resultados...")
    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "h3, h2")
        ))
        titulos = driver.find_elements(By.CSS_SELECTOR, "h3, h2")
        vistos = set()
        contador = 0
        print()
        for t in titulos:
            txt = t.text.strip()
            if txt and txt not in vistos:
                vistos.add(txt)
                contador += 1
                print(f"{contador}. {txt}")
                if contador >= 5:
                    break
    except Exception as e:
        print("❌ Não encontrou resultados:", e)
        print("   URL atual:", driver.current_url)
        driver.save_screenshot("05_sem_resultados.png")

    input("\nENTER para fechar...")