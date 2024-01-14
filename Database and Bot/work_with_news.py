import time
from typing import List
import requests
import os
import psycopg2
import news_parser
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=20, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

connection = psycopg2.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("PORT"))
)


def make_annotation(text: str):
    text_list = []
    it = 0
    while it < len(text):
        text_list.append(text[it:min(it + 20000, len(text))])
        it += 20000
    res = []
    for j in text_list:
        response = None
        for i in range(10):
            response = session.post("https://api.aicloud.sbercloud.ru/public/v2/summarizator/predict",
                                    allow_redirects=True, json={
                                        "instances": [
                                            {
                                                "text": j
                                            }
                                        ]
                                    })

            print("Суммаризатор статус:", response.status_code)
            if response.status_code == 200:
                break
            time.sleep(5)
        if response.status_code != 200:
            raise requests.exceptions.RequestException("Ошибка рерайтера: " + str(response.status_code))
        response = response.json()
        if "detail" in response:
            raise requests.exceptions.RequestException("Ошибка суммаризатора: " + response["detail"])

        if "comment" in response:
            if response["comment"] == "Ok!":
                res.append(response["prediction_best"]["bertscore"])
            else:
                raise requests.exceptions.RequestException("Ошибка суммаризатора: " + response['comment'])
    return "".join(res)


def rewrite_text(text: str) -> str:
    text_list = []
    it = 0
    while it < len(text):
        text_list.append(text[it:min(it + 20000, len(text))])
        it += 20000
    res = []
    for j in text_list:
        response = None
        for i in range(10):
            try:
                response = session.post("https://api.aicloud.sbercloud.ru/public/v2/rewriter/predict",
                                        allow_redirects=True, json={
                                            "instances": [
                                                {
                                                    "text": j,
                                                    "top_k": 50,
                                                    "top_p": 0.7,
                                                    "temperature": 0.9
                                                }
                                            ]
                                        })
                print("Рерайтер статус:", response.status_code)
                if response.status_code == 200:
                    break
                time.sleep(5)
            except Exception:
                print("Рерайтер пизда")
                time.sleep(5)
        if response.status_code != 200:
            raise requests.exceptions.RequestException("Ошибка рерайтера: " + str(response.status_code))
        response = response.json()

        if "detail" in response:
            raise requests.exceptions.RequestException("Ошибка рерайтера: " + response["detail"])

        if "comment" not in response:
            if "prediction_best" not in response:
                raise requests.exceptions.RequestException("Ошибка рерайтера: " + response)
            res.append(response["prediction_best"]["bertscore"])

    return "".join(res)


def insert_original_news(news: news_parser.News, sentiment: str, cursor: psycopg2.extensions.cursor):
    news.header = news.header.replace("'", "\"")
    news.text = news.text.replace("'", "\"")
    cursor.execute(
        f"INSERT INTO original_news VALUES(DEFAULT, '{news.header}', '{news.link}', '{news.text}', '{news.date}', '{sentiment}')")


def insert_edited_news(original_news_id: int, annotation: str, text: str, cursor: psycopg2.extensions.cursor):
    annotation = annotation.replace("'", "\"")
    text = text.replace("'", "\"")
    cursor.execute(f"INSERT INTO edited_news VALUES(DEFAULT, '{annotation}', '{text}', {original_news_id})")


def has_news_url_in_bd(url: str) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM original_news WHERE link_='{url}'")
        return cursor.fetchone() is not None


def make_dict_for_bot(news: news_parser.News, annotation: str,
                      rewrote_text: str, persons: List[str],
                      places: List[str], sentiment: str):
    return {"title": news.header,
            "annot": annotation,
            "text": rewrote_text,
            "link": news.link,
            "persons": persons,
            "places": places,
            "sentiment": sentiment}


def get_persons_in_news_from_bd(news_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT fio_ FROM persons WHERE id_ IN (SELECT person_id_ FROM persons_in_news WHERE news_id_ = {news_id})"
        )
        bd_result = cursor.fetchall()
        if bd_result is None:
            return []
        result = []
        for i in bd_result:
            result.append(i[0])
        return result


