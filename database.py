import pyodbc
import urllib
import sqlalchemy
import pandas as pd
import datetime
# from scraper import *


def read_sql_server(sql_query):

    cnct = pyodbc.connect(r"DRIVER={ODBC DRIVER 17 for SQL Server};"
                          r"SERVER=BSLT-25\ROBINHOOD1;"
                          r"DATABASE=linkedin_scraper;"
                          r"Trusted_Connection=yes;", autocommit=True)
    print('connected_to_db')

    df = pd.read_sql(sql_query,cnct)

    print('closing conn')

    cnct.close

    return df



def write_to_database_job_details(df):

    cnct = pyodbc.connect(r"DRIVER={ODBC DRIVER 17 for SQL Server};"
                          r"SERVER=BSLT-25\ROBINHOOD1;"
                          r"DATABASE=master;"
                          r"Trusted_Connection=yes;", autocommit=True)
    print('connection established')

    cur = cnct.cursor()
    cur.execute("""IF DB_ID('linkedin_scraper') IS NULL BEGIN CREATE DATABASE linkedin_scraper END""")

    cur.execute("""USE linkedin_scraper""")

    cur.execute("""IF OBJECT_ID(N'job_details_l3', N'U') IS NULL BEGIN
    CREATE TABLE job_details_l3(
                            job_id varchar(max),
                            title varchar(max),
                            company_name varchar(max),
                            job_location varchar(max),
                            posted_time varchar(max),
                            no_applicants varchar(max),
                            apply_link varchar(max),
                            description varchar(max),
                            seniority_level varchar(max),
                            employment_type varchar(max),
                            job_function varchar(max),
                            industries varchar(max),
                            recorded_timestamp datetime
                            )
                            END""")

    cnct.commit()

    params = urllib.parse.quote_plus(r'DRIVER={ODBC DRIVER 17 for SQL Server};'
                          r'SERVER=BSLT-25\ROBINHOOD1;;'
                          r'DATABASE=linkedin_scraper;'
                          r'Trusted_Connection=yes;')


    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}" .format(params))
    df.to_sql(name='job_details_l3', con=engine, if_exists='append', index=False)


    cur.close()
    cnct.close()
    print("Write to Database Successful")

# file_path = 'C:/Users/kkari/Desktop/dev/LinkedIn_extractor/scraper_output_file-2_11_2020.csv'
# df = pd.read_csv(file_path)
# # appendDFToCSV_void(df, file_path, sep=',')
# print(df)
#
# write_to_database_job_details(df)
