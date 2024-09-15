import requests, json

r = requests.get('https://jsonplaceholder.typicode.com/posts/')
data = r.json()
mas = [i for i in data if i['userId'] % 2 == 0]
print(json.dumps(mas, indent=4))