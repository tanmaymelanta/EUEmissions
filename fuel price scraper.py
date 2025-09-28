from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os

# ===== Setup for headless Chrome =====
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

# ===== Start Scraping =====
driver.get("https://shipandbunker.com/prices/av/region")

# Locate the table
table = driver.find_element(By.XPATH, '//*[@id="portsTable_625-"]')

# Extract headers
headers = []
header_elements = table.find_elements(By.XPATH, ".//thead/tr/th")
for header in header_elements:
    text = header.text.strip()
    headers.append(text if text else "Date")

# Extract data rows
data = []
rows = table.find_elements(By.XPATH, ".//tbody/tr")
for row in rows:
    row_data = []

    # Port name
    port_element = row.find_element(By.XPATH, ".//th/a")
    row_data.append(port_element.text.strip())

    # Prices
    price_cells = row.find_elements(By.XPATH, ".//td[contains(@class, 'price')]")
    for cell in price_cells:
        price = cell.find_element(By.CLASS_NAME, "quote").text.strip()
        row_data.append(price)

    # Date
    date_cell = row.find_element(By.XPATH, ".//td[contains(@class, 'date')]")
    row_data.append(date_cell.text.strip())

    data.append(row_data)

driver.quit()

# ===== Save data =====
os.makedirs("data", exist_ok=True)  # Create folder if not exists
file_path = os.path.join("data", "bunker_prices.csv")

with open(file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(data)

print(f"Scraping complete. Data saved to {file_path}")
