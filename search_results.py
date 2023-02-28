from googlesearch import search

query=input("Enter your query: ")
for url in search(query, stop=10):
    print(url)

