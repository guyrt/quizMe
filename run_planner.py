from writer.planner import Planner
from intelligence.openai_client import OpenAIClient

oai = OpenAIClient()
p = Planner(oai)
p.make_plan("What is the outlook for Recursion Pharmaceuticals?")
