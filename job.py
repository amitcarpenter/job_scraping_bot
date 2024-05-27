import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pymongo import MongoClient, errors
from datetime import datetime
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By



app = Flask(__name__)

def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["job_scraping"]
    return db

def get_collection(db, collection_name):
    return db[collection_name]

def initiate_browser():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')  # Disable GPU
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        print("Chrome driver created successfully.")
        return driver
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# def scrape_jobs(driver, url, collection, processed_urls):
#     driver.get(url)

#     sleep(3)
#         # Get the initial height of the page
#     last_height = driver.execute_script("return document.body.scrollHeight")

#     while True:
#         # Scroll down to bottom
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#         # Wait to load page
#         sleep(3)

#         # Calculate new height and compare with the last height
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height
#         sleep(2)

#     soup = BeautifulSoup(driver.page_source, 'html.parser')

#     job_divs = soup.find_all('li', class_='iFjolb gws-plugins-horizon-jobs__li-ed')

#     print()

#     for job_div in job_divs:
#         job_title = job_div.find('div', class_='BjJfJf PUpOsf').text if job_div.find('div', class_='BjJfJf PUpOsf') else 'N/A'
#         company_name = job_div.find('div', class_='vNEEBe').text if job_div.find('div', class_='vNEEBe') else 'N/A'
#         location = job_div.find_all('div', class_='Qk80Jf')[0].text if len(job_div.find_all('div', class_='Qk80Jf')) > 0 else 'N/A'
#         salary = job_div.find('span', {'aria-label': True, 'aria-hidden': 'true'}).text if job_div.find('span', {'aria-label': True, 'aria-hidden': 'true'}) else 'N/A'
#         employment_type = job_div.find('span', {'aria-label': True, 'aria-hidden': 'true'}).find_next_sibling().text if job_div.find('span', {'aria-label': True, 'aria-hidden': 'true'}) else 'N/A'
#         job_url = job_div.find('a', class_='a-no-hover-decoration')['href']

#         scraped_data = {
#             "job_title": job_title,
#             "company_name": company_name,
#             "location": location,
#             "salary": salary,
#             "employment_type": employment_type,
#             "job_url": job_url,
#             "scraped_date": datetime.now()
#         }

#         if job_url not in processed_urls:
#             try:
#                 collection.insert_one(scraped_data)
#                 processed_urls.add(job_url)
#             except errors.DuplicateKeyError:    
#                 print(f"Skipping duplicate URL during MongoDB insertion: {job_url}")

#         print("-" * 40)



def scrape_jobs(driver, url, collection, processed_urls):
    driver.get(url)
    sleep(3)

    # Get the initial height of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for a certain element to be visible indicating that more content has loaded
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "gws-plugins-horizon-jobs__li-ed"))
            )
        except:
            break

        # Calculate new height and compare with the last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Once all job listings are loaded, proceed with scraping
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_divs = soup.find_all('li', class_='iFjolb gws-plugins-horizon-jobs__li-ed')

    for job_div in job_divs:
        job_title = job_div.find('div', class_='BjJfJf PUpOsf').text.strip()
        company_name = job_div.find('div', class_='vNEEBe').text.strip()
        location = job_div.find('div', class_='Qk80Jf').text.strip()
        salary = job_div.find('div', class_='LL4CDc').text.strip()
        employment_type = job_div.find_all('div', class_='LL4CDc')[-1].text.strip()
        job_url = job_div.find('a', class_='a-no-hover-decoration')['href']

        scraped_data = {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "salary": salary,
            "employment_type": employment_type,
            "job_url": job_url,
            "scraped_date": datetime.now()
        }

        if job_url not in processed_urls:
            try:
                collection.insert_one(scraped_data)
                processed_urls.add(job_url)
            except errors.DuplicateKeyError:    
                print(f"Skipping duplicate URL during MongoDB insertion: {job_url}")

        print("-" * 40)



def main():
    db = connect_to_mongodb()
    collection = get_collection(db, "job_listings")
    processed_urls = set()
    collection.create_index([('job_url', 1)], unique=True)

    # target_url = "https://www.google.com/search?q=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&rlz=1C1RXQR_en-GBIN1081IN1081&oq=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&gs_lcrp=EgZjaHJvbWUyBggAEEUYOdIBCDI2MDhqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"
    target_url = "https://www.google.com/search?q=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&rlz=1C1RXQR_en-GBIN1081IN1081&oq=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg70gEHMjAwajBqN6gCALACAA&sourceid=chrome&ie=UTF-8&ibp=htl;jobs&sa=X&ved=2ahUKEwiUkMHY262GAxV7yTgGHehHCRIQudcGKAF6BAgYECg&sxsrf=ADLYWIIdBidCDHdd4l72HA_-9qSG8BrxHQ:1716808940806#htivrt=jobs&htidocid=y6ctJpHJUXfFntQNAAAAAA%3D%3D&fpstate=tldetail"
    
    driver = initiate_browser()
    if driver:
        scrape_jobs(driver, target_url, collection, processed_urls)
        driver.quit()

@app.route('/show_jobs', methods=['GET'])
def show_jobs():
    db = connect_to_mongodb()
    collection = get_collection(db, "job_listings")
    jobs = list(collection.find({}, {'_id': 0}))
    return jsonify(jobs)

if __name__ == "__main__":
    main()
    app.run(port=5000, debug=False)
