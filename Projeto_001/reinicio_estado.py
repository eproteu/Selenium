from selenium import webdriver
from selenium.webdriver.common.by import By

def set_checkbox(cb, marcado: bool):
    """Garante que o checkbox fique no estado desejado."""
    if cb.is_selected() != marcado:
        cb.click()

driver = webdriver.Chrome()
try:
    driver.get("https://the-internet.herokuapp.com/checkboxes")

    # 1) CAPTURAR os checkboxes  ← isso define cb1 e cb2
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "#checkboxes input[type='checkbox']")
    assert len(checkboxes) == 2, "esperava 2 checkboxes"
    cb1, cb2 = checkboxes

    # 2) agora sim, pode usar o helper
    set_checkbox(cb1, False)   # garante cb1 desmarcado
    set_checkbox(cb2, True)    # garante cb2 marcado

    assert cb1.is_selected() is False
    assert cb2.is_selected() is True
    print("✅ Estado de partida garantido:", cb1.is_selected(), cb2.is_selected())

    # ---- agora os cenários ficam independentes ----
    # cenário A: marcar cb1
    set_checkbox(cb1, True)
    assert cb1.is_selected() is True
    print("Cenário A OK -> cb1 marcado")

    # cenário B: reinicia e desmarca cb1
    set_checkbox(cb1, False)
    assert cb1.is_selected() is False
    print("Cenário B OK -> cb1 desmarcado")

    # cenário C: idempotência — pedir o mesmo estado não deve mudar nada
    set_checkbox(cb1, True)
    estado_antes = cb1.is_selected()
    set_checkbox(cb1, True)          # já está marcado → não clica
    assert cb1.is_selected() == estado_antes
    print(f"Cenário C OK -> idempotente (continuou {estado_antes})")

    print("✅ Todos os asserts passaram!")
finally:
    driver.quit()