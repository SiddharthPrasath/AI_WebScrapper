import traceback
import openai
from dotenv import load_dotenv
import os
from googlesearch import search
import json
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, render_template, send_file, session , flash, get_flashed_messages, Response
import pandas as pd
import io
import flask
from flask_session import Session
import concurrent.futures
import uuid
import time
import multiprocessing as mp
from multiprocessing import Pool
from functools import partial
def configure():
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')


def rank_websites(query,message,result_dict):
    messages = [
    {"role": "system", "content": "Do not reply with anything other than the JSON. The user is looking for a Dataset on: '" + query + "'. The user will provide you with a list of websites. You have to rank these websites from best to scrape, to worst to scrape. While ranking keep in mind, the dataset the user is looking for and if the website you rank high will have these coloumns:"+ str(result_dict[5])+" which are important to satisfy the customer. Also keep in mind that the content on the website should be free to access and not behing a paywall. Return the websites ranked in JSON format.The JSON format should be like this: " + '{"1":["website1"],"2":["website2"],"3":["website3"],"4":["website4"],"5":["website5"]}'+".One website per priority, Rank Wiki Sites always higher. Do not reply with any text other than JSON."},
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

def important_columns(query):
    message= "Reply with the list of columns along with their priority and reply only in JSON"
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
        middle_lines=body_lines[middle_index-115:middle_index+115]
        return ''.join(middle_lines).replace(" ", "").replace("\n", "")
    except Exception as e:
        print(f"Not able to get Source Code: {e}")
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
        chunk_size = 70
        chunks = [body_str[i:i+chunk_size] for i in range(0, len(body_str), chunk_size)]
        middle_index = len(chunks) // 2
        middle_chunks = chunks[middle_index - 50:middle_index + 50]

        # Remove newlines and return
        return ''.join(middle_chunks).replace("\n", "")
    
    except Exception as e:
        print(f"Not able to get Source Code: {e}")
        return "None"
    
#this function will write code to create the web scrapper
def web_scrapper_old(query,link,result_dict,message):
    messages = [
    {"role": "system", "content": "You are a developer. You need to write python code to scrape this website:" + link + ". Write the code for a python scrapper, the dataset the user is looking for is " + query + ". The user will share a snippet from the source code of the website. Analyze the source code to find elements and class names that you need to scrape if necessary. For eg: wiki tables might often have th as well as td in their tables as records which causes errors in the scrappers you write, so you can analyze the source code to see which columns/records are th and which is td. Remember that there might be advertisements on the website so make sure the scrapper is scrapping throughout the entire website using find all. Make sure you add coloumn titles, Scrape and return the data only in a Excel file. The name of the excel file should be Dataset. Only return Python Code, do not return any other words other than the code. If the data is behind a paywall reply with only not_possible, but only if it is behind a paywall, if you are only able to scrape parts of the dataset the user is looking for its fine, reply with the code anyways"},
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
    scraper=modify_python_code(scraper)
    print(scraper)
    try:
        response = execute_scrapper(scraper)
        return response
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
        new_scrapper=modify_python_code(new_scrapper)

        messages.append({"role": "assistant", "content": new_scrapper})

        print(f"DataGPT: {new_scrapper}")
        try:
            response = execute_scrapper(new_scrapper)
            return response
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
            new_scrapper=modify_python_code(new_scrapper)

            messages.append({"role": "assistant", "content": new_scrapper})

            print(f"DataGPT: {new_scrapper}")
            response = download_file_scraper(new_scrapper, "xlsx")
            return response
        
def error_messages(e,last_three_lines):
            #add error messages to a different function
    if isinstance(e, Exception) and str(e) == "No rows are in the Dataset":
        error_message = f"There are no records in the dataset. The dataframe is empty, please update the code to resolve this error, only send back the code, do not send back any other text."
    elif type(e).__name__ == "SyntaxError":
        error_message = f"Please only reply with python code, do not send back any other text."
    elif type(e).__name__ == "ValueError":
        error_message = f"This is the error I am getting: {last_three_lines[-1]},Please update the code to resolve this error, only reply with python code, do not send back any other text."
    elif type(e).__name__ == "AttributeError":
        error_message = f"This is the error I am getting: {last_three_lines[0]}.{last_three_lines[1]}.{last_three_lines[2]},Please update the code to resolve this error, only reply with python code, do not send back any other text."
    elif type(e).__name__ == "KeyError":
        error_message = f"This is the error I am getting: {last_three_lines[2]},Please update the code to resolve this error, only reply with python code, do not send back any other text."
    else:
        error_message = f"This is the error I am getting: {last_three_lines[1]}. {last_three_lines[2]}. Please update the code to resolve this error, only send back the code, do not send back any other text other than the python code."
    #return error message    
    return error_message

def web_scrapper(query,link,result_dict,message):
    messages = [
    {"role": "system", "content": "You are a developer. You need to write python code to scrape this website:" + link + ". Write the code for a python scrapper, the dataset the user is looking for is " + query + ". The user will share a snippet from the source code of the website. Analyze the source code to find elements and class names that you need to scrape if necessary. For eg: wiki tables might often have th as well as td in their tables as records which causes errors in the scrappers you write, so you can analyze the source code to see which columns/records are th and which is td. Remember that there might be advertisements on the website so make sure the scrapper is scrapping throughout the entire website using find all. Make sure you add coloumn titles, Scrape and return the data only in a Excel file. The name of the excel file should be Dataset. Only return Python Code, do not return any other words other than the code. If the data is behind a paywall reply with only not_possible, but only if it is behind a paywall, if you are only able to scrape parts of the dataset the user is looking for its fine, reply with the code anyways"},
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
    if reply == "not_possible":
        return reply,"",""

    messages.append({"role": "assistant", "content": reply})
    scraper=reply
    attempts = 0
    while attempts < 4:
        try:
            response,df,num_rows = execute_scrapper(scraper)
            if num_rows <=3:
                raise Exception("No rows are in the Dataset")
            return response,df,num_rows
        except Exception as e:
            if attempts == 3:
                print(f"Error occurred: {e}")
                break
            # Get last line of error message
            error_lines = traceback.format_exc().strip().split("\n")
            last_three_lines = error_lines[-3:]
            print(f"Error occurred: {error_lines}")
            # print(f"Error occurred: {last_three_lines}")
            error_message = error_messages(e,last_three_lines)
            print(f"{error_message}")

            messages.append(
                        {"role": "user", "content": f"{error_message}"},
                    )
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            new_scraper = chat.choices[0].message.content

            messages.append({"role": "assistant", "content": new_scraper})

            print(f"DataGPT: {new_scraper}")
            scraper = new_scraper
            attempts += 1

    return "not_possible","",""
def execute_scrapper(scraper):
    scraper=clean_gpt_output(scraper)
    scraper=modify_python_code(scraper)
    print(scraper)
    response, df, num_rows = scrape_and_preview(scraper)

    return response,df,num_rows

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
def modify_python_code(code_str):
    # Find the line that writes the dataframe to an excel file
    # Find the line that writes the dataframe to an excel file
    excel_line_start = code_str.find(".to_excel(")
    excel_line_end = code_str.find(")", excel_line_start) + 1
    excel_line = code_str[excel_line_start:excel_line_end]

    # Remove the entire line from the code string
    excel_line_start = code_str.rfind("\n", 0, excel_line_start) + 1
    excel_line_end = code_str.find("\n", excel_line_start)
    if excel_line_end == -1:
        excel_line_end = len(code_str)
    code_str = code_str[:excel_line_start] + code_str[excel_line_end:]
    # Remove the line from the code string
   
    
    return code_str
def download_file_scraper(df, file_type):

    
    # Get the DataFrame object from the dictionary
    df = df
    # Create a BytesIO object to hold the file data
    file_buffer = io.BytesIO()

    # Write the DataFrame object to the buffer, depending on the file type
    if file_type == 'csv':
        df.to_csv(file_buffer, index=False)
    elif file_type == 'xlsx':
        df.to_excel(file_buffer, index=False)

    # Create a Flask response object with the file data
    response = flask.make_response(file_buffer.getvalue())

    # Set the appropriate Content-Type header
    if file_type == 'csv':
        response.headers['Content-Type'] = 'text/csv'
    elif file_type == 'xlsx':
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    # Set the Content-Disposition header to force download of the file
    response.headers['Content-Disposition'] = 'attachment; filename=data.' + file_type

    return response

def scrape_and_preview(scraper_code):
    # Create an empty dictionary to store the variables defined inside the exec function
    exec_globals = {}

    # Execute the scraper code in the exec function, passing the empty dictionary as the global namespace
    exec(scraper_code, exec_globals)

    # Get the DataFrame object from the dictionary
    df = exec_globals.get('df')

    # Get the total number of rows in the DataFrame
    num_rows = len(df)

    # Get the first, middle, and last rows of the DataFrame
    preview_rows = pd.concat([df.head(5),df.tail(5)])
    #df.iloc[len(df)//2:len(df)//2+1]],

    # Generate an HTML table for the preview rows
    preview_html = preview_rows.to_html(index=False)

    # Create a Flask response object with the preview HTML
    response = flask.make_response(preview_html)

    # Set the appropriate Content-Type header
    response.headers['Content-Type'] = 'text/html'

    return response, df , num_rows
#   scraped_data[idx] = {'preview': preview, 'num_rows': num_rows, 'type': type}
#check for each website if type is preview, then add it to response array
def create_response(scraped_data):
    response = []
    for data in scraped_data:
        if data['type'] == 'preview':
            response.append({
                'preview': data['preview'],
                'num_rows': data['num_rows'],
                'type': data['type']
            })
    #if response is empty, then return a message
    if len(response) == 0:
        sorry_message = "Sorry! We couldn't find anything for your query. Please simplify your query and try again."
        response.append({
            'message': sorry_message,
            'num_rows': 0,
            'type': 'error'
        })
    return response


app = Flask(__name__)
app.secret_key = 'abdahvyqf9uquofb'

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


@app.route('/', methods=['GET', 'POST'])
def index():
     return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
        isNormalExecution = False
        isParallelExecution = True
        isParallelExecutionThreading = False
        # query = request.form['query']
        query = request.get_json().get('message')
        configure()
        websites=search_results(query)
        json_string = important_columns(query) #ChatGPT will Print the JSON string
        cleaned_json_string = clean_gpt_response_to_json(json_string)
        # print(cleaned_json_string)
        result_dict = convert_json_to_dict(cleaned_json_string) 
        print(result_dict)
        json_string2=rank_websites(query,websites,result_dict)
        try:
            result_list = convert_json_to_list(json_string2)
            print(result_list)
            #check if length of result list is less than 5, then raise exception 
            if len(result_list) < 5:
                raise Exception("Less than 5 results")
        except:
            json_string2=rank_websites(query,websites,result_dict)
            result_list = convert_json_to_list(json_string2)
            
        scraped_data = []
        request_id = uuid.uuid4()

        if isNormalExecution == True:
            for i in range(0, 5):
                website = result_list[i][1]
                print(website)
                preview,df,num_rows,type = execute_functions(website,query,result_dict)
                if type == 'preview':
                    scraped_data.append({'preview': preview, 'num_rows': num_rows, 'type': type})
                    response = create_response(scraped_data)
                    print(response)
                    return flask.jsonify(response=response)
                    # return flask.jsonify(preview=preview, num_rows=num_rows, type= 'preview', df=df.to_json())
                # if type == 'error':
                #     return flask.jsonify(message=preview, type= 'error' )
            return flask.jsonify(response=response )
        elif isParallelExecution == True:
                pool = Pool(processes=5)

                # Use starmap_async to execute execute_functions for each website
                execute_with_args = partial(execute_functions, query=query, result_dict=result_dict)

                # Use imap_unordered to execute execute_functions for each website
                results = pool.imap_unordered(execute_with_args, [result_list[i][1] for i in range(0, 5)])
                # Get the results from the multiprocessing pool
                print("This is the result list:")
                for result in results:
                    print(" Scrapper Execution Complete:")
                    print(result)
                    preview,df,num_rows,type = result
                    if type == 'preview':
                        scraped_data.append({'preview': preview, 'num_rows': num_rows, 'type': type})
                        response = create_response(scraped_data)
                        print(response)
                        kill_other_processes()
                        return flask.jsonify(response=response)
                
                

                pool.close()
                pool.join()
                return flask.jsonify(response=response)
        #threading instead of procceses (concurrency instead of parrelisim), needs more refinement, gets stuck a lot and is slow, and stop_process_pool() doesn't work
        elif isParallelExecutionThreading == True:

                with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(execute_functions, result_list[i][1], query, result_dict) for i in range(0, 3)]
                    for idx, future in enumerate(concurrent.futures.as_completed(futures, timeout=1800)):
                        preview, df, num_rows, type = future.result()
                        scraped_data.append({'preview': preview, 'num_rows': num_rows, 'type': type})
                        # check if type success, then break
                        if type == 'preview':
                            print(scraped_data)
                            response = create_response(scraped_data)
                            print(response)
                            # doesnt stop the other threads
                            stop_process_pool(executor)
                            return flask.jsonify(response=response)
                print(scraped_data)
                response = create_response(scraped_data)
                print(response)
                return flask.jsonify(response=response)

def kill_other_processes():
    for p in mp.active_children():
        #print active children processes
        print ("Child process name: %s" % p.name)
        print ("Terminating process %d" % p.pid)

        if p != mp.current_process():
            #terminate process
            print ("Terminating process %d" % p.pid)
            p.terminate()
            p.join()

    
    for p in mp.active_children():
        #print active children processes
        #check if alive
        if p.is_alive():
            print("Child process is still running.")
        else:
            print("Child process has terminated.")

        print ("Child process name: %s" % p.name)
        print ("Terminating process %d" % p.pid)




        
            

#doesn't work, doesnt stop the other threads
def stop_process_pool(executor):
    for process in executor._processes.values():
        process.terminate()
    executor.shutdown()

def not_premium_execution(result_list,query,result_dict):
        for i in range(0, 5):
            source_code = get_source_code(result_list[i][1])
            print(source_code)
            try:
                response, df, num_rows = web_scrapper(query, result_list[i][1], result_dict, source_code)
                
            except Exception as e:
                print(f"Moving on To next Website because: {e}")
                # print("too much tokens")
                continue
            if response != "not_possible":

                # session['df'] = df.to_json()
                # return flask.render_template('index.html', preview_html=response.data.decode('utf-8'),num_rows=num_rows, df=df)
                return response.data.decode('utf-8'), df, num_rows, "preview"

        return "Sorry! We couldn't find anything for your query. Please simplify your query and try again.","","","error"

def execute_functions(website,query,result_dict):
        with app.app_context():
            source_code = get_source_code(website)
            print(source_code)
            try:
                response, df, num_rows = web_scrapper(query, website, result_dict, source_code)
                
            except Exception as e:
                print(f"Moving on To next Website because: {e}")
                # print("too much tokens")
                response = "not_possible"
            if response != "not_possible":

                # session['df'] = df.to_json()
                # return flask.render_template('index.html', preview_html=response.data.decode('utf-8'),num_rows=num_rows, df=df)
                return response.data.decode('utf-8'), df, num_rows, "preview"
            return "Sorry! We couldn't find anything for your query. Please simplify your query and try again.","","","error"

    
def premium_execution(website,query,result_dict,request_id,i):
        with app.app_context():
            source_code = get_source_code(website)
            print(source_code)
            try:
                response, df, num_rows = web_scrapper(query, website, result_dict, source_code)
                
            except Exception as e:
                print(f"Moving on To next Website because: {e}")
                # print("too much tokens")
                exit()
            if response != "not_possible":
                word= str(request_id)+str(i)
                # session[word] = df.to_json()
                # return flask.render_template('index.html', preview_html=response.data.decode('utf-8'),num_rows=num_rows, df=df)
                return response.data.decode('utf-8'), df, num_rows, "preview"
            else:
                return "Sorry! We couldn't find anything for your query. Please simplify your query and try again.","","","error"


def scrape_old():
        # query = request.form['query']
        query = request.get_json().get('message')
        configure()
        websites=search_results(query)
        json_string = important_columns(query) #ChatGPT will Print the JSON string
        cleaned_json_string = clean_gpt_response_to_json(json_string)
        # print(cleaned_json_string)
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
                response, df, num_rows = web_scrapper(query, result_list[i][1], result_dict, source_code)
                
            except Exception as e:
                print(f"Moving on To next Website because: {e}")
                # print("too much tokens")
                continue
            if response != "not_possible":
                # configure session type to filesystem


                session['df'] = df.to_json()
                # return flask.render_template('index.html', preview_html=response.data.decode('utf-8'),num_rows=num_rows, df=df)
                return flask.jsonify(preview=response.data.decode('utf-8'), num_rows=num_rows, type= 'preview', df=df.to_json())

        return flask.jsonify(message="Sorry! We couldn't find anything for your query. Please simplify your query and try again.", type= 'error')

@app.route('/get_flashed_messages')
def get_flashed_messages():
    messages = flask.session.pop('_flashes', [])
    if messages:
        return '<ul class="flashes">{}</ul>'.format(''.join('<li>{}</li>'.format(msg) for msg in messages))
    else:
        return 'Hello'

@app.route("/download")
def download_excel():
    df = pd.read_json(session['df'])    
    response=download_file_scraper(df, 'xlsx')

    
    return response

if __name__ == '__main__':
    app.run(host="0.0.0.0",port="5000")
# https://sharegpt.com/c/HeqAGXz
# https://sharegpt.com/c/C7wUG5v
# https://sharegpt.com/c/DlIK6uQ
# https://sharegpt.com/c/Ve3t0yN
# configure()
# query=input("What data are you looking for?: ")
# websites=search_results(query)

# json_string = important_columns(query) #ChatGPT will Print the JSON string
# cleaned_json_string = clean_gpt_response_to_json(json_string)
# print(cleaned_json_string)
# result_dict = convert_json_to_dict(cleaned_json_string) 
# print(result_dict)
# json_string2=rank_websites(query,websites,result_dict)
# try:
#     result_list = convert_json_to_list(json_string2)
#     print(result_list)
# except:
#     json_string2=rank_websites(query,websites,result_dict)
#     result_list = convert_json_to_list(json_string2)

# for i in range(0, 5):
#     source_code = get_source_code(result_list[i][1])
#     print(source_code)
#     try:
#         scraper = web_scrapper(query, result_list[i][1], result_dict, source_code)
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         print("too much tokens")
#         continue
#     if scraper != "not_possible":
#         break
        
    # add the code that runs when web_scrapper succeeds here





# rank_websites(query,"https://pib.gov.in/PressReleaseIframePage.aspx?PRID=1806254 https://www.statista.com/statistics/1061130/india-population-of-pet-dogs/ https://timesofindia.indiatimes.com/life-style/relationships/pets/popular-dog-breeds/articleshow/60132107.cms https://dahd.nic.in/sites/default/filess/Breeding%20Survey%20Book%20-%20Corrected.pdf https://en.wikipedia.org/wiki/List_of_dog_breeds_from_India https://en.wikipedia.org/wiki/List_of_most_popular_dog_breeds https://vikaspedia.in/agriculture/agri-directory/reports-and-policy-briefs/20th-livestock-census https://www.nddb.coop/information/stats/pop https://nbagr.icar.gov.in/wp-content/uploads/2021/11/NBAGR-Annual-Report-2020.pdf https://highlandcanine.com/the-50-most-popular-dog-breeds-in-the-world-2019/")