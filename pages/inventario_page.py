from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class InventarioPage:
    TITULO = (By.CLASS_NAME, "title")
    BOTAO_ADD_MOCHILA = (By.ID, "add-to-cart-sauce-labs-backpack")
    BADGE_CARRINHO = (By.CLASS_NAME, "shopping_cart_badge")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def obter_titulo(self):
        return self.wait.until(EC.visibility_of_element_located(self.TITULO)).text

    def adicionar_mochila(self):
        self.wait.until(EC.element_to_be_clickable(self.BOTAO_ADD_MOCHILA)).click()

    def quantidade_no_carrinho(self):
        return int(self.wait.until(EC.visibility_of_element_located(self.BADGE_CARRINHO)).text)