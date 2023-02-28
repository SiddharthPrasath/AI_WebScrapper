import requests
from bs4 import BeautifulSoup

# Send a request to the website
url = "https://www.gizbot.com/mobile-brands-in-india/"
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, "html.parser")

# Print the HTML source code
print(soup.prettify())
