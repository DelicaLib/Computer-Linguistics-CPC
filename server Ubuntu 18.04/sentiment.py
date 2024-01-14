from transformers import pipeline
model = pipeline(model="seara/rubert-base-cased-russian-sentiment")


def sentiment_analyze(text: str):
    result = model(text)[0]
    output_str = ""
    if result["label"] == "neutral":
        output_str = "Нейтральная"
    elif result["label"] == "positive":
        output_str = "Позитивная"
    else:
        output_str = "Негативная"
    output_str = f"{output_str} на {round(result['score'] * 100)}%"
    return output_str
