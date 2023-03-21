import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_Japanese_prefectures_by_population'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if cells:
            name = cells[1].text.strip()
            population_2020 = cells[2].text.strip()
            population_2015 = cells[3].text.strip()
            population_2010 = cells[4].text.strip()
            population_2005 = cells[5].text.strip()
            population_2000 = cells[6].text.strip()
            population_1995 = cells[7].text.strip()
            population_1990 = cells[8].text.strip()
            population_1985 = cells[9].text.strip()

            print(name, population_2020, population_2015, population_2010, population_2005, population_2000, population_1995, population_1990, population_1985)
else:
    print('not_possible')