def get_places_in_news_from_bd(news_id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT name_ FROM places WHERE id_ IN (SELECT place_id_ FROM places_in_news WHERE news_id_ = {news_id})"
        )
        bd_result = cursor.fetchall()
        if bd_result is None:
            return []
        result = []
        for i in bd_result:
            result.append(i[0])
        return result


def get_new_news() -> List[dict]:
    res = []
    with connection.cursor() as cursor:
        print("Поиск новых новостей начат")
        news: List[news_parser.News] = news_parser.parse_page(1)
        for j in range(len(news)):
            if has_news_url_in_bd(news[j].link):
                continue
            sentiment = sentiment_analyze(news[j].text)
            insert_original_news(news[j], sentiment, cursor)
            cursor.execute("SELECT * FROM original_news ORDER BY id_ DESC LIMIT 1")
            annotation = make_annotation(news[j].text)
            rewrote_text = rewrite_text(news[j].text)
            original_news_id = cursor.fetchone()
            if original_news_id is None:
                raise ValueError("В базе данных не нашлось данных")
            original_news_id = int(original_news_id[0])
            set_places_for_one_news(original_news_id, news[j])
            set_persons_for_one_news(original_news_id, news[j])
            insert_edited_news(original_news_id, annotation, rewrote_text, cursor)
            found_persons = get_persons_in_news_from_bd(original_news_id)
            found_places = get_places_in_news_from_bd(original_news_id)
            if len(found_places) == 0 and len(found_persons) == 0:
                sentiment = ""
            res.append(make_dict_for_bot(news=news[j], annotation=annotation,
                                         rewrote_text=rewrote_text, persons=found_persons,
                                         places=found_places, sentiment=sentiment))
            print(f"added {j + 1} news")
            connection.commit()
    print("Поиск новых новостей закончен")
    return res


def sentiment_analyze(text: str):
    print("Проводим анализ тональности новости")
    sentiment_result = session.post(url="http://192.168.0.115:8000/sentiment_analyze", json={"text": text}).json()
    return sentiment_result


def set_persons_for_one_news(news_id: int, news: news_parser.News) -> bool:
    news_text = news.text
    print(f"Ищем персоны в новости {news_id}")
    found_persons = session.post(url="http://192.168.0.115:8000/persons", json={"text": news_text}).json()
    for i in found_persons:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO persons_in_news VALUES(DEFAULT, {news_id}, {i})")
    connection.commit()
    return len(found_persons) > 0


def set_places_for_one_news(news_id: int, news: news_parser.News):
    news_text = news.text
    print(f"Ищем достопримечательность в новости {news_id}")
    found_persons = session.post(url="http://192.168.0.115:8000/places", json={"text": news_text}).json()
    for i in found_persons:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO places_in_news VALUES(DEFAULT, {news_id}, {i})")
    connection.commit()
    return len(found_persons) > 0


def set_persons_places_for_all_news():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM original_news")
        news = cursor.fetchall()
        for i in news:
            set_persons_for_one_news(i[0], news_parser.News(i[1], i[4], i[2], i[3]))
            set_places_for_one_news(i[0], news_parser.News(i[1], i[4], i[2], i[3]))


def main():
    with connection.cursor() as cursor:
        for i in range(1, 2, 2):
            print(f"Page {i} started")
            news: List[news_parser.News] = news_parser.parse_page(i)
            for j in range(len(news)):
                insert_original_news(news[j], cursor)
                cursor.execute("SELECT * FROM original_news ORDER BY id_ DESC LIMIT 1")
                annotation = make_annotation(news[j].text)
                rewrited_text = rewrite_text(news[j].text)
                original_news_id = cursor.fetchone()
                if original_news_id is None:
                    raise ValueError("В базе данных не нашлось данных")
                original_news_id = int(original_news_id[0])
                insert_edited_news(original_news_id, annotation, rewrited_text, cursor)
                print(f"added {j + 1} news")
                connection.commit()
            print(f"Page {i} finished\n\n")


if __name__ == "__main__":
    get_new_news()
