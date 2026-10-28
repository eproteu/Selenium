from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://books.toscrape.com")
print(driver.title)

livros = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")
for livro in livros[:5]:
    print(livro.get_attribute("title"))

driver.quit()