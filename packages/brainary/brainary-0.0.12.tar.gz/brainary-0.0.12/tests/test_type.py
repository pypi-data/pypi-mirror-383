import brainary


Review = brainary.define_type(
    type_name="Review",
    text={"type": str, "desc": "review content"},
    author={"type": str, "desc": "reviewer name"}
)
Movie = brainary.define_type(
    type_name="Movie",
    title={"type": str, "desc": "movie title"},
    year={"type": int, "desc": "release year"},
    reviews={"type": list[Review], "desc": "list of Review objects"}
)
m = Movie(
    title='Matrix',
    year=1999,
    reviews=[Review(text="Amazing!", author="Bob")]
)
print(m)  # 'Matrix'
print(m.to_dict())  # {'title': 'Matrix', 'year': 1999, 'reviews': [...]}x