import requests
from lxml.html import fromstring
import random
import pandas as pd
from lxml import html
from itertools import cycle
from boltons import iterutils
from main import *

def ip_scraper():
# This function scrapes the public ip website and returns the ip_list that should possibly work with https connection.
# the output format is as follows, "https:// [ip]:[port]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    # master_list = []

    print("Fetching proxy IPs")

    url = 'https://free-proxy-list.net/'
    page = requests.get(url, headers=headers)
    doc = html.fromstring(page.content)
    xpath_proxies = '//*[@id="proxylisttable"]//text()'
    raw_proxies = doc.xpath(xpath_proxies)
    print(raw_proxies)
    ip_list_with_headings = iterutils.chunked(raw_proxies,8)
    ip_main_list = ip_list_with_headings[1:]

    df = pd.DataFrame(ip_main_list)
    df.columns = ip_list_with_headings[0]

    df_https = df[df['Https'] == 'yes']
    pd.options.mode.chained_assignment = None

    df_https['last_checked_min'] = df_https['Last Checked'].str.split().str[0]
    df_https['last_checked_time_units'] = df_https['Last Checked'].str.split().str[1]
    df_https['proxy'] = "https://" +df_https['IP Address'] + ":" + df_https['Port']
    df_https[['last_checked_min']] = df_https[['last_checked_min']].apply(pd.to_numeric)
    df_https['last_checked_min_converted'] = df_https.apply(lambda row: new_column_time(row), axis=1)
    df_https = df_https[df_https['last_checked_min_converted']<=20]

    new_df = df_https['proxy'].values

    ip_list = new_df.tolist()
    print('cleanded proxy df')
    return ip_list

def new_column_time(row):
    if row['last_checked_time_units'] == "seconds":
        return row['last_checked_min']/60
    elif row['last_checked_time_units'] == "minutes":
        return row['last_checked_min']
    elif row['last_checked_time_units'] == "hours":
        return row['last_checked_min']*60

def ip_randomizer():
    global master_list
    if len(master_list)<=3:
        temp_list = ip_scraper()
        print("Running IP scraper via randomizer")
        initial_ip_validation(temp_list)
        ip_randomizer()
    else:
        new_ip = random.choice(master_list)
    return new_ip

def ip_validator(ip):
    global master_list
    try:
        print("Validating {}".format(ip))
        print("current master list length={}".format(len(master_list)))

        url_0 = 'https://httpbin.org/ip'
        response_0 = requests.get(url_0, proxies={"https": ip})
        print("{} Successfully established connection with {}" .format(ip,url_0))
        sleep(4)
        url_1 = 'https://www.amazon.in/'
        response_1 = requests.get(url_1, proxies={"https": ip})
        print("{} Successfully established connection with {}" .format(ip,url_1))
        sleep(3)

        return ip

    except Exception as e:
        if ip in master_list:
            master_list.remove(ip)
            print("Exception occoured for {}. Exception:{}".format(ip,e))
            print("{} Validation failed. Deleted from Master list. Current IP count in Master = ".format(ip,len(master_list)))
            print("Fetching new ip from IP randomizer")
            new_ip = ip_randomizer()
            ip_validator(new_ip)
        else:
            print("Exception occoured for {}. Exception:{}".format(ip,e))
            print("{} Validation failed. Current IP count in Master = ".format(ip,len(master_list)))
            print("Fetching new ip from IP randomizer")
            new_ip = ip_randomizer()
            ip_validator(new_ip)

def initial_ip_validation(ip_list):
    global master_list
    print("Running initial validator")
    for ip in ip_list:
        if len(master_list) <= 5:
            try:
                print("Validating {}".format(ip))

                url_0 = 'https://httpbin.org/ip'
                response_0 = requests.get(url_0, proxies={"https": ip})
                print("{} Successfully established connection with {}".format(ip, url_0))
                sleep(4)
                url_1 = 'https://www.amazon.in/'
                response_1 = requests.get(url_1, proxies={"https": ip})
                print("{} Successfully established connection with {}".format(ip, url_1))

                master_list.append(ip)
                print("Master list ={}".format(master_list))
                sleep(3)
            except Exception as e:
                print("Exception occoured during initial validation for {}. Exception:{}".format(ip,e))
                continue
            else:
                continue
