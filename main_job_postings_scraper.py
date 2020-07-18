from lxml import html
import csv, os, json
import requests
from time import sleep
import sys
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

from scraper_job_postings import *





driver_path = "C:\\Users\\kkari\\Desktop\\LinkedIn_extractor\\chromedriver.exe"
# browser = webdriver.Chrome(driver_path)
browser = webdriver.Chrome(ChromeDriverManager().install())

browser.get('https://www.linkedin.com/jobs')

sleep(random_time(2,5)) #Waiting to load the page above


input_element_list = browser.find_elements_by_tag_name('input')

initial_search_parameters(job_title = 'Business Intelligence', location='United States', ele_list=input_element_list)

#---------------------------------------------SEARCH PART FINISHED---------------------------------------------#

job_count_list=[0]


while len(job_count_list)< 3 or max(job_count_list)< 2000:
    try:
        see_more_jobs_ele = browser.find_element_by_class_name('see-more-jobs')
        job_count = see_more(see_more_jobs_ele, browser)
        job_count_list.append(job_count)

        if job_count_list[-1]==job_count_list[-2] and job_count_list[-3] == job_count_list[-1]:
            break
        else:
            continue
    except:
        last_height = browser.execute_script("return document.body.scrollHeight")
        while True:
            SCROLL_PAUSE_TIME = random.uniform(0.5,2)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            job_count = scroll_more(browser)
            job_count_list.append(job_count)
            sleep(SCROLL_PAUSE_TIME)
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        if job_count_list[-1]==job_count_list[-2]:
            break
        else:
            continue



print("No of jobs available: {}".format(max(job_count_list)))


#---------------------------------------------LOADING ALL JOBS FINISHED---------------------------------------------#


ele_list = pre_elements_processing(browser) #fetched all the required elements

#Actual scraping starts:
df_main = pd.DataFrame()

for ele in ele_list:
    try:
        sleep(random_time(2, 5))
        ele.click()
        sleep(random_time(5, 7))
        df_job = fetch_data(browser)
        df_main = df_main.append(df_job)

        if len(df_main)>=10:
            print("Length of DF Main = {}".format(df_main.shape[0]))
            write_to_database_job_details(df_main)
            df_main = df_main.iloc[0:0]
            print("DF reset complete")
        else:
            print("Length of DF Main = {}".format(df_main.shape[0]))



    except StaleElementReferenceException:
        print("Loading Element Failed. Moving on to new Element.")
        continue

print("Final Main dataframe: {}" .format(df_main.shape))
write_to_database_job_details(df_main)
print(df_main)

browser.quit()