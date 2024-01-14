#encoding "utf-8"
#GRAMMAR_ROOT Person

person -> Word<kwtype=OnePerson>;
Person -> person interp(VIPPerson.Person);
