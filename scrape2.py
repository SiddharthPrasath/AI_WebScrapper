import requests
from bs4 import BeautifulSoup
import csv

# URL for the Wikipedia page
url = 'https://en.wikipedia.org/wiki/List_of_Indian_state_birds'

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table containing the data
table = soup.find('table', {'class': 'wikitable sortable'})

# Find all the rows in the table
rows = table.find_all('tr')

# Create a new CSV file and write the headers
with open('indian_state_birds.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['State', 'Common name', 'Scientific name', 'Image'])

    # Loop through all the rows and extract the data
    for row in rows[1:]:
        # Find all the cells in the row
        cells = row.find_all('td')

        # Extract the data from the cells
        state = cells[0].text.strip()
        common_name = cells[1].text.strip()
        scientific_name = cells[2].text.strip()
        image = cells[3].find('a', class_='image')

        # Write the data to the CSV file
        writer.writerow([state, common_name, scientific_name, image])

print('Data scraped successfully!')
