import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime,timedelta
import re

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.naukri.com/")

find = None

job_titles = []
company_names = []
locations = []
links = []
experience = []
post_dates = []
MAX_PAGES = 5
page_count = 0

last_date = datetime.now() - timedelta(days=7)

def search():
    global find
    find = input('Enter job field: ')
    search = driver.find_element(By.CLASS_NAME, value="suggestor-input")
    search.send_keys(f'{find}', Keys.ENTER)
    time.sleep(3)
    sort_button = driver.find_element(By.ID, 'filter-sort')
    sort_button.click()
    time.sleep(2)
    date_sort = driver.find_element(By.XPATH, '/html/body/div/div/main/div[1]/div[2]/div[1]/div[2]/span/div/ul/li[2]/a')
    date_sort.click()
    time.sleep(3)
    print(f"{find} jobs are now processing....")





def get_jobs():
    global job_titles,company_names,locations,experience,links,post_dates, last_date

    # THIS WILL FIND THE JOB TITLE AND IGNORE THE PROMOTIONAL CONTENT'S JOB TITLES
    get_divs = driver.find_elements(By.CLASS_NAME, "srp-jobtuple-wrapper")

    for div in get_divs:
        try:
            title = div.find_element(By.CLASS_NAME, 'title')
            name = div.find_element(By.CLASS_NAME,value='comp-name')
            loc = driver.find_element(By.CLASS_NAME, value='locWdth')
            exp = driver.find_element(By.CLASS_NAME, value='expwdth')
            date_text = driver.find_element(By.CLASS_NAME, value='job-post-day ').text

            try:
                if date_text == 'Just Now' or date_text == 'Few Hours Ago':
                    posted_date = datetime.now()
                elif 'Days' in date_text or 'Day' in date_text:
                    if '+' in date_text:
                        days_ago = re.findall(r'\d+', date_text)
                    days_ago = int(date_text.split(' ')[0])
                    posted_date = datetime.now() - timedelta(days=days_ago)
                else:
                    posted_date = datetime.strptime(date_text, '%d %b %Y')

            except Exception as e:
                print(f"Error while parsing date: {e}")
                continue

            if posted_date >= last_date:
                job_titles.append(title.text)
                company_names.append(name.text)
                locations.append(loc.text)
                experience.append(exp.text)
                link = title.get_attribute('href')
                links.append(link)
                post_dates.append(posted_date.strftime('%Y-%m-%d'))


        except Exception as e:
            print(f'Error processing job listing: {e}')
            continue


    try:
            next_btn = driver.find_element(By.XPATH,'/html/body/div/div/main/div[1]/div[2]/div[3]/div/a[2]')
            if 'disabled' not in next_btn.get_attribute('class'):
                next_btn.click()
                time.sleep(4)
            else:
                return False
    except Exception as e:
            print(f"Error while navigating page{e}")
            return False
    return True

def export_csv():
    with open(f'{find}.csv','w',newline='',encoding='utf-8') as file:
        writer= csv.writer(file)
        writer.writerow(["Job Title", "Company Name", "Location", "Experience", "Link", "Posted Date"])
        for i in range(len(job_titles)):
            writer.writerow([job_titles[i], company_names[i], locations[i], experience[i], links[i], post_dates[i]])


search()

on = True
while on:
    get_jobs()
    if not job_titles:
        print(f'No results for {find} found!!')
        on = False
    page_count += 1
    if page_count >= MAX_PAGES:
        export_csv()
        print(f"Data exported to {find}.csv successfully.")
        on = False


driver.quit()




