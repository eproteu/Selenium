from pages.login_page import LoginPage
from pages.inventario_page import InventarioPage


def test_adicionar_produto_ao_carrinho(driver):
    login = LoginPage(driver)
    login.abrir()
    login.login("standard_user", "secret_sauce")

    inventario = InventarioPage(driver)
    inventario.adicionar_mochila()

    assert inventario.quantidade_no_carrinho() == 1