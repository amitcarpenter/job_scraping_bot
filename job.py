# import requests
# from bs4 import BeautifulSoup
# from flask import Flask, jsonify
# from selenium.webdriver.chrome.options import Options
# from selenium import webdriver
# from pymongo import MongoClient, errors
# from datetime import datetime
# from time import sleep
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from flask import Flask, jsonify, render_template



# app = Flask(__name__)

# def connect_to_mongodb():
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["job_scraping_new"]
#     return db

# def get_collection(db, collection_name):
#     return db[collection_name]

# # def initiate_browser():
# #     try:
# #         chrome_options = Options()
# #         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
# #         # chrome_options.add_argument('--headless')
# #         # chrome_options.add_argument('--no-sandbox')
# #         # chrome_options.add_argument('--disable-dev-shm-usage')
# #         # chrome_options.add_argument('--disable-gpu')  # Disable GPU
# #         driver = webdriver.Chrome(options=chrome_options)
# #         driver.maximize_window()
# #         print("Chrome driver created successfully.")
# #         return driver
# #     except Exception as e:
# #         print(f"An error occurred: {e}")
# #         return None

# def initiate_browser():
#     # Log before creating the driver
#     # display = Display(visible=0, size=(800, 600))
#     # display.start()
#     # chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--no-sandbox')
#     # chrome_options.add_argument('--headless')
#     chrome_options = Options()
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     driver = webdriver.Chrome(options=chrome_options)

#     driver.maximize_window()

#     # Log after creating the driver
#     print("Chrome driver created successfully.")
#     return driver



# def scrape_jobs(driver, url, collection, processed_urls):
#     driver.get(url)

#     sleep(15)
#     soup = BeautifulSoup(driver.page_source, 'html.parser')
#     job_divs = soup.find_all('li', class_='iFjolb gws-plugins-horizon-jobs__li-ed')

#     # Iterate over job divs
#     for job_div in job_divs:
#         try:
#             job_title = job_div.find('div', class_='BjJfJf PUpOsf').text.strip()
#         except AttributeError:
#             job_title = "N/A"
        
#         try:
#             company_name = job_div.find('div', class_='vNEEBe').text.strip()
#         except AttributeError:
#             company_name = "N/A"
        
#         try:
#             location = job_div.find('div', class_='Qk80Jf').text.strip()
#         except AttributeError:
#             location = "N/A"
        
#         try:
#             salary = job_div.find('div', class_='LL4CDc').text.strip()
#         except AttributeError:
#             salary = "N/A"
        
#         try:
#             employment_type = job_div.find_all('div', class_='LL4CDc')[-1].text.strip()
#         except (AttributeError, IndexError):
#             employment_type = "N/A"
        
#         try:
#             job_url = job_div.find('a', class_='a-no-hover-decoration')['href']
#         except (AttributeError, TypeError):
#             job_url = "N/A"

#         scraped_data = {
#             "job_title": job_title,
#             "company_name": company_name,
#             "location": location,
#             "salary": salary,
#             "employment_type": employment_type,
#             "job_url": job_url,
#             "scraped_date": datetime.now()
#         }
#         if company_name not in processed_urls:
#             try:
#                 collection.insert_one(scraped_data)
#                 processed_urls.add(company_name)
#             except errors.DuplicateKeyError:    
#                 print(f"Skipping duplicate URL during MongoDB insertion: {company_name}")

#         print("-" * 40)



# def main():
#     db = connect_to_mongodb()
#     collection = get_collection(db, "job_listings")
#     processed_urls = set()
#     collection.create_index([('company_name', 1)], unique=True)

#     target_url = "https://www.google.com/search?q=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&rlz=1C1RXQR_en-GBIN1081IN1081&oq=IT+jobs+near+Indore+Madhya+Pradesh+in+IT+companies+Node+OR+js&gs_lcrp=EgZjaHJvbWUqBggAEEUYOzIGCAAQRRg70gEHMjAwajBqN6gCALACAA&sourceid=chrome&ie=UTF-8&ibp=htl;jobs&sa=X&ved=2ahUKEwiUkMHY262GAxV7yTgGHehHCRIQudcGKAF6BAgYECg&sxsrf=ADLYWIIdBidCDHdd4l72HA_-9qSG8BrxHQ:1716808940806#htivrt=jobs&htidocid=y6ctJpHJUXfFntQNAAAAAA%3D%3D&fpstate=tldetail"
    
#     driver = initiate_browser()
#     if driver:
#         scrape_jobs(driver, target_url, collection, processed_urls)
#         driver.quit()

# @app.route('/show_jobs', methods=['GET'])
# def show_jobs():
#     db = connect_to_mongodb()
#     collection = get_collection(db, "job_listings")
#     jobs = list(collection.find({}, {'_id': 0}))
#     return jsonify(jobs)



# @app.route('/jobs', methods=['GET'])
# def show_jobs():
#     jobs = scrape_jobs()
#     return render_template('jobs.html', jobs=jobs)


# if __name__ == "__main__":
#     # main()
#     app.run(port=5000, debug=False)



import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from pymongo import MongoClient, errors
from datetime import datetime
from time import sleep

app = Flask(__name__)

# Function to connect to MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["job_scraping_new"]
    return db

# Function to get a collection from MongoDB
def get_collection(db, collection_name):
    return db[collection_name]

# Function to scrape jobs and save them to MongoDB
def scrape_jobs(driver, url, collection, processed_urls):
    driver.get(url)
    sleep(15)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_divs = soup.find_all('li', class_='iFjolb gws-plugins-horizon-jobs__li-ed')

    # Iterate over job divs
    for job_div in job_divs:
        try:
            job_title = job_div.find('div', class_='BjJfJf PUpOsf').text.strip()
        except AttributeError:
            job_title = "N/A"
        
        try:
            company_name = job_div.find('div', class_='vNEEBe').text.strip()
        except AttributeError:
            company_name = "N/A"
        
        try:
            location = job_div.find('div', class_='Qk80Jf').text.strip()
        except AttributeError:
            location = "N/A"
        
        try:
            salary = job_div.find('div', class_='LL4CDc').text.strip()
        except AttributeError:
            salary = "N/A"
        
        try:
            employment_type = job_div.find_all('div', class_='LL4CDc')[-1].text.strip()
        except (AttributeError, IndexError):
            employment_type = "N/A"
        
        try:
            job_url = job_div.find('a', class_='a-no-hover-decoration')['href']
        except (AttributeError, TypeError):
            job_url = "N/A"

        scraped_data = {
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "salary": salary,
            "employment_type": employment_type,
            "job_url": job_url,
            "scraped_date": datetime.now()
        }
        
        # Check if the company name already exists in processed URLs
        if company_name not in processed_urls:
            try:
                collection.insert_one(scraped_data)
                processed_urls.add(company_name)
            except errors.DuplicateKeyError:    
                print(f"Skipping duplicate URL during MongoDB insertion: {company_name}")

        print("-" * 40)

# Route to display jobs as JSON
@app.route('/show_jobs', methods=['GET'])
def show_jobs_json():
    db = connect_to_mongodb()
    collection = get_collection(db, "job_listings")
    jobs = list(collection.find({}, {'_id': 0}))
    return jsonify(jobs)

# Route to display jobs as HTML table
@app.route('/show_jobs_html', methods=['GET'])
def show_jobs_html():
    db = connect_to_mongodb()
    collection = get_collection(db, "job_listings")
    jobs = list(collection.find({}, {'_id': 0}))
    return render_template('jobs.html', jobs=jobs)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
