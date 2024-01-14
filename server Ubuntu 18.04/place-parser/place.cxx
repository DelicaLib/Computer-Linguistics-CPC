#encoding "utf-8"
#GRAMMAR_ROOT Place

place -> Word<kwtype=place>;
Place -> place interp(BestPlace.Place);
