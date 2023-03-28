import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://en.wikipedia.org/wiki/Pok%C3%A9mon_Trading_Card_Game'

response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'wikitable'})

rows = table.findAll('tr')

data = []

for row in rows[1:]:
    cols = row.findAll(['th','td'])
    cols = [col.text.strip() for col in cols]
    data.append(cols)

df = pd.DataFrame(data)

df.columns = ['Name',  'Type', 'Rarity']


df.to_excel('pokemoncards.xlsx', index=False)