import requests
import datetime
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=10, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


class News:
    header: str
    link: str
    text: str
    date: datetime.datetime

    def __init__(self, header, date, link, text) -> None:
        self.header = header
        self.date = date
        self.link = link
        self.text = text

    def __str__(self) -> str:
        return f"{self.header}\n{self.link}\n\n{self.text}\n {self.date}"


def parse_datetime(datetime_: str):
    datetime_now = datetime.datetime.now()

    if datetime_.find("минут") != -1:
        time_ago = int(datetime_.split()[0])
        return datetime_now - datetime.timedelta(minutes=time_ago)

    if datetime_.find("сегодня") != -1:
        time_news = datetime_.split(" ")[1]
        datetime_news = datetime_now.replace(hour=int(time_news.split(":")[0]),
                                             minute=int(time_news.split(":")[1]))
        return datetime_news

    if datetime_.find("вчера") != -1:
        time_news = datetime_.split(" ")[1]
        datetime_news = datetime_now.replace(hour=int(time_news.split(":")[0]),
                                             minute=int(time_news.split(":")[1]))
        return datetime_news - datetime.timedelta(days=1)
    if datetime_.find("секунд") != -1:
        return datetime_now

    datetime_format = "%d.%m.%Y %H:%M"
    return datetime.datetime.strptime(datetime_, datetime_format)


def parse_from_bloknot_russia(link: str):
    response = session.get(link)
    data = BeautifulSoup(response.text, "html.parser")
    news_text = []
    date_news = parse_datetime(data.find("time", class_="article__timestamp").text)
    for j in data.find_all("p", class_="article__text"):
        for i in j.text.split("\n"):
            if i.strip() != "":
                news_text.append(i.strip())
    news_text.pop()
    news_text.pop()
    news_text.pop()
    return date_news, news_text


def parse_page(page: int):
    response = session.get(f"https://bloknot-volgograd.ru/?PAGEN_1={page}")
    result = []

    data = BeautifulSoup(response.text, "html.parser")
    news_data = data.find("ul", class_="bigline")

    for i in news_data.find_all("li"):
        header = i.find("a", class_="sys").text
        news: News
        link = i.find("a", class_="sys")["href"]
        date_news: datetime.datetime
        news_text: list
        if "https://bloknot-volgograd.ru" in link:
            link = str(link).replace("https://bloknot-volgograd.ru", "")
        if "https" in link:
            date_news, news_text = parse_from_bloknot_russia(link)
            print("Парсим", link)
        else:
            link = "https://bloknot-volgograd.ru" + link
            print("Парсим", link)
            response_news_text = session.get(link)
            data_news_text = BeautifulSoup(response_news_text.text, "html.parser")
            news_text = []
            date_news = parse_datetime(data_news_text.find("span", class_="news-date-time").text)
            for i in data_news_text.find("div", class_="news-text").text.split("\n"):
                if i.strip() != "":
                    news_text.append(i.strip())
            news_text.pop()
            news_text.pop()
        news = News(header, date_news, link, "\n".join(news_text))
        result.append(news)

    return result


def main():
    for i in parse_page(707):
        print(i)
        print("\n")


if __name__ == "__main__":
    main()
