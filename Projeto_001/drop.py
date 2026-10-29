from selenium.webdriver.support.ui.select import Select
select = Select(driver.find_element(By.ID, "dropdown"))
select.select_by_visible_text("Option 1")