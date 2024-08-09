import json
import discord
import requests
from bs4 import BeautifulSoup
from censure import Censor  # https://github.com/Priler/samurai/tree/main/censure
from random import choice
from datetime import datetime

censor_ru = Censor.get(lang="ru")


def get_profanity(text):
    info = censor_ru.clean_line(text)
    return info


def get_json(path):
    with open(path, encoding="utf8") as f:
        f = f.read()
        return json.loads(f)


def save(a) -> None:
    with open("./saves.json", "w") as f:
        json.dump(a, f)


def get_holiday():
    link = "https://www.calend.ru/"
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "html.parser")
    id_ = f"day_{datetime.now().strftime("%Y")}-{datetime.now().strftime("%m-%d").replace("0", "")}"
    today = soup.find(id=id_)
    today = today.find(class_="wrapIn")
    return today.find("a").get_text()


def load_gif_from_tenor(link: str) -> discord.File:
    reg = requests.get(link).content
    soup = BeautifulSoup(reg, 'html.parser')
    lin = soup.find("meta", {"itemprop": "contentUrl"}).get("content")
    req2 = requests.get(lin).content
    print(req2[0:100])
    return discord.File(req2)


phrases = get_json("./phrases.json")


def get_phrase(key: str):
    return choice(phrases[key])


