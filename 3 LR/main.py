import sqlite3
import requests
# python -m venv venv
# .\venv\Scripts\activate
# pip install -r .\requirments.txt

def create_db():
    connection = sqlite3.connect('3 LR/posts.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        title TEXT,
        body TEXT
    )
    ''')

    connection.commit()
    connection.close()

def fetch_posts():
    url = 'https://jsonplaceholder.typicode.com/posts'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print('You can not get data from the server')
        return []

def save_posts(posts):
    connection = sqlite3.connect('3 LR/posts.db')
    cursor = connection.cursor()

    for post in posts:
        cursor.execute('''
        INSERT INTO posts (id, user_id, title, body) 
        VALUES (?, ?, ?, ?)
        ''', (post['id'], post['userId'], post['title'], post['body']))

    connection.commit()
    connection.close()

def get_posts_by_user(user_id):
    connection = sqlite3.connect('3 LR/posts.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
    posts = cursor.fetchall()

    connection.close()

    for post in posts:
        print(f"ID: {post[0]}, User ID: {post[1]}, Title: {post[2]}, Body: {post[3]}")

def get_all_posts():
    
    conn = sqlite3.connect('3 LR/posts.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM posts')

    posts = cursor.fetchall()

    conn.close()

    for post in posts:
        print(f"ID: {post[0]}, User ID: {post[1]}, Title: {post[2]}, Body: {post[3]}")



# по заданию
create_db()  
posts = fetch_posts()  
save_posts(posts)  
get_posts_by_user(1)

#get_all_posts()