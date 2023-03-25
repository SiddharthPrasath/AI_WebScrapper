import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.equitymaster.com/stock-screener/top-banking-companies-in-india"
html_content = requests.get(url).text

soup = BeautifulSoup(html_content, "html.parser")
table = soup.find_all("table", {"class": "tableData"})[0]
headers = []
for th in table.find_all("th"):
    headers.append(th.get_text().strip())

result = []
for row in table.find_all("tr"):
    d = []
    cells = row.findAll(["td", "th"])
    for cell in cells:
        d.append(cell.get_text().strip())
    if len(d) == len(headers):
        result.append(d)

df = pd.DataFrame(result, columns=headers)
df = df[df['Revenue-Rs.Cr']>='1']
df = df.iloc[:, 1:]
print(df)
df.to_excel('output.xlsx', index=False)