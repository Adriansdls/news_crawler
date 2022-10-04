import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
from datetime import datetime
import re

el_diario = pd.read_csv("el_diario/data/el_diario.csv")
el_diario.drop("Unnamed: 0",axis=1,inplace=True)
el_diario.to_csv("el_diario/data/bups/el_diario_links_bup.csv")
old_links = el_diario.url.to_list()

new_links = pd.DataFrame(columns=["seccion","titulo","url","cmp","idx","dominio","crawl_day"])

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

url = "https://www.eldiario.es/"
driver.get(url)

page_source = driver.page_source

soup = BeautifulSoup(page_source, "lxml")

tags = soup.find_all("h2", {"class": "ni-title"})
errors=[]

for i in tags:
    l=[]

    i.a["href"]
    cmp = i.a["cmp-ltrk"]
    idx = i.a["cmp-ltrk-idx"]
    href = i.a["href"]
    if href.startswith("http"):
        link = href
        dominio = href.split("/")[2]
    else:
        link = "https://www.eldiario.es{0}".format(i.a["href"])
        dominio = "www.eldiario.es"
    titulo = i.text
    seccion = i.a["href"].split("/")[1]
    
    l.append([seccion,titulo,link,cmp,idx,dominio,date.today()])
    df_ = pd.DataFrame(l,columns=["seccion","titulo","url","cmp","idx","dominio","crawl_day"])
    new_links = pd.concat([new_links,df_],axis=0)

new_links = new_links[new_links["dominio"] == "www.eldiario.es"]
new_links.reset_index(inplace=True,drop=True)

for col,row in new_links.iterrows():
    if row["url"] in old_links:
        new_links.drop(col,inplace=True)

el_diario = pd.concat([el_diario,new_links],axis=0)
el_diario.reset_index(inplace=True,drop=True)
el_diario.to_csv("el_diario/data/el_diario.csv")
print("{0} new links will be parsed".format(len(new_links)))

df_full = pd.DataFrame(columns=["url","seccion","cmp","idx","date","title","sub","sub_2","authors","text","crawl_day"])

for col,row in new_links.iterrows():
    l=[]
    url = row["url"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if not "ultima-hora" in url.split("/")[4]:

        d = soup.find("time",{"class": "date"})
        try:
            date = datetime.strptime(d["datetime"], '%Y-%m-%dT%H:%M:%S+02:00').date()
        except ValueError:
            date = datetime.strptime(d["datetime"], '%Y-%m-%dT%H:%M:%S+01:00').date()

        title = soup.find("h1",{"class": "title"})
        title = title.text.replace("\n"," ")
        title = re.sub(' +', ' ', title)
        
        try:
            ul = soup.find("ul",{"class": "footer"})
            ul = ul.text.replace("\n"," ")
            ul = re.sub(' +', ' ', ul)
            sub = ul.split("—  ")[0]
            try:
                sub_2 = ul.split("—")[1]
            except IndexError:
                sub_2 = "no sub_2"
        except AttributeError:
            pass
        

        try:
            author = soup.find("p",{"class": "authors"})
            author = author.text.replace("\n"," ")
        except AttributeError:
            try:
                author = soup.find("a",{"class": "featured-name"})
                author = author.text.replace("\n"," ")
            except AttributeError:
                pass
        t = soup.find_all("p",{"class": "article-text"})
        text = ""

        for i in t:
            text = text + i.text
        text = text.replace("\n"," ")
        text = re.sub(' +', ' ', text)
        
        l.append([row["url"],row["seccion"],row["cmp"],row["idx"], date, title, sub, sub_2, author, text,date.today()])
        df_ = pd.DataFrame(l,columns=["url","seccion","cmp","idx","date","title","sub","sub_2","authors","text","crawl_day"])
        df_full = pd.concat([df_full,df_], axis=0)


df_el_diario = pd.read_csv("el_diario/data/el_diario_full.csv")
df_el_diario.drop("Unnamed: 0",axis=1,inplace=True)
df_el_diario.reset_index(inplace=True,drop=True)
df_el_diario.to_csv("el_diario/data/bups/el_diario_full_bup.csv")

df_el_diario = pd.concat([df_el_diario,df_full],axis=0)
df_el_diario.reset_index(inplace=True,drop=True)
df_el_diario.to_csv("el_diario/data/el_diario_full.csv")