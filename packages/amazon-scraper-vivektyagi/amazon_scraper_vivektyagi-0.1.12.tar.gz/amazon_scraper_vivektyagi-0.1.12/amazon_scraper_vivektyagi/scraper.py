import os
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _setup_driver(headless: bool = False):
    """Setup Chrome WebDriver with user profile and optional headless mode."""
    USER_DATA_DIR = os.path.join(os.getcwd(), "chrome-user-data")
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--start-maximized")

    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(options=chrome_options)


def extract_bsr(soup):
    """Extract Parent & Child Best Sellers Rank from page."""
    parent_rank = "NA"
    child_rank = "NA"

    # Method 1: structured product details tables
    possible_tables = soup.select("#productDetails_detailBullets_sections1, #productDetails_db_sections")
    for table in possible_tables:
        text = table.get_text(" ", strip=True)
        match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", text)
        if match:
            if len(match) >= 1:
                parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
            if len(match) >= 2:
                child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
            return parent_rank, child_rank

    # Method 2: detail bullets wrapper
    detail_bullets = soup.select("#detailBulletsWrapper_feature_div")
    for section in detail_bullets:
        text = section.get_text(" ", strip=True)
        match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", text)
        if match:
            if len(match) >= 1:
                parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
            if len(match) >= 2:
                child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
            return parent_rank, child_rank

    # Method 3: fallback - search entire page
    full_text = soup.get_text(" ", strip=True)
    match = re.findall(r"#([\d,]+)\s+in\s+([^(]+)", full_text)
    if match:
        if len(match) >= 1:
            parent_rank = f"#{match[0][0]} in {match[0][1].strip()}"
        if len(match) >= 2:
            child_rank = f"#{match[1][0]} in {match[1][1].strip()}"
    return parent_rank, child_rank


def _scrape_product_details(driver, asin, country_code):
    url = f"https://www.amazon.{country_code}/dp/{asin}"
    driver.get(url)
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    def safe_find(selector, attr=None):
        tag = soup.select_one(selector)
        if tag:
            return tag.get(attr) if attr else tag.get_text(strip=True)
        return 'N/A'

    # Basic product info
    title = safe_find('#productTitle')
    price = 'N/A'
    currency = ''
    price_block = soup.select_one('.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay')
    if not price_block:
        price_block = soup.select_one('.a-price')  # fallback
    
    if price_block:
        # Case 1: Regular "offscreen" format
        offscreen = price_block.select_one('.a-offscreen')
        if offscreen and re.search(r'[\d]', offscreen.get_text()):
            price = offscreen.get_text(strip=True)
        else:
            # Case 2: Separate whole + fraction parts (common on Amazon US)
            symbol = price_block.select_one('.a-price-symbol')
            whole = price_block.select_one('.a-price-whole')
            fraction = price_block.select_one('.a-price-fraction')

            whole_text = whole.get_text(strip=True).replace('.', '') if whole else ''
            fraction_text = fraction.get_text(strip=True) if fraction else ''
            
            if whole_text:
                price = f"{whole_text}.{fraction_text}" if fraction_text else whole_text

    # ---- Clean and normalize only number ----
    price = re.sub(r'[^0-9.,]', '', price).strip()
    if re.search(r'\d+,\d{2}$', price):  # convert comma decimal to dot
        price = price.replace(',', '.')

    # Remove extra commas (thousand separators like 1,299.00 → 1299.00)
    price = price.replace(',', '')

    # Convert to float safely
    try:
        price = str(float(price))
    except:
        price = 'N/A'
    # ---------------------------------------        
    rating_tag = soup.select_one('#acrPopover')
    rating = rating_tag['title'] if rating_tag and 'title' in rating_tag.attrs else 'N/A'
    reviews = safe_find('#acrCustomerReviewText')
    image = safe_find('#landingImage', 'src')
    if reviews != 'N/A':
        reviews = ''.join(filter(str.isdigit, reviews))

    # Brand
    brand_tag = soup.find("a", id="bylineInfo")
    if not brand_tag:
        brand_tag = soup.find("tr", string=lambda t: t and "Brand" in t)
        if brand_tag:
            brand_tag = brand_tag.find_next("td")
    brand = brand_tag.get_text(strip=True) if brand_tag else "Not Found"

    # BSR
    parent_rank, child_rank = extract_bsr(soup)

    # Product Description
    product_desc_section = soup.find(id="productDescription")
    product_desc_available = "Yes" if product_desc_section else "NA"

    # From the Manufacturer
    from_manufacturer_section = soup.find(lambda tag: tag.name in ["h2", "h3"] and "From the manufacturer" in tag.get_text())
    from_manufacturer_available = "Yes" if from_manufacturer_section else "NA"
    
        # Bought in past month (robust approach)
    bought = "N/A"
    try:
        # Wait until "in past month" appears
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(., 'in past month')]"))
        )

        # Locate the suffix span
        suffix_elems = driver.find_elements(By.XPATH, "//span[contains(., 'in past month')]")
        if suffix_elems:
            parent = suffix_elems[0].find_element(By.XPATH, "./..")  # go to parent <span>
            bold_elem = parent.find_element(By.CSS_SELECTOR, "span.a-text-bold")
            if bold_elem:
                bought_text = bold_elem.text.strip()  # e.g., "6K+ bought"
                bought_raw = bought_text.split()[0].replace("+", "").upper()

                if "K" in bought_raw:
                    bought = str(int(float(bought_raw.replace("K", "")) * 1000))
                elif "M" in bought_raw:
                    bought = str(int(float(bought_raw.replace("M", "")) * 1000000))
                else:
                    bought = str(int(bought_raw))
    except Exception as e:
        print(f"[DEBUG] Bought extraction failed for {asin}")
        bought = "N/A"

    return {
        'ASIN': asin,
        'Title': title,
        'Price': price,
        'Bought': bought,
        'Rating': rating,
        'Reviews': reviews,
        'Image': image,
        'Brand': brand,
        'Parent_Category_Rank': parent_rank,
        'Child_Category_Rank': child_rank,
        'Product_Description': product_desc_available,
        'From_Manufacturer': from_manufacturer_available
    }


def get_amazon_product_details(asin, country_code="in", headless=False):
    driver = _setup_driver(headless=headless)
    try:
        return _scrape_product_details(driver, asin, country_code)
    finally:
        driver.quit()


def get_multiple_product_details(asin_list, country_code="in", delay=5, headless=False):
    driver = _setup_driver(headless=headless)
    results = []
    try:
        for asin in asin_list:
            try:
                data = _scrape_product_details(driver, asin, country_code)
                results.append(data)
                print(f" Scraped: {asin}")
            except Exception as e:
                print(f" Failed {asin}: {e}")
                results.append({'ASIN': asin})
            time.sleep(delay)
    finally:
        driver.quit()
    return results

