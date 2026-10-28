from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://example.com/login")

username = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "username"))
)
username.send_keys("myuser")

password = driver.find_element(By.NAME, "password")
password.send_keys("mypass")

driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()