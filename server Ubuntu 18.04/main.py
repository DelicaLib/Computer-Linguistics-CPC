from fastapi import FastAPI
from typing import List
from pydantic import BaseModel
import json
from pyspark.sql import SparkSession
from pyspark.ml.feature import Word2VecModel
from pyspark.ml.feature import Tokenizer

import tomita
import sentiment

app = FastAPI(docs_url="/")

spark = SparkSession.builder.appName("SynonymSearch").getOrCreate()
model = Word2VecModel.load("synonyms/model/Word2VecModel")


def get_synonyms(word: str) -> List[str]:
    if len(word.split()) > 1:
        return ["Это не одно слово"]
    data = [(word,)]
    schema = ["news"]
    df = spark.createDataFrame(data, schema)
    tokenizer = Tokenizer(inputCol="news", outputCol="words")
    word_data = tokenizer.transform(df)
    vector = model.transform(word_data).select("result").collect()[0]["result"]
    synonyms = model.findSynonyms(vector, 5)
    synonyms_list = synonyms.select("word").rdd.flatMap(lambda x: x).collect()
    return synonyms_list


class PostRequest(BaseModel):
    text: str


@app.post("/persons", response_model=List[str])
def get_persons(req: PostRequest):
    return tomita.find_people(req.text)


@app.post("/places", response_model=List[str])
def get_persons(req: PostRequest):
    return tomita.find_places(req.text)


@app.post("/sentiment_analyze", response_model=str)
def do_sentiment_analyze(req: PostRequest):
    while True:
        try:
            if len(req.text) == 0:
                return "Не удалось выяснить"
            return sentiment.sentiment_analyze(req.text)
        except:
            req.text = req.text[:-min(512, len(req.text))]


@app.post("/send_data", response_model=str)
def save_data(data: List[str]):
    with open("synonyms/data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    return "Ok"


@app.post("/synonyms", response_model=List[str])
def save_data(req: PostRequest):
    return get_synonyms(req.text)
