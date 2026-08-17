from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeWebDriverFactory:

    @staticmethod
    def create():

        options = Options()

        #options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")

        return webdriver.Chrome(options=options)