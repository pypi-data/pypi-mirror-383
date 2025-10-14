#amazon_scraper

A simple and powerful multi-country Amazon product scraper built using Python and Selenium.
It fetches product details like Title, Price, Bought, Rating, Reviews, Image URL, Brand, Category Ranks, and checks for Product Description and From the Manufacturer sections using ASINs.

##🚀 Features

🌍 Scrape from any Amazon marketplace by passing country_code (e.g., in, us, ae, uk)
🔍 Fetch detailed product info:
Title
Price
Bought
Rating
Reviews
Image URL
Brand
Parent Category Rank
Child Category Rank
Product Description Available
From the Manufacturer Available

📦 Supports single or multiple ASINs
🧼 Automatically handles browser setup and teardown
💡 Lightweight and easy to use

##📦 Installation
###From PyPI:
pip install amazon-scraper-vivektyagi

💻 Usage
Scrape a single product
from amazon_scraper_vivektyagi import get_amazon_product_details

data = get_amazon_product_details("B0C1234567", country_code="in")
print(data)

Scrape multiple products

from amazon_scraper_vivektyagi import get_multiple_product_details
asins = ["B0C1234567", "B0D7654321"]
results = get_multiple_product_details(asins, country_code="ae")

for product in results:
    print(product)

✅ Output Format
{
    'ASIN': 'B0C1234567',
    'Title': 'Sample Product Title',
    'Price': '₹1,299.00',
    'Bought':'200',
    'Rating': '4.3 out of 5 stars',
    'Reviews': '345',
    'Image': 'https://m.media-amazon.com/images/I/xxxxx.jpg',
    'Brand': 'Sample Brand',
    'Parent_Category_Rank': '#12 in Electronics',
    'Child_Category_Rank': '#1 in Headphones',
    'Product_Description': 'Yes',
    'From_Manufacturer': 'No'
}

📄 Requirements
Python 3.6 or higher
Google Chrome installed
ChromeDriver (auto-installed via webdriver-manager)

Install dependencies:
pip install selenium beautifulsoup4 webdriver-manager


👤 Author
Vivek Tyagi

📄 License
This project is licensed under the MIT License.

⚠️ Disclaimer
This tool is for educational purposes only.
Scraping Amazon may violate their Terms of Service. Use responsibly.