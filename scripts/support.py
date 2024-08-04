import json
import discord
import requests
from bs4 import BeautifulSoup


def get_json(path):
    with open(path, encoding="utf8") as f:
        f = f.read()
        return json.loads(f)


def load_gif_from_tenor(link: str) -> discord.File:
    reg = requests.get(link).content
    soup = BeautifulSoup(reg, 'html.parser')
    lin = soup.find("meta", {"itemprop": "contentUrl"}).get("content")
    req2 = requests.get(lin).content
    print(req2[0:100])
    return discord.File(req2)

