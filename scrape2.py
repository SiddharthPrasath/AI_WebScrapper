import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://en.wikipedia.org/wiki/List_of_Indians_by_net_worth'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'class': 'wikitable sortable'})

table_head = table.find('thead')
header_cols = table_head.find_all('th')
headers = [col.text.strip() for col in header_cols]

table_body = table.find('tbody')
rows = table_body.find_all('tr')[1:]

data = []
for row in rows:
    cols = row.find_all(['th', 'td'])
    cols = [col.text.strip() for col in cols]
    data.append(cols)

df = pd.DataFrame(data, columns=headers)

df.to_excel('indian_billionaires.xlsx', index=False)