from pyspark.sql import SparkSession
from pyspark.ml.feature import Word2Vec
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer
import json

# Создаем Spark сессию
spark = SparkSession.builder.appName("NewsWord2Vec").getOrCreate()

# Пример структуры данных
with open("data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)
data = []
for i in raw_data:
    data.append(tuple(i))
# Создаем DataFrame
schema = ["news"]
df = spark.createDataFrame(data, schema)

# Токенизация текста новостей
tokenizer = Tokenizer(inputCol="news", outputCol="words")
word_data = tokenizer.transform(df)

# Создаем модель Word2Vec
word2Vec = Word2Vec(vectorSize=100, minCount=1, inputCol="words", outputCol="result")
model = word2Vec.fit(word_data)

# Сохраняем модель
model.save("model/Word2VecModel")


