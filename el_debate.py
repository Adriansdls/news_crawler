import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import date
from datetime import datetime
import re
from pandas.errors import ParserError

el_debate = pd.read_csv("el_debate/data/el_debate.csv")
el_debate.drop("Unnamed: 0",axis=1,inplace=True)
el_debate.to_csv("el_debate/data/bups/el_debate_links_bup.csv")
old_links = el_debate.url.to_list()

new_links = pd.DataFrame(columns=["pos","url","crawl_day"])

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=options)

url = "https://www.eldebate.com/"
driver.get(url)

page_source = driver.page_source

soup = BeautifulSoup(page_source, "lxml")

articles = soup.find_all("article")

for n,article in enumerate(articles):
    l = []
    for a in article.findAll("a"):
        try:
            href = "https://www.eldebate.com{0}".format(a["href"])
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

el_debate = pd.concat([el_debate,new_links],axis=0)
el_debate.drop_duplicates(inplace=True)
el_debate.reset_index(inplace=True,drop=True)
el_debate.to_csv("el_debate/data/el_debate.csv")
print("{0} new links will be parsed".format(len(new_links)))

df_full = pd.DataFrame(columns=["tags","tag","keywords","url","seccion","pos","date","title","sub","author","text","crawl_day"])

for col,row in new_links.iterrows():
    l=[]
    url = row["url"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    head = soup.find("head")
    seccion = soup.find("meta",property="article:section")
    title = soup.find("meta",property="og:title")
    title = title["content"]
    seccion = seccion["content"]

    for i in head.find_all("meta"):
        try:
            if i["name"] == "date":
                fecha = i["content"]
            elif i["name"] == "Keywords":
                keywords = i["content"]
            elif i["name"] == "author":
                author = i["content"]
            elif i["name"] == "article:tag":
                tag = i["content"]
        
        except KeyError:
            pass

    try:
        sub = soup.find("div",class_="c-detail__subtitle").text
    except AttributeError:
        try:
            sub = soup.find("h2",class_="c-detail__subtitle").find("h2").text
        except AttributeError:
            sub = "Nan"
    
    text = []
    x = soup.find_all("div",class_="paragraph")
    for i in x:
        text.append(i.text)
    text = " ".join(text)
    
    temas = []
    x = soup.find_all("li",class_="c-detail__tags__item")
    for i in x:
        temas.append(i.text.replace("\n",""))
    
    l.append([temas,tag,keywords,row["url"],seccion,row["pos"], fecha, title, sub, author, text,date.today()])
    df_ = pd.DataFrame(l,columns=["tags","tag","keywords","url","seccion","pos","date","title","sub","author","text","crawl_day"])
    df_full = pd.concat([df_full,df_], axis=0)

df_full.url.drop_duplicates(inplace=True)

df_el_debate = pd.read_csv("el_debate/data/el_debate_full.csv")
df_el_debate.drop("Unnamed: 0",axis=1,inplace=True)
df_el_debate.reset_index(inplace=True,drop=True)
df_el_debate.to_csv("el_debate/data/bups/el_debate_full_bup.csv")

df_el_debate = pd.concat([df_el_debate,df_full],axis=0)
df_el_debate.reset_index(inplace=True,drop=True)
df_el_debate.to_csv("el_debate/data/el_debate_full.csv")