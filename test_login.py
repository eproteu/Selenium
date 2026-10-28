from pages.login_page import LoginPage
from pages.inventario_page import InventarioPage


def test_login_valido(driver):
    login = LoginPage(driver)
    login.abrir()
    login.login("standard_user", "secret_sauce")

    assert InventarioPage(driver).obter_titulo() == "Products"


def test_login_senha_invalida(driver):
    login = LoginPage(driver)
    login.abrir()
    login.login("standard_user", "senha_errada")

    assert "do not match" in login.obter_mensagem_erro()


def test_usuario_bloqueado(driver):
    login = LoginPage(driver)
    login.abrir()
    login.login("locked_out_user", "secret_sauce")

    assert "locked out" in login.obter_mensagem_erro()