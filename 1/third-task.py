import json, requests

updated_post = {"userId": 10,
            "id" : 100,
            "title" : "Обновленный пост",
            "body" : "11010000 10011111 11010000 10111110 11010000 10111010 11010000 10110000"}

json_response = requests.put('https://jsonplaceholder.typicode.com/posts/100', json = updated_post)
if json_response.ok:
    data = json_response.json()
    print(json.dumps(data, ensure_ascii = False, indent=3))
else:
    print(json_response.status_code)


# Суть задания немного непонятна -- на сайте не добавляется новый пост, который я создал на 2 пункте. Отсюда вопрос - как обновить то, чего не существует на сайте? Сотый пост спокойно обновился
# На сайте написано - Important: resource will not be really updated on the server but it will be faked as if. Значит - все ок?