import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_match_info(match_str):
    pattern = r"^(\d{4}-\d{2}-\d{2}) (.+?) ([A-Z0-9]+): ([\w\s\.-]+) vs ([\w\s\.-]+) \((ATP|WTA)\)$"
    match = re.match(pattern, match_str)
    
    if match:
        date = match.group(1)
        tournament = match.group(2).strip()
        round_ = match.group(3)

        player1_fullname = match.group(4).strip().split(" ")
        player2_fullname = match.group(5).strip().split(" ")

        player1_firstname = " ".join(player1_fullname[:-1])
        player1_lastname = player1_fullname[-1]

        player2_firstname = " ".join(player2_fullname[:-1])
        player2_lastname = player2_fullname[-1]

        category = match.group(6)

        return {
            "date": date,
            "tournament": tournament,
            "round": round_,
            "player1_firstname": player1_firstname,
            "player1_lastname": player1_lastname,
            "player2_firstname": player2_firstname,
            "player2_lastname": player2_lastname,
            "category": category
        }
    else:
        return None

url = "https://www.tennisabstract.com/charting/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

matches_div = soup.find('div', id='header')
links = matches_div.find_all('a')

data = []
for link in links:
    href = link.get('href')
    if href.startswith('2025'):
        text = link.get_text()
        parsed = parse_match_info(text)
        if parsed:
            parsed["URL"] = href
            data.append(parsed)
        else:
            print(f"Could not parse: {text}")
    else:
        continue

df = pd.DataFrame(data)

df.to_csv("data/Scrapping/list_matches.csv", index=False)
