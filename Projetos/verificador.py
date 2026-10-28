import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

PAGINAS = [
    "https://www.devbueno.com.br",
    "https://books.toscrape.com/unesp.html",
]
LIMITE_CARREGAMENTO_S = 5
TEXTOS_DE_ERRO = ["404", "500", "internal server error", "page not found"]


def criar_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return webdriver.Chrome(options=opts)


def checar_console(driver):
    logs = driver.get_log("browser")
    return [f"JS: {l['message']}" for l in logs if l["level"] == "SEVERE"]


def checar_tempo(driver):
    ms = driver.execute_script(
        "return performance.getEntriesByType('navigation')[0].duration"
    )
    seg = ms / 1000
    if seg > LIMITE_CARREGAMENTO_S:
        return [f"Página lenta: {seg:.1f}s (limite {LIMITE_CARREGAMENTO_S}s)"]
    return []


def checar_imagens(driver):
    erros = []
    for img in driver.find_elements(By.TAG_NAME, "img"):
        quebrada = driver.execute_script(
            "return arguments[0].complete && arguments[0].naturalWidth === 0", img
        )
        if quebrada:
            erros.append(f"Imagem quebrada: {img.get_attribute('src')}")
    return erros


def checar_texto_de_erro(driver):
    texto = driver.find_element(By.TAG_NAME, "body").text.lower()
    titulo = driver.title.lower()
    return [
        f"Texto suspeito na página: '{t}'"
        for t in TEXTOS_DE_ERRO
        if t in titulo or (t in texto and len(texto) < 500)
    ]


def checar_links(driver, url_base):
    hrefs = {
        urljoin(url_base, a.get_attribute("href"))
        for a in driver.find_elements(By.TAG_NAME, "a")
        if a.get_attribute("href")
    }
    erros = []
    for href in hrefs:
        if urlparse(href).scheme not in ("http", "https"):
            continue
        try:
            r = requests.head(href, timeout=10, allow_redirects=True)
            if r.status_code == 405:  # servidor não aceita HEAD
                r = requests.get(href, timeout=10)
            if r.status_code >= 400:
                erros.append(f"Link quebrado ({r.status_code}): {href}")
        except requests.RequestException as e:
            erros.append(f"Link sem resposta: {href} ({type(e).__name__})")
    return erros


def verificar_pagina(driver, url):
    driver.get(url)
    erros = []
    erros += checar_texto_de_erro(driver)
    erros += checar_console(driver)
    erros += checar_tempo(driver)
    erros += checar_imagens(driver)
    erros += checar_links(driver, url)
    if erros:
        nome = f"erro_{urlparse(url).path.strip('/').replace('/', '_') or 'home'}.png"
        driver.save_screenshot(nome)
    return erros


def main():
    driver = criar_driver()
    relatorio = {}
    try:
        for url in PAGINAS:
            print(f"Verificando {url} ...")
            relatorio[url] = verificar_pagina(driver, url)
    finally:
        driver.quit()

    total = sum(len(e) for e in relatorio.values())
    linhas = [f"Relatório - {datetime.now():%d/%m/%Y %H:%M}", ""]
    for url, erros in relatorio.items():
        linhas.append(f"{'OK  ' if not erros else 'FALHA'} {url}")
        linhas += [f"    - {e}" for e in erros]
    linhas.append(f"\nTotal de problemas: {total}")

    texto = "\n".join(linhas)
    print("\n" + texto)
    with open("relatorio.txt", "w", encoding="utf-8") as f:
        f.write(texto)

    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()