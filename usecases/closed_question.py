from ner_utils import closed_question

question = "Who directed The Bridge on the River Kwai?"
print(closed_question(question))


question = "Who is the director of Star Wars: Episode VI - Return of the Jedi? "
print(closed_question(question))


question = "What is the genre of Good Neighbors?  "
print(closed_question(question))

question = "Who is the screenwriter of The Masked Gang: Cyprus?   "
print(closed_question(question))

question = "What is the MPAA film rating of Weathering with You? "
print(closed_question(question))


question = "When was \"The Godfather\" released?  "
print(closed_question(question))

question = "Who is the director of Good Will Hunting? "
print(closed_question(question))
