import openai
from dotenv import load_dotenv
import os
from googlesearch import search
import json

def configure():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

def rank_websites(query,message,result_dict):
    messages = [
    {"role": "system", "content": "The user is looking for a Dataset on" + query + ". The user will provide you with a list of websites. You have to rank these websites from best to scrape, to worst to scrape. While ranking keep in mind, the dataset the user is looking for and if the website you rank high will have these coloumns:"+ str(result_dict[5])+" which are important to satisfy the customer"},
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

# This function will make an api call to extract the important columns that the dataset that the user is looking for could have and assign a priority score to each column out of 5. 5 being the highest priority.

def important_columns(message):
    messages = [
    {"role": "system", "content": "The user is looking for a Dataset on" + query + ". Come up with list of columns that the dataset could have and assign a priority score to each column out of 5. 5-Highest, 4-High, 3-Medium, 2-Low, 1-Lowest. Highest Priority means without that coloumn the dataset wouldn't fulfill user's request. Send Back only the coloumns and no other text. Send back the columns in JSON format. Only send back JSON and No other text. The JSON format should be like this: " + '{5":["column1","column2"],"4":["column3","column4"],"3":["column5","column6"],"2":["column7","column8"],"1":["column9","column10"]}'},
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

    #reply is in JSON format
    messages.append({"role": "assistant", "content": reply})
    return reply

#Convert JSON to Python Dictionary
def convert_json_to_dict(json_string):
    json_dict = json.loads(json_string)

    result_dict = {}
    for priority, columns in json_dict.items():
        result_dict[int(priority)] = columns
    return result_dict




def search_results(query):
    websites=""
    for url in search(query, tld="co.in", stop=10):
        websites=websites+url+" "
    return websites
    

configure()
query=input("What data are you looking for?: ")
websites=search_results(query)

json_string = important_columns(query) #ChatGPT will Print the JSON string
result_dict = convert_json_to_dict(json_string) 
print(result_dict)
rank_websites(query,websites,result_dict)

# rank_websites(query,"https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1806254 https://www.statista.com/statistics/1061130/india-population-of-pet-dogs/ https://timesofindia.indiatimes.com/life-style/relationships/pets/popular-dog-breeds/articleshow/60132107.cms https://dahd.nic.in/sites/default/filess/Breeding%20Survey%20Book%20-%20Corrected.pdf https://en.wikipedia.org/wiki/List_of_dog_breeds_from_India https://en.wikipedia.org/wiki/List_of_most_popular_dog_breeds https://vikaspedia.in/agriculture/agri-directory/reports-and-policy-briefs/20th-livestock-census https://www.nddb.coop/information/stats/pop https://nbagr.icar.gov.in/wp-content/uploads/2021/11/NBAGR-Annual-Report-2020.pdf https://highlandcanine.com/the-50-most-popular-dog-breeds-in-the-world-2019/")