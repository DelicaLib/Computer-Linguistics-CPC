CREATE DATABASE news;
CREATE TABLE original_news(
	id_ SERIAL PRIMARY KEY,
	header_ VARCHAR(511) NOT NULL,
	link_ VARCHAR(256) NOT NULL,
	text_ text NOT NULL,
	date_ TIMESTAMP NOT NULL,
	temperature_ VARCHAR(250)
)
CREATE TABLE edited_news(
	id_ SERIAL PRIMARY KEY,
	annotation_ TEXT NOT NULL,
	rewrote_text_TEXT NOT NULL,
	news_id_ SERIAL REFERENCES original_news(id_)
)
CREATE TABLE persons(
	id_ SERIAL PRIMARY KEY,
	fio_ VARCHAR(250) NOT NULL
)
CREATE TABLE places(
	id_ SERIAL PRIMARY KEY,
	name_ VARCHAR(250) NOT NULL
)
CREATE TABLE persons_in_news(
	id_ SERIAL PRIMARY KEY,
	news_id_ SERIAL REFERENCES original_news(id_),
	person_id_ SERIAL REFERENCES persons(id_)
)
CREATE TABLE places_in_news(
	id_ SERIAL PRIMARY KEY,
	news_id_ SERIAL REFERENCES original_news(id_),
	place_id_ SERIAL REFERENCES places(id_)
)