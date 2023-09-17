import json
from dataclasses import dataclass
from typing import List

from intelligence.openai_client import OpenAIClient

from writer.writer_types import Plan, Section, Topic

import logging


class Planner:

    def __init__(self, oai : OpenAIClient) -> None:
        self._oai = oai

    def make_plan(self, goal : str) -> Plan:
        """
        Create a Plan with sections and questions.
        """
        outline = self.create_outline(goal)
        for section in outline.sections:
            for topic in section.topics:
                self.add_facts(goal, topic)

        return outline

    def create_outline(self, goal : str) -> Plan:
        system = f"""You are a financial analyst assistant who helps compiles research reports. Our reports are known for their factual accuracy, depth, detail, and humor.

Our client has given us a contract to write a prospectus on this question:
{goal}

Please develop an outline for a report on that topic.

You should answer in a list JSON format. Each element in the list is a report section. Use this structure:
```json
[
    {{
        "title": "name of the report section"
        "topics": [
            {{
                "name": "topic1",
                "description": "a detailed, one sentence description of that topic."
            }}
        ]
    }}
]
```

Each section should have between 4 and 10 topics. You should have between 10 and 15 sections. It's ok to be long because we will edit the content in a later step.
""".strip()

        response = self._oai.call([{'role': 'system', 'content': system}])
        try:
            structured_response = json.loads(response)
        except json.decoder.JSONDecodeError as e:
            logging.error(f"Failed to decode outline: {e}")
            raise e  # TODO - try to correct it! Use a "go make better JSON" prompt.
        else:
            sections = [Section(name=s['title'], topics=_make_topics(s['topics'])) for s in structured_response]
            plan = Plan(sections=sections)
            return plan

    def add_facts(self, goal : str, topic : Topic):
        system = f"""You are a financial analyst assistant who helps compiles research reports. Our reports are known for their factual accuracy, depth, detail, and humor.

Our client has given us a contract to write a prospectus on this question:
{goal}

One of the topics we will discuss is
{topic.name}: {topic.description}

Create a list of questions that we should answer or facts we should gather in order to write about this topic. 

Answer with one question on each line and do not include formatting like bullet points. There should be 1 to 10 questions per line. Be thorough.

If the topic is a summary then there are no new questions needed so you should return an empty list.

Do not try to answer the questions or provide detailed facts. Describe the fact or question and we will look it up later.

Do not include questions about the report itself. Your job is to decide what specific facts to include or questions we need to answer to meet our objective.
""".strip()
        
        response = self._oai.call([{'role': 'system', 'content': system}])
        structured_response = [r.strip() for r in response.split('\n')]
    
        topic.questions = structured_response
        print(f"Added {len(structured_response)} topics")
        return topic





def _make_topics(d : List[any]) -> List[Topic]:
    return [Topic(name=t['name'], description=t['description']) for t in d]