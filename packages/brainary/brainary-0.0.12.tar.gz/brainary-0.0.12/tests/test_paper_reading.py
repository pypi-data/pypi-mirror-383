from typing import List
import brainary
from brainary.util.logging_util import init_logging

@brainary.tool
def get_weather(city: str) -> str:
    '''
    Retrieve current weather information for a given city.
    
    Args:
        city (str): the city.
        
    Returns:
        str: The weather information.
    '''
    return "sunny"
    
    

init_logging("log/tests/paper_reading.log")

brainary.install_vm("gpt-4o-mini", temperature=0, experience_base="tests/experience_base", experience_learning=True)

Paper = brainary.define_type(
    type_name="Paper",
    text={"type": str, "desc": "paper content"},
)
p1 = Paper(text=open("tests/paper1.txt", "r").read().strip())
p2 = Paper(text=open("tests/paper2.txt", "r").read().strip())

summarize = brainary.define_action(
    "Perform a literature review based on the given papers.",
    ("paper_list",),
    attentions=["combination", "limitations"],
    output_constraints={"tone": "rigorous"},
    tools=[get_weather])
summarize(paper_list=[p1, p2])


