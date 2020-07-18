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
from selenium.common.exceptions import *

from database import *


def random_time(a,b):
    rand_time = random.randint(a,b)
    return rand_time


def initial_search_parameters(job_title, location, ele_list):


    for ele in ele_list:
        data_control_name = ele.get_attribute('data-tracking-control-name')
        field_name = ele.get_attribute('name')
        if data_control_name == 'homepage-jobseeker_dismissable-input':
            if field_name == 'keywords':
                job_title_field_ele = ele
            elif field_name == 'location':
                location_field = ele
    # Entering values into the fields and enter
    input_values(job_title_field_ele, job_title)

    input_values(location_field, location)

    location_field.send_keys(Keys.ENTER)

def input_values(field_element, input_value):

    field_element.send_keys(Keys.CONTROL+"a")
    field_element.send_keys(Keys.DELETE)
    field_element.send_keys(input_value)

# ---------------------------------------------SEARCH PART FINISHED---------------------------------------------#


def no_jobs_loaded(browser):
    ele_list = browser.find_elements_by_class_name('result-card')
    no_jobs=[]
    for ele in ele_list:
        if ele.get_attribute('data-row') is None:
            no_jobs.append(0)
        else:
            no_jobs.append(int(ele.get_attribute('data-row')))
#     print(max(no_jobs))
    return max(no_jobs)

def see_more(ele, browser):
    if ele.text == 'See more jobs':
        ele.click()
        print('clicked SEE MORE JOBS:', end=' ')
        sleep(random_time(3, 7)) #Let the program sleep while the page loads

        job_count = no_jobs_loaded(browser)
        print(job_count)

        return  job_count

def scroll_more(browser):
     # Let the program sleep while the page loads

    job_count = no_jobs_loaded(browser)
    print(job_count)

    return job_count
 # ---------------------------------------------LOADING ALL JOBS FINISHED---------------------------------------------#




def pre_elements_processing(browser):
    exclude_list=['1732464600']
    sql_0 = "SELECT job_id FROM job_details_l3;"
    df_db_existing = read_sql_server(sql_0)
    print("# of Records loaded from DATABASE = {}".format(df_db_existing.shape[0]))

    job_ids_list_elements = browser.find_elements_by_class_name('result-card')

    scraped_data_df = pd.DataFrame()

    for job_id_ele in job_ids_list_elements:
        job_link_full_element = job_id_ele.find_element_by_class_name('result-card__full-card-link')
        if job_id_ele.get_attribute('data-id') in exclude_list:
            continue
        else:
            result_dict = {
                "job_id": job_id_ele.get_attribute('data-id'),
                "job_ele": job_link_full_element
            }
            scraped_data_df = scraped_data_df.append(pd.DataFrame([result_dict]))


    scraped_data_df = scraped_data_df.drop_duplicates(subset='job_id', keep="first")
    print("Removed duplicates. New Shape: {}".format(scraped_data_df.shape))

    scraped_data_df = scraped_data_df[scraped_data_df['job_id'].isin(df_db_existing['job_id']) == False]
    print("Database Validation Complete. Final Shape: {}".format(scraped_data_df.shape))

    ele_list = list(scraped_data_df['job_ele'])

    return ele_list


#------------------------------------------Loading all new elements Finished------------------------------------------#

def fetch_data(browser):
#Job ID
    def f_job_id():
        job_id_element = browser.find_element_by_class_name('job-card__contents--active')
        job_id = job_id_element.get_attribute('data-id')
        return job_id
#Job Title
    def f_job_title():
        try:
            job_title_ele = browser.find_element_by_class_name('topcard__title')
            job_title = job_title_ele.text
        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            job_title_ele = browser.find_element_by_class_name('topcard__title')
            job_title = job_title_ele.text

        if len(job_title) > 0:
            return job_title
        else:
            return None

#Company Name

    def f_job_company_name():
        try:
            job_company_name_ele = browser.find_element_by_class_name('topcard__org-name-link')
            job_company_name = job_company_name_ele.text

        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            # print('Company Name Element not found, sleeping for a while..!!------------------------->')
            job_company_name_ele = browser.find_element_by_class_name('topcard__org-name-link')
            job_company_name = job_company_name_ele.text

        except NoSuchElementException:
            # print('Company Name Element not found, trying with another element..!!------------------------->')
            # sleep(random_time(3, 5))
            job_company_name_ele = browser.find_element_by_class_name('topcard__flavor')
            job_company_name = job_company_name_ele.text

        if len(job_company_name) > 0:
            return job_company_name

        else:
            return None

#Company Location

    def f_job_company_location():
        try:
            job_company_loc_ele = browser.find_element_by_class_name('topcard__flavor--bullet')
            job_company_loc = job_company_loc_ele.text
        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            job_company_loc_ele = browser.find_element_by_class_name('topcard__flavor--bullet')
            job_company_loc = job_company_loc_ele.text
        except NoSuchElementException:
            # sleep(random_time(3, 5))
            # job_company_name_ele = browser.find_element_by_class_name('topcard__flavor')
            job_company_loc = "Not Found"
        if len(job_company_loc) > 0:
            return job_company_loc
        else:
            return None

