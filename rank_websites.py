import openai
from dotenv import load_dotenv
import os
from googlesearch import search
import json
import requests
from bs4 import BeautifulSoup
import re

def configure():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

def rank_websites(query,message,result_dict):
    messages = [
    {"role": "system", "content": "Do not reply with anything other than the JSON. The user is looking for a Dataset on: '" + query + "'. The user will provide you with a list of websites. You have to rank these websites from best to scrape, to worst to scrape. While ranking keep in mind, the dataset the user is looking for and if the website you rank high will have these coloumns:"+ str(result_dict[5])+" which are important to satisfy the customer. Also keep in mind that the content on the website should be free to access and not behing a paywall. Return the websites ranked in JSON format.The JSON format should be like this: " + '{"1":["website1"],"2":["website2"],"3":["website3"],"4":["website4"],"5":["website5"]}'+". Do not reply with any text other than JSON."},
]
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print("Do not reply with anything other than the JSON. The user is looking for a Dataset on" + query + ". The user will provide you with a list of websites. You have to rank these websites from best to scrape, to worst to scrape. While ranking keep in mind, the dataset the user is looking for and if the website you rank high will have these coloumns:"+ str(result_dict[5])+" which are important to satisfy the customer. Also keep in mind that the content on the website should be free to access and not behing a paywall. Return the websites ranked in JSON format. Do not return anything other than the json. The JSON format should be like this: " + '{"1":["website1"],"2":["website2"],"3":["website3"],"4":["website4"],"5":["website5"]}'+". Rank Wiki Sites always higher.")
    print(f"DataGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})
    return reply

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
    #print(f"DataGPT: {reply}")

    #reply is in JSON format
    messages.append({"role": "assistant", "content": reply})
    return reply

#Convert JSON to Python Dictionary
def convert_json_to_dict(json_string):
    json_dict = json_string

    result_dict = {}
    for priority, columns in json_dict.items():
        result_dict[int(priority)] = columns
    return result_dict


def convert_json_to_list(json_string):

        json_obj = json.loads(json_string)
        result = []
        for key, value in json_obj.items():
            result.append([key] + value)
        return result


def search_results(query):
    websites=""
    for url in search(query, tld="co.in", stop=10):
        websites=websites+url+" "
    return websites



def get_source_code_old(url):
    try:
        headers={'User-Agent':'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/58.0.3029.110Safari/537.3'}
        response=requests.get(url,headers=headers,timeout=10)
        soup=BeautifulSoup(response.content,'html.parser')
        for script in soup(["script","style","nav","footer","head","header","aside","form"]):
            script.extract()
        body=soup.body
        body_lines=str(body.prettify()).split('\n')
        middle_index=len(body_lines)//2
        middle_lines=body_lines[middle_index-150:middle_index+150]
        return ''.join(middle_lines).replace(" ", "").replace("\n", "")
    except Exception as e:
        print(f"Error occurred: {e}")
        return "None"

def get_source_code(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0(Windows NT 10.0;Win64;x64)AppleWebKit/537.36(KHTML,like Gecko)Chrome/58.0.3029.110Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for elem in soup(["script", "style", "nav", "footer", "head", "header", "aside", "form", "noscript", "meta", "link", "comment"]):
            elem.extract()
        
        # Remove whitespace outside of quotes
        body = soup.find('body')
        body_str = str(body)
        body_str = re.sub(r'(?<=[^\s="])\s+(?![^"]*")|(?<!^)\s+(?=[^"]*(?:"[^"]*"[^"]*)*$)', '', body_str)

        # Extract middle 220 lines
        chunk_size = 80
        chunks = [body_str[i:i+chunk_size] for i in range(0, len(body_str), chunk_size)]
        middle_index = len(chunks) // 2
        middle_chunks = chunks[middle_index - 70:middle_index + 70]

        # Remove newlines and return
        return ''.join(middle_chunks).replace("\n", "")
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return "None"
    
#this function will write code to create the web scrapper
def web_scrapper(query,link,result_dict,message):
    messages = [
    {"role": "system", "content": "You are a developer. You need to write python code to scrape this website:" + link + ". Write the code for a python scrapper, the dataset the user is looking for is " + query + ". The user will share a snippet from the source code of the website. Analyze the source code to find elements and class names that you need to scrape if necessary. For eg: wiki tables might often have th as well as td in their tables as records which causes errors in the scrappers you write, so you can analyze the source code to see which columns/records are th and which is td. Remember that there might be advertisements on the website so make sure the scrapper is scrapping throughout the entire website using find all. Make sure you add coloumn titles, Scrape and return the data only in a Excel file. Only return Python Code, do not return any other words other than the code. If the data is behind a paywall reply with only not_possible, but only if it is behind a paywall, if you are only able to scrape parts of the dataset the user is looking for its fine, reply with the code anyways"},
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
    if reply=="not_possible":
        return reply

    messages.append({"role": "assistant", "content": reply})
    scraper=clean_gpt_output(reply)
    print(scraper)
    try:
        exec(scraper)
    except Exception as e:
        print(f"Error occurred: {e}")
        #return error message
        messages.append(
                    {"role": "user", "content": "Error occurred:"+ str(e) +"Please updated the code and send back the code again, only send back the code, do not send back any other text"},
                )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        new_scrapper = chat.choices[0].message.content
        new_scrapper=clean_gpt_output(new_scrapper)
        messages.append({"role": "assistant", "content": new_scrapper})

        print(f"DataGPT: {new_scrapper}")
        try:
            exec(new_scrapper)
        except Exception as e:
            print(f"Error occurred: {e}")
            #return error message
            messages.append(
                        {"role": "user", "content": "Error occurred:"+ str(e) +"Please update the code and send back the code again, only send back the code, do not send back any other text"},
                    )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            new_scrapper = chat.choices[0].message.content
            new_scrapper=clean_gpt_output(new_scrapper)
            messages.append({"role": "assistant", "content": new_scrapper})

            print(f"DataGPT: {new_scrapper}")
            exec(new_scrapper)
def clean_gpt_output(output):
    code_lines = []
    is_python = True
    for line in output.split('\n'):
        if line.startswith('```python'):
            is_python = True
            code_lines.append(line.replace('```python', ''))
        elif line.startswith('```'):
            is_python = False
        elif is_python:
            code_lines.append(line)
    return '\n'.join(code_lines)

def run_scrapper(scraper):
    try:
        exec(scraper)
    except Exception as e:
        print(f"Error occurred: {e}")
        #return error message
        return str(e)
    
def clean_gpt_response_to_json(response):
    # Check if the response is a JSON string or not
    try:
        json_data = json.loads(response)
        return json_data
    except ValueError:
        # If the response contains both JSON and text, extract only the JSON data
        json_start = response.find('{')
        json_end = response.rfind('}')
        if json_start != -1 and json_end != -1:
            json_data = response[json_start:json_end+1]
            return json.loads(json_data)
    # If the response is neither JSON nor contains JSON, return None
    return None
configure()
query=input("What data are you looking for?: ")
websites=search_results(query)

json_string = important_columns(query) #ChatGPT will Print the JSON string
cleaned_json_string = clean_gpt_response_to_json(json_string)
print(cleaned_json_string)
result_dict = convert_json_to_dict(cleaned_json_string) 
print(result_dict)
json_string2=rank_websites(query,websites,result_dict)
try:
    result_list = convert_json_to_list(json_string2)
    print(result_list)
except:
    json_string2=rank_websites(query,websites,result_dict)
    result_list = convert_json_to_list(json_string2)

for i in range(0, 5):
    source_code = get_source_code(result_list[i][1])
    print(source_code)
    try:
        scraper = web_scrapper(query, result_list[i][1], result_dict, source_code)
    except Exception as e:
        print("too much tokens")
        continue
    if scraper != "not_possible":
        break
        
    # add the code that runs when web_scrapper succeeds here





# rank_websites(query,"https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1806254 https://www.statista.com/statistics/1061130/india-population-of-pet-dogs/ https://timesofindia.indiatimes.com/life-style/relationships/pets/popular-dog-breeds/articleshow/60132107.cms https://dahd.nic.in/sites/default/filess/Breeding%20Survey%20Book%20-%20Corrected.pdf https://en.wikipedia.org/wiki/List_of_dog_breeds_from_India https://en.wikipedia.org/wiki/List_of_most_popular_dog_breeds https://vikaspedia.in/agriculture/agri-directory/reports-and-policy-briefs/20th-livestock-census https://www.nddb.coop/information/stats/pop https://nbagr.icar.gov.in/wp-content/uploads/2021/11/NBAGR-Annual-Report-2020.pdf https://highlandcanine.com/the-50-most-popular-dog-breeds-in-the-world-2019/")