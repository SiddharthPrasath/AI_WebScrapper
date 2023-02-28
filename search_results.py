from googlesearch import search

query=input("Enter your query: ")
for url in search(query, tld="co.in", stop=10):
    print(url)

