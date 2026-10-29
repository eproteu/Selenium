from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
try:
    driver.get("https://the-internet.herokuapp.com/checkboxes")

    checkboxes = driver.find_elements(By.CSS_SELECTOR, "#checkboxes input[type='checkbox']")
    assert len(checkboxes) == 2, "esperava 2 checkboxes"
    cb1, cb2 = checkboxes

    # ---- estado inicial ----
    print("Inicial -> cb1:", cb1.is_selected(), "| cb2:", cb2.is_selected())
    assert cb1.is_selected() is False
    assert cb2.is_selected() is True

    # ---- marcar o primeiro ----
    cb1.click()
    assert cb1.is_selected() is True
    print("Após clicar cb1 -> marcado:", cb1.is_selected())

    # ---- desmarcar o segundo ----
    cb2.click()
    assert cb2.is_selected() is False
    print("Após clicar cb2 -> marcado:", cb2.is_selected())

    # ---- idempotência: 2 cliques voltam ao estado anterior ----
    estado_antes = cb1.is_selected()      # captura o estado REAL
    cb1.click()
    cb1.click()
    assert cb1.is_selected() == estado_antes
    print(f"Idempotência OK: cb1 continuou {estado_antes}")

    print("✅ Todos os asserts passaram!")
finally:
    driver.quit()