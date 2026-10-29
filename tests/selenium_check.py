import json
import sys
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By

base_url = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5004").rstrip("/")
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--window-size=1200,800")

with webdriver.Chrome(options=options) as browser:
    browser.get(base_url + "/health")
    health = json.loads(browser.find_element(By.TAG_NAME, "body").text)
    assert health["status"] == "UP"
    browser.get(base_url + "/beta")
    beta = json.loads(browser.find_element(By.TAG_NAME, "body").text)
    assert beta["enabled"] is True, "Start the app with FEATURE_BETA=true"
    Path("docs/screenshots").mkdir(parents=True, exist_ok=True)
    browser.save_screenshot("docs/screenshots/beta-browser.png")
    print("Health and enabled beta feature passed in Chrome.")
