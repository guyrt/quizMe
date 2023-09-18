from writer.planner import Planner
from writer.writer_types import serialize_plan
from azurewrapper.openai_client import OpenAIClient

oai = OpenAIClient()
p = Planner(oai)
plan = p.make_plan("What is the outlook for Costco?")

s = serialize_plan(plan)
f = open("samples/sample_plan.json", 'w')
f.write(s)
f.close()
