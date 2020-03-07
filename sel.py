from selenium import webdriver
chrome_path = r"/usr/bin/chromedriver"
driver = webdriver.Chrome(chrome_path)
driver.get("http://www.mcmaster.com")
