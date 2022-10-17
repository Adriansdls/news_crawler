import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import date
from datetime import datetime
import re
from pandas.errors import ParserError
from datetime import datetime

now = datetime.now()
current_time = now.strftime("%d.%m.%Y %H:%M:%S")

cadena_ser = pd.read_csv("data/cadena_ser.csv")
cadena_ser.drop("Unnamed: 0",axis=1,inplace=True)
cadena_ser.to_csv("data/cadena_ser_links_bup.csv")
old_links = cadena_ser.url.to_list()

new_links = pd.DataFrame(columns=["pos","url","crawl_day"])

path = "/Users/adriansanchezdelasierra/projects/news_parser/new_crawler/chromedriver"
s = Service(path)
options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=s,options=options)
#driver = webdriver.Chrome(executable_path="/Users/adriansanchezdelasierra/projects/news_parser/new_crawler/chromedriver" ,chrome_options=options)

url = "https://www.cadenaser.com/"
driver.get(url)

page_source = driver.page_source

soup = BeautifulSoup(page_source, "html.parser") #lxml to be solved

articles = soup.find_all("article")

for n,article in enumerate(articles):
    l = []
    for a in article.findAll("a"):
        try:
            href = "https://www.cadenaser.com{0}".format(a["href"])
        except KeyError:
            pass
    pos = n

    l.append([pos,href,date.today()])
    df_ = pd.DataFrame(l,columns=["pos","url","crawl_day"])
    new_links = pd.concat([new_links,df_],axis=0)

new_links.drop_duplicates(inplace=True)
new_links.reset_index(inplace=True,drop=True)

for col,row in new_links.iterrows():
    if row["url"] in old_links:
        new_links.drop(col,inplace=True)

cadena_ser = pd.concat([cadena_ser,new_links],axis=0)
cadena_ser.drop_duplicates(inplace=True)
cadena_ser.reset_index(inplace=True,drop=True)

print("{0} - {1} new links will be parsed".format(current_time, len(new_links)))

df_full = pd.DataFrame(columns=["fecha","programa","seccion","tags","tags_2","loc","titulo","titulo_2","subtiulo","texto","url","pos","crawl_day"])

for col,row in new_links.iterrows():
    try:
        l=[]
        url = row["url"]
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        head = soup.find("head")
        body = soup.find("body")
        article = soup.find("article")

        seccion = article.find("a",class_="bcrumb").text
        titulo = article.header.find("h1").text
        subtitulo = article.header.find("h2").text
        fecha = pd.to_datetime(head.find("meta",property="article:published_time")["content"]).date().isoformat()
        seccion = head.find_all("meta",property="article:tag")[0]["content"]
        programa = article.header.find("a").text

        lista_tags =list(head.find_all("meta",property="article:tag"))
        
        tags = []
        for i in lista_tags:
            tags.append(i["content"])

        tags = ", ".join(tags)
        
        titulo_2 = head.find("meta", property="og:title")["content"]
        loc = body.find("p",class_="loc").text
        texto = body.find("div",class_="cnt-txt").text

        lista_tags_2 = body.find("div",class_="tags").find_all("li")

        tags_2 = []
        for i in lista_tags:
            tags_2.append(i["content"])

        tags_2 = ", ".join(tags_2)
    except:
        continue
    
    l.append([fecha, programa, seccion, tags, tags_2, loc, titulo, titulo_2, subtitulo, texto, row["url"], row["pos"],date.today()])
    df_ = pd.DataFrame(l,columns=["fecha","programa","seccion","tags","tags_2","loc","titulo","titulo_2","subtiulo","texto","url","pos","crawl_day"])
    df_full = pd.concat([df_full,df_], axis=0)

df_full.url.drop_duplicates(inplace=True)

df_cadena_ser = pd.read_csv("/Users/adriansanchezdelasierra/projects/news_parser/new_crawler/csvs/cadena_ser_full.csv")
df_cadena_ser.drop("Unnamed: 0",axis=1,inplace=True)
df_cadena_ser.reset_index(inplace=True,drop=True)
df_cadena_ser.to_csv("data/cadena_ser_full_bup.csv")

df_cadena_ser = pd.concat([df_cadena_ser,df_full],axis=0)
df_cadena_ser.reset_index(inplace=True,drop=True)
df_cadena_ser.to_csv("/Users/adriansanchezdelasierra/projects/news_parser/new_crawler/csvs/cadena_ser_full.csv")

# ACTUALIZANDO OLD LINKS
cadena_ser.to_csv("data/cadena_ser.csv")
