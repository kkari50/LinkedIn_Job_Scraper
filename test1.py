from lxml import html
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys


driver_path = "C:\\Users\\kkari\\Desktop\\dev\\LinkedIn_extractor\\chromedriver.exe"
browser = webdriver.Chrome(driver_path)

browser.get('https://www.linkedin.com/login')


