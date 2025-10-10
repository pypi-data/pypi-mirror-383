# Brainary

Brainary is a Python framework for building cognitive architectures that integrate LLMs, self-regulation, and multiple capabilities such as reasoning, planning, and evaluation.


## Archtecture Overview
<img src="./brainary-arch.png" alt="Arch Overview" style="width:75%;height:auto;">

## Installation

```bash
pip install brainary
```

## Usage

Create a configure file **llm.yml** to specify the `API key` or `Base Url` for OpenAI client creation. Note that, many LLM services (e.g., DeepSeek) or serving frameworks (e.g., vLLM) are compatible with OpenAI client library, you can refer to their docs to configure the `API key` or `Base Url`.

```yaml
# llm.yml
api-key: sk-proj-...

# base-url: http://...
```

An example:
```python
from typing import List
import brainary
from brainary.util.logging_util import init_logging

init_logging()

brainary.install_vm("gpt-4o-mini")

Review = brainary.define_type(
    type_name="Review",
    text={"type": str, "desc": "review content"},
    author={"type": str, "desc": "reviewer name"}
)
Movie = brainary.define_type(
    type_name="Movie",
    name={"type": str, "desc": ""},
    year={"type": int, "desc": "release year"},
    reviews={"type": List[Review], "desc": "reviews of the movie"}
)
r1 = Review(text="When this came out, I was living with a roommate. He went out and saw it, came home and said, \"Dude, you have to go see The Matrix.\" So we left and he sat through it a second time. This movie is splendidly done. The mystery about what the Matrix is, unravels and you see a dystopian future unlike any we as a race would want. I have watched this over and over and never tire of it. Everyone does a great job acting in this, the special effects are above par and the story is engaging.", author="acedj")
r2 = Review(text="This was a real change in filmmaking. Like watching it again in 2020, i.e. after 21 years and it still feels fresh. Iconic scenes are still having benchmarks setting up.\n\nIf we say it sci-fi at its best, it won't be wrong. The hype was real, it is still not easy to match the level of Matrix where we experience the connection of humans and science, that too with amazing action fight and chase scenes, not just normal scenes they were, multiple exposures, slow motion 3D moves, Oh My God, and it's understandable as well like what are the characters up to and what storyline they are entering into. The script was very well written and executed otherwise it could have been a mess. A special appreciation in managing the theme with those black color costumes and a scientific zone with unimaginable equipment and props doing unbelievable things in the two worlds created. No spoilers, but the action scenes in the climax where the protagonist goes to save someone from agents are really breathtaking. The technology used at its best.\n\nA salute to Wachowski Brothers and the team for creating this masterpiece. It will be a great competition and motivation as well for many films coming in the future.", author="suryanmukul")
m = Movie(name="Matrix", year=1999, reviews=[r1, r2])

if brainary.examine("The sentiment of the review is negative.", review=r1):
    print("===== Negative Review =====")

summarize = brainary.define_action("Summarize the movie reviews.", "movie", attentions=["sentiment", "character"], output_constraints={"tone": "grandiloquent"})
summarize(movie=m)
```