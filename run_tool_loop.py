from writer.tool_loop import ToolLoop
from intelligence.openai_client import OpenAIClient

oai = OpenAIClient()
p = ToolLoop(oai)
#p.loop("What is the size of the retail industry that Costco operates in?")

#p.loop("What are the major competitors of Costco in the retail industry?")

#p.loop("What are Costco's competitive advantages over its competitors?")

#p.loop("What are the current trends in the retail industry?")

p.loop("What is COSTCO's revenue trend over the past few years?")