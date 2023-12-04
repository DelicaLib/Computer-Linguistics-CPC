from typing import List
import requests
import os
import psycopg2
import news_parser
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

connection = psycopg2.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("PORT")
)   

def make_annotation(text: str):
    response = requests.post("https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict", json={
        "instances": [
            {
                "text" : text
            }
        ]
    }).json()
    if "detail" in response:
        raise requests.exceptions.RequestException("Ошибка суммаризатора: " + response["detail"])
    
    if response['comment'] == "Ok!":
        return response["prediction_best"]["bertscore"]

    raise requests.exceptions.RequestException("Ошибка суммаризатора: " + response['comment'])

def rewrite_text(text: str) -> dict:
    response = requests.post("https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict", json={
        "instances": [
            {
                "text" : text,
                "num_return_sequences" : 5,
                "top_k" : 50,
                "top_p" : 0.7,
                "temperature" : 0.9
            }
        ]
    }).json()
    if "detail" in response:
        raise requests.exceptions.RequestException("Ошибка рерайтера: " + response["detail"])
    
    if "comment" not in response:
        response["comment"] = "Ok!"
        return response["prediction_best"]["bertscore"]

    raise requests.exceptions.RequestException("Ошибка рерайтера: " + response['comment'])


def insert_original_news(news : news_parser.News, cursor : psycopg2.extensions.cursor):
    news.header=news.header.replace("'", "\"")
    news.text=news.text.replace("'", "\"")
    cursor.execute(f"INSERT INTO original_news VALUES(DEFAULT, '{news.header}', '{news.link}', '{news.text}', '{news.date}')")
    
def insert_edited_news(original_news_id: int, annotation : str, text : str, cursor : psycopg2.extensions.cursor):
    annotation=annotation.replace("'", "\"")
    text=text.replace("'", "\"")
    cursor.execute(f"INSERT INTO edited_news VALUES(DEFAULT, '{annotation}', '{text}', {original_news_id})")

def main():
    with connection.cursor() as cursor:
        for i in range(235,10001):
            print(f"Page {i} started")
            news : List[news_parser.News] = news_parser.parse_page(i)
            for j in range(len(news)):
                insert_original_news(news[j], cursor)
                cursor.execute("SELECT * FROM original_news ORDER BY id_ DESC LIMIT 1")
                annotation = make_annotation(news[j].text)
                rewrited_text = rewrite_text(news[j].text)
                original_news_id = cursor.fetchone()[0]
                insert_edited_news(original_news_id, annotation, rewrited_text, cursor)
                print(f"added {j + 1} news")
                connection.commit()
            print(f"Page {i} finished\n\n")
    

if __name__=="__main__":
    main()