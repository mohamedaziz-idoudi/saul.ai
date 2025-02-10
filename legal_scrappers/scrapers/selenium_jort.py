from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Setup Selenium WebDriver
options = Options()
options.add_argument('--headless')  # Run browser in headless mode (without UI)
options.add_argument('--no-sandbox')  # Bypass sandbox for Chrome
options.add_argument('--disable-dev-shm-usage')  # Disable shared memory usage for better performance

# Setup ChromeDriver service
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Open the target page
url = "https://9anoun.tn/fr/kb/codes"
driver.get(url)

# Step 1: Click "Charger" until all items are loaded
while True:
    try:
        load_more_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Charger')]")))
        driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        ActionChains(driver).move_to_element(load_more_button).click().perform()
        time.sleep(2)  # Allow new content to load
    except Exception as e:
        print("No more 'Charger' button found. Finished loading all items.")
        break

# Step 2: Extract all code links from the page
codes = []
code_elements = driver.find_elements(By.CSS_SELECTOR, "div.Ee a")
for code in code_elements:
    code_name = code.text.strip()
    code_link = code.get_attribute("href")
    if code_link:
        codes.append({"name": code_name, "link": code_link, "articles": []})

print(f"Extracted {len(codes)} codes.")

# Step 3: Visit each code page and extract article links and full content
for code in codes:
    driver.get(code["link"])
    time.sleep(2)

    article_elements = driver.find_elements(By.CSS_SELECTOR, "div.xd.Cj a")
    
    for article in article_elements:
        # Attempt to extract title from <strong>
        try:
            article_title = article.find_element(By.TAG_NAME, "strong").text.strip()
        except Exception:
            article_title = ""
        
        # If title is empty, skip this article
        if not article_title:
            continue

        article_link = article.get_attribute("href")
        if article_link:
            # Open the article in a new tab
            original_window = driver.current_window_handle
            driver.execute_script("window.open(arguments[0]);", article_link)
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)  # Wait for the article page to load

            try:
                # Extract the full article content using the provided XPath
                content_element = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[2]/div/main/div/div/div/div[5]")
                article_content = content_element.text.strip()
            except Exception as e:
                print(f"Error extracting content from {article_link}: {e}")
                article_content = ""
            
            # Close the new tab and switch back to the original window
            driver.close()
            driver.switch_to.window(original_window)
            
            # Add the article only if there is content
            if article_content:
                code["articles"].append({
                    "title": article_title,
                    "content": article_content,
                    "link": article_link
                })

    print(f"Extracted {len(code['articles'])} articles from {code['name']}.")

# Step 4: Save extracted data to a JSON file
with open("codes_and_articles.json", "w", encoding="utf-8") as f:
    json.dump(codes, f, indent=4, ensure_ascii=False)

print("✅ Data extraction completed and saved to codes_and_articles.json")

# Close the browser
driver.quit()
