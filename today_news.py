# Connect to Google Sheets
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

scope = ['https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name("/Users/adriansanchezdelasierra/projects/news_parser/new_crawler/newspapers-366612-be359318d4f2.json", scope)
client = gspread.authorize(credentials)

today_news_sheet = client.open("today_news").sheet1
today_news_sheet.clear()
today_news_sheet.batch_update([{"range" : "A1:D1", "values" : [["paper","foto","title","text"]]}])