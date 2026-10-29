from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
try:
    driver.get("https://the-internet.herokuapp.com/inputs")

    campo = driver.find_element(By.CSS_SELECTOR, "input[type='number']")

    # ---- 1) estado inicial: vazio ----
    assert campo.get_attribute("value") == ""
    print("Inicial -> value:", repr(campo.get_attribute("value")))

    # ---- 2) digitar um número ----
    campo.send_keys("42")
    assert campo.get_attribute("value") == "42"
    print("Após digitar -> value:", campo.get_attribute("value"))

    # ---- 3) limpar o campo ----
    campo.clear()
    assert campo.get_attribute("value") == ""
    print("Após clear -> value:", repr(campo.get_attribute("value")))

    # ---- 4) incrementar com a setinha ↑ ----
    campo.send_keys(Keys.ARROW_UP)
    assert campo.get_attribute("value") == "1"
    print("Após ARROW_UP -> value:", campo.get_attribute("value"))

    # ---- 5) decrementar duas vezes ----
    campo.send_keys(Keys.ARROW_DOWN)
    campo.send_keys(Keys.ARROW_DOWN)
    assert campo.get_attribute("value") == "-1"
    print("Após 2x ARROW_DOWN -> value:", campo.get_attribute("value"))

    # ---- 6) digitar letra (input number rejeita) ----
    campo.clear()
    campo.send_keys("abc")
    assert campo.get_attribute("value") == ""   # letras não entram
    print("Após digitar 'abc' -> value:", repr(campo.get_attribute("value")))

    print("✅ Todos os asserts passaram!")
finally:
    driver.quit()