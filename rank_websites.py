import openai
from dotenv import load_dotenv
import os
from googlesearch import search

def configure():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

def rank_websites(query,message):
    messages = [
    {"role": "system", "content": "The user is looking for a Dataset on" + query + ". The user will provide you with a list of websites. You have to rank these websites from best to scrape, to worst to scrape. While ranking keep in mind, the dataset the user is looking for and if the website you rank high will have that data."},
]
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"DataGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})

def seacrh_results(query):
    websites=""
    for url in search(query, tld="co.in", stop=10):
        websites=websites+url+" "
    return websites
    

configure()
query=input("What data are you looking for?: ")
websites=seacrh_results(query)
rank_websites(query,websites)

# rank_websites(query,"https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1806254 https://www.statista.com/statistics/1061130/india-population-of-pet-dogs/ https://timesofindia.indiatimes.com/life-style/relationships/pets/popular-dog-breeds/articleshow/60132107.cms https://dahd.nic.in/sites/default/filess/Breeding%20Survey%20Book%20-%20Corrected.pdf https://en.wikipedia.org/wiki/List_of_dog_breeds_from_India https://en.wikipedia.org/wiki/List_of_most_popular_dog_breeds https://vikaspedia.in/agriculture/agri-directory/reports-and-policy-briefs/20th-livestock-census https://www.nddb.coop/information/stats/pop https://nbagr.icar.gov.in/wp-content/uploads/2021/11/NBAGR-Annual-Report-2020.pdf https://highlandcanine.com/the-50-most-popular-dog-breeds-in-the-world-2019/")