#Posted Time
    def f_job_posted_time():
        try:
            job_posted_time_ele = browser.find_element_by_class_name('posted-time-ago__text')
            job_posted_time = job_posted_time_ele.text

        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            job_posted_time_ele = browser.find_element_by_class_name('posted-time-ago__text')
            job_posted_time = job_posted_time_ele.text

        except NoSuchElementException:
             job_posted_time = "Not Found"

        if len(job_posted_time)>0:
            return job_posted_time
        else:
            return None

#No of Applicants
    def f_job_no_applicants():
        try:
            job_no_applicants_ele = browser.find_element_by_class_name('num-applicants__caption')
            job_no_applicants = job_no_applicants_ele.text

        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            job_no_applicants_ele = browser.find_element_by_class_name('num-applicants__caption')
            job_no_applicants = job_no_applicants_ele.text

        except NoSuchElementException:
            job_no_applicants = "Not Found"

        if len(job_no_applicants) > 0:
            return job_no_applicants
        else:
            return job_no_applicants

#Apply Button Link
    def f_job_apply_button_link():
        job_id_element = browser.find_element_by_class_name('job-card__contents--active')
        job_id = job_id_element.get_attribute('data-id')
        job_apply_button_link = "https://www.linkedin.com/jobs/view/" + job_id + "/"
        print(job_apply_button_link)

        if len(job_apply_button_link) > 36:
            return job_apply_button_link
        else:
            return None

# Job Criteria
    def f_job_criteria():
        try:
            job_criteria_item = browser.find_elements_by_class_name('job-criteria__item')

            seniority_level = None
            employment_type = None
            job_function = None
            industries = None

            for field in job_criteria_item:
                #     print(field.text)
                job_criteria_header = field.find_element_by_class_name('job-criteria__subheader')
                #     print(job_criteria_header.text, end=' ')
                job_criteria_text = field.find_element_by_class_name('job-criteria__text')
                #     print(job_criteria_text.text)

                if job_criteria_header.text == "Seniority level":
                    seniority_level = job_criteria_text.text
                elif job_criteria_header.text == "Employment type":
                    employment_type = job_criteria_text.text
                elif job_criteria_header.text == "Job function":
                    job_function = job_criteria_text.text
                elif job_criteria_header.text == "Industries":
                    industries = job_criteria_text.text

            return seniority_level,employment_type,job_function,industries

        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            print("Job Criteria Element not found")
            job_criteria_item = browser.find_elements_by_class_name('job-criteria__item')

            seniority_level = None
            employment_type = None
            job_function = None
            industries = None

            for field in job_criteria_item:
                #     print(field.text)
                job_criteria_header = field.find_element_by_class_name('job-criteria__subheader')
                #     print(job_criteria_header.text, end=' ')
                job_criteria_text = field.find_element_by_class_name('job-criteria__text')
                #     print(job_criteria_text.text)

                if job_criteria_header.text == "Seniority level":
                    seniority_level = job_criteria_text.text
                elif job_criteria_header.text == "Employment type":
                    employment_type = job_criteria_text.text
                elif job_criteria_header.text == "Job function":
                    job_function = job_criteria_text.text
                elif job_criteria_header.text == "Industries":
                    industries = job_criteria_text.text
            return seniority_level, employment_type, job_function, industries

#Job Desctription
    def f_job_description():
        try:
            job_description_ele = browser.find_element_by_class_name('description__text')
            job_description = job_description_ele.text

        except ElementNotInteractableException:
            sleep(random_time(5, 7))
            job_description_ele = browser.find_element_by_class_name('description__text')
            job_description = job_description_ele.text

        except NoSuchElementException:
            job_description = "Not Found"

        if len(job_description)>0:
            return job_description
        else:
            return None



    job_title = f_job_title()
    company_name = f_job_company_name()
    job_location = f_job_company_location()
    posted_time = f_job_posted_time()
    no_applicants = f_job_no_applicants()
    apply_link = f_job_apply_button_link()
    description = f_job_description()
    # job_criteria =  f_job_criteria(element)
    job_id = f_job_id()
    (seniority_level, employment_type, job_function, industries) = f_job_criteria()
    timestamp = datetime.datetime.now()

    data = {
            "job_id": job_id,
            "title": job_title,
            "company_name": company_name,
            "job_location": job_location,
            "posted_time": posted_time,
            "no_applicants": no_applicants,
            "apply_link":apply_link,
            "description": description,
            "seniority_level": seniority_level,
            "employment_type": employment_type,
            "job_function": job_function,
            "industries": industries,
            "recorded_timestamp": timestamp
        }

    df = pd.DataFrame([data])

    print(df)

    return df