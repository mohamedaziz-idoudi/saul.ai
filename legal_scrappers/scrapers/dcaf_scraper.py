from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def initialize_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

def scrape_site(url):
    driver = initialize_driver()
    try:
        driver.get(url)
        time.sleep(2)  # Adjust wait as needed
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for idx, p in enumerate(paragraphs, start=1):
            print(f"Paragraph {idx}: {p.text}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    target_url = "https://www.example.com"  # Replace with actual target
    scrape_site(target_url)
