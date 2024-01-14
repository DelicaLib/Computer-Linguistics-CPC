from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

import tomita
import sentiment

app = FastAPI(docs_url="/")


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
