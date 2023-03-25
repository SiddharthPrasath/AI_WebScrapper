import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.forbes.com/lists/india-billionaires/?sh=7914181e109b'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')

tables = soup.findAll('div', {'class': 'table'})
results = []

for table in tables:

    rows = table.findAll('a')


    for row in rows:
        rank = row.find('div', {'class': 'rank first table-cell rank'})
        name = row.find('div', {'class': 'personName second table-cell name'})
        net_worth = row.find('div', {'class': 'finalWorth table-cell net worth'})
        industry = row.find('div', {'class': 'category table-cell industry'})

        if name is not None:
            results.append({
                'Rank': rank.text.strip(),
                'Name': name.text.strip(),
                'Net Worth': net_worth.text.strip(),
                'Industry': industry.text.strip()})

df = pd.DataFrame(results)
df.to_excel('IndiaBillionaires6.xlsx', index=False)