import requests
from bs4 import BeautifulSoup

# URL of the webpage to scrape
url = 'https://www.imdb.com/list/ls530915139/'

# Send a GET request to the URL and store the response
response = requests.get(url)

# Parse the HTML content of the page using Beautiful Soup
soup = BeautifulSoup(response.content, 'html.parser')

# Remove unnecessary elements from the HTML
for script in soup(["script", "style", "nav", "footer", "head", "header", "aside", "form"]):
    script.extract()

# Extract only the <body> element
body = soup.body

# Format the HTML source code with indentation and extract the middle 300 lines
body_lines = str(body.prettify()).split('\n')
middle_index = len(body_lines) // 2
middle_lines = body_lines[middle_index - 150:middle_index + 150]

# Join the middle lines together with line breaks and display them
print('\n'.join(middle_lines))
