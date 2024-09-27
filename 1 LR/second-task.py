import json, requests

new_post = {"userId": 10,
            "id" : 101,
            "title" : "Тестовый пост",
            "body" : "11010000 10011111 11010001 10000000 11010000 10111000 11010000 10110010 11010000 10110101 11010001 10000010"}

json_response = requests.post('https://jsonplaceholder.typicode.com/posts', json = new_post)
if json_response.ok:
    data = json_response.json()
    print(json.dumps(data, ensure_ascii = False, indent=3))
else:
    print(json_response.status_code)
