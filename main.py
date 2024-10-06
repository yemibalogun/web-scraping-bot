from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import time
import datetime

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless") # Run in headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.90 Safari/537.36")
    
# Initialize Chrome WebDriver using webdriver-manager
service = Service(ChromeDriverManager().install(), port=50223)
driver = webdriver.Chrome(service=service, options=chrome_options)
    
def scrape_product_data(url):
    driver.get(url)
    
    # Wait for the page to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, "productTitle")))
        product_name = driver.find_element(By.ID, "productTitle").text.strip()
    except Exception as e:
        product_name = "Product title not found"
        
    # Find product price
    try:
        price = driver.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
    except:
        price = "Price not found"
    
    driver.quit()
    return {"name": product_name, "price": price}

def collect_price_data(url, days):
    prices = []
    for _ in range(days):
        data = scrape_product_data(url)
        try:
            prices.append(float(data['price']))
        except ValueError:
            prices.append(np.nan) # If the price is not found, append NaN for missing data
        time.sleep(1) # Wait between requests to avoid being blocked
    return prices

# Simulating data collection for 30 days
url = "https://www.amazon.com/BOSGAME-B100-Windows-Computers-SO-DIMM/dp/B0CLV98PSH/ref=sr_1_2_sspa?crid=HF02ZOUNS43Z&dib=eyJ2IjoiMSJ9.aes0YWBS4Yqq1s4k3qFltv-5Y5kvIv2q8fXt4jd7hxKzuqlEkmpvEq9Hb-lw94khkAn4aRW8Y3pMEhufELQftXHqFkotCV2OCE4V5hkL6PrztfpOi5bJSEngiu1lPRZiyaEyspodazwolzyydXDeiliOT7jNOfTdIQ1W3a8tE1J4Oir9MMGdjUvmz76KgmGrCZHM6T9bo2yXJCoc-WHDg-iDQWTqhwex1R7vH0E6vdzbA00zEs0ngIxPuogZnuVv9irYH_XO6jSYaUvi8_SbBhtCW-d4dpYML4V6-Ipt-N4.22Orx_XFM2BdnyEbuPwy1-CqOjddduWseslwQCTo-NQ&dib_tag=se&keywords=mini%2Bpc&qid=1728148602&s=amazon-devices&sprefix=mini%2Bpc%2Camazon-devices%2C524&sr=1-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
prices = collect_price_data(url, 30)

# Handle missing values by forward filling
prices = pd.Series(prices).fillna(method='ffill').tolist()

# Create a pandas DataFrame with dates
date_rng = pd.date_range(start=datetime.datetime.now() - pd.Timedelta(days=29), periods=30, freq='D')
df = pd.DataFrame(data=prices, index=date_rng, columns=['Price'])

# Fit ARIMA model
model = ARIMA(df['Price'], order=(1,1,1))
results = model.fit()

# Make predictions
forecast = results.forecast(steps=7)

# Plot the results
plt.figure(figsize=(12,6))
plt.plot(df.index, df['Price'], label='Observed')
plt.plot(pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=7, freq='D'),
         forecast, color='red', label='Forecast')
plt.title('Price Forecast')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.savefig("price_forecast.png") # Save the plot as an image
plt.show()

# Print the forecasted prices
print("Forecasted prices for the next 7 days:")
for date, price in zip(pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=7, freq='D'), forecast):
    print(f"{date.date()}: ${price:.2f}")
    
# Calculate error metrics using the last 7 observed values (if available)
if len(df['Price']) >= 14:
    actual = df['Price'][-7:].values
    predicted = results.forecast(steps=7)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    print(f"\nRoot Mean Squared Error: ${rmse:.2f}")
else:
    print("\nNot enough data points to calcuate error metrics.")
    

# def order_item(driver, product_url):
#     driver.get(product_url)
    
#     # Add the product to cart
#     add_to_cart_button = driver.find_element(By.ID, "add-to-cart-button")
#     add_to_cart_button.click()
#     time.sleep(4)
    
#     # Proceed to checkout
#     checkout_button = driver.find_element(By.NAME, "proceedToRetailCheckout")
#     checkout_button.click()
#     time.sleep(3)
    
#     # Fill out the necessary fields at checkout
#     address_field = driver.find_element(By.NAME, "shipping-address")
#     payment_method_field = driver.find_element(By.NAME, "payment-method")
    
#     # Submit the order 
#     submit_order_button = driver.find_element(By.ID, "submit-order")
#     submit_order_button.click()
    
# # Example usage

    
    
# # Test the scraping function
# url = "https://www.amazon.com/BOSGAME-B100-Windows-Computers-SO-DIMM/dp/B0CLV98PSH/ref=sr_1_2_sspa?crid=HF02ZOUNS43Z&dib=eyJ2IjoiMSJ9.aes0YWBS4Yqq1s4k3qFltv-5Y5kvIv2q8fXt4jd7hxKzuqlEkmpvEq9Hb-lw94khkAn4aRW8Y3pMEhufELQftXHqFkotCV2OCE4V5hkL6PrztfpOi5bJSEngiu1lPRZiyaEyspodazwolzyydXDeiliOT7jNOfTdIQ1W3a8tE1J4Oir9MMGdjUvmz76KgmGrCZHM6T9bo2yXJCoc-WHDg-iDQWTqhwex1R7vH0E6vdzbA00zEs0ngIxPuogZnuVv9irYH_XO6jSYaUvi8_SbBhtCW-d4dpYML4V6-Ipt-N4.22Orx_XFM2BdnyEbuPwy1-CqOjddduWseslwQCTo-NQ&dib_tag=se&keywords=mini%2Bpc&qid=1728148602&s=amazon-devices&sprefix=mini%2Bpc%2Camazon-devices%2C524&sr=1-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1"
# product_data = scrape_product_data(url)
# print(product_data)
