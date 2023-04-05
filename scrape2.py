import requests
from bs4 import BeautifulSoup
import pandas as pd

# use requests to get the HTML content of the website
url = 'https://forbesindia.com/lists/2019-celebrity-100/1819/all'
response = requests.get(url)
html_content = response.content

# use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# find the table that contains the data
table = soup.find('table', attrs={'class': 'tbldata14'})

# create a list to store the column titles
columns = []

# loop through the header row and add each column title to the columns list
header_row = table.find('tr', attrs={'class': 'tbldatahdr'})
for header in header_row.find_all('th'):
    columns.append(header.text.strip())

# create a list to store the data
data = []

# loop through each row of the table and add each data point to the data list
rows = table.find_all('tr', attrs={'class': 'evenrow'})
rows.extend(table.find_all('tr', attrs={'class': 'oddrow'}))
for row in rows:
    data_row = []
    for item in row.find_all('td'):
        data_row.append(item.text.strip())
    data.append(data_row)

# convert the data and columns lists to a pandas DataFrame
df = pd.DataFrame(data, columns=columns)

# export the DataFrame to an Excel file
df.to_excel('forbes_india_celebrity_100_2019.xlsx', index=False)