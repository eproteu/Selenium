import csv
import html
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

URL_INICIAL = "https://books.toscrape.com"
MAX_PAGINAS = 10  # limite do rastreamento

cache_status = {}


def criar_driver():
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    return webdriver.Chrome(options=opts)


def status_link(url):
    """Retorna o status HTTP (0 = sem resposta)."""
    if url in cache_status:
        return cache_status[url]
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        if r.status_code in (403, 405, 501):
            r = requests.get(url, timeout=10, stream=True)
        status = r.status_code
    except requests.RequestException:
        status = 0
    cache_status[url] = status
    return status


def analisar_pagina(driver, url):
    driver.get(url)
    dominio = urlparse(url).netloc

    # Links
    todos = set()
    for a in driver.find_elements(By.TAG_NAME, "a"):
        href = a.get_attribute("href")
        if href:
            href = urldefrag(urljoin(url, href))[0]
            if urlparse(href).scheme in ("http", "https"):
                todos.add(href)
    internos = {h for h in todos if urlparse(h).netloc == dominio}
    externos = todos - internos

    with ThreadPoolExecutor(max_workers=10) as pool:
        resultados = dict(zip(todos, pool.map(status_link, todos)))
    quebrados = {h: s for h, s in resultados.items() if s == 0 or s >= 400}

    # Imagens
    imagens_quebradas = driver.execute_script(
        "return Array.from(document.images)"
        ".filter(i => i.complete && i.naturalWidth === 0).map(i => i.src);"
    )
    sem_alt = driver.execute_script(
        "return Array.from(document.images)"
        ".filter(i => !i.getAttribute('alt')).length;"
    )

    # Outras métricas
    meta = driver.find_elements(By.CSS_SELECTOR, "meta[name='description']")
    tempo_ms = driver.execute_script(
        "return performance.getEntriesByType('navigation')[0].duration;"
    )

    dados = {
        "url": url,
        "titulo": driver.title,
        "tempo_s": round(tempo_ms / 1000, 2),
        "links_total": len(todos),
        "links_internos": len(internos),
        "links_externos": len(externos),
        "links_quebrados": len(quebrados),
        "imagens_total": len(driver.find_elements(By.TAG_NAME, "img")),
        "imagens_quebradas": len(imagens_quebradas),
        "imagens_sem_alt": sem_alt,
        "scripts": len(driver.find_elements(By.TAG_NAME, "script")),
        "formularios": len(driver.find_elements(By.TAG_NAME, "form")),
        "h1": len(driver.find_elements(By.TAG_NAME, "h1")),
        "tem_meta_description": "sim" if meta else "não",
    }
    return dados, internos, quebrados, imagens_quebradas


def rastrear():
    driver = criar_driver()
    fila, visitadas = deque([URL_INICIAL]), set()
    paginas, detalhes = [], []
    try:
        while fila and len(visitadas) < MAX_PAGINAS:
            url = fila.popleft()
            if url in visitadas:
                continue
            visitadas.add(url)
            print(f"[{len(visitadas)}/{MAX_PAGINAS}] {url}")
            dados, internos, quebrados, img_q = analisar_pagina(driver, url)
            paginas.append(dados)
            detalhes.append((url, quebrados, img_q))
            fila.extend(i for i in internos if i not in visitadas)
    finally:
        driver.quit()
    return paginas, detalhes


def gerar_csv(paginas):
    with open("relatorio.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=paginas[0].keys(), delimiter=";")
        w.writeheader()
        w.writerows(paginas)


def gerar_html(paginas, detalhes):
    soma = lambda chave: sum(p[chave] for p in paginas)
    cards = "".join(
        f"<div class='card'><b>{v}</b><span>{k}</span></div>"
        for k, v in [
            ("Páginas analisadas", len(paginas)),
            ("Links (soma)", soma("links_total")),
            ("Links quebrados", soma("links_quebrados")),
            ("Imagens (soma)", soma("imagens_total")),
            ("Imagens quebradas", soma("imagens_quebradas")),
            ("Imagens sem alt", soma("imagens_sem_alt")),
        ]
    )

    cabecalho = "".join(f"<th>{html.escape(c)}</th>" for c in paginas[0])
    linhas = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in p.values()) + "</tr>"
        for p in paginas
    )

    problemas = ""
    for url, quebrados, img_q in detalhes:
        if quebrados or img_q:
            problemas += f"<h3>{html.escape(url)}</h3><ul>"
            problemas += "".join(
                f"<li>Link {s or 'sem resposta'}: {html.escape(h)}</li>"
                for h, s in quebrados.items()
            )
            problemas += "".join(
                f"<li>Imagem quebrada: {html.escape(i)}</li>" for i in img_q
            )
            problemas += "</ul>"
    problemas = problemas or "<p>Nenhum problema encontrado.</p>"

    pagina = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório do site</title>
<style>
body{{font-family:Arial,sans-serif;margin:2rem;color:#222}}
.cards{{display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0}}
.card{{background:#f2f4f8;padding:1rem 1.5rem;border-radius:8px;text-align:center}}
.card b{{display:block;font-size:1.8rem}}
table{{border-collapse:collapse;font-size:.85rem;display:block;overflow-x:auto}}
th,td{{border:1px solid #ccc;padding:6px 10px;text-align:left}}
th{{background:#e8ebf1}}
</style></head><body>
<h1>Relatório do site</h1>
<p>{html.escape(URL_INICIAL)} - {datetime.now():%d/%m/%Y %H:%M}</p>
<div class="cards">{cards}</div>
<h2>Métricas por página</h2>
<table><tr>{cabecalho}</tr>{linhas}</table>
<h2>Problemas encontrados</h2>{problemas}
</body></html>"""
    with open("relatorio.html", "w", encoding="utf-8") as f:
        f.write(pagina)


if __name__ == "__main__":
    paginas, detalhes = rastrear()
    gerar_csv(paginas)
    gerar_html(paginas, detalhes)
    print("Pronto: relatorio.html e relatorio.csv")