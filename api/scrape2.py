import requests
from bs4 import BeautifulSoup
import pandas as pd

page = requests.get("https://www.interflora.in/blog/guide-to-indian-blooms-flower-types-and-uses")
soup = BeautifulSoup(page.content, 'html.parser')

data = []
table = soup.find_all('div', class_='blog-area-description')
rows = table[0].find_all('p')
for row in rows[1:]:
    value = row.text.strip()
    data.append(value)

df = pd.DataFrame(data, columns=["List of flowers found in India"])
df.to_excel("Dataset.xlsx", index=False)