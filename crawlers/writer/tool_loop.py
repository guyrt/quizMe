import json

from azurewrapper.openai_client import OpenAIClient
from writer.quality_response import RelevantDataChecker
from writer.tools.bing_search import Bing
from writer.tools.wikipedia import Wikipedia

from .tools.base import Tool

import logging


class Sec(Tool):
    name = "CompanyFinancialDetails"
    description = (
        "A wrapper around data that companies file with the Securities Exchange Commission. "
        "Useful for specific questions about a company that files with the SEC. "
        "Useful for information about the financial health of a company, but does not have its stock price."
        "Financial data that gets reported in a quarterly report is available. "
        "Input should a search topic or query. Do not ask for a specific type of document. Ask a question that the SEC bot can use to search in docs."
    )


class YahooFinance(Tool):
    name = "FinanceNewsAPI"
    description = (
        "Useful for when you need to find recent financial news about a public company. "
        "Input should be a company ticker. "
        "For example, AAPL for Apple, MSFT for Microsoft."
    )


class YahooFinanceFact(Tool):
    name = "StockPrice"
    description = (
        "This tool contains only the following information: daily stock prices, sector name for a stock."
        "Input should be a company ticker. "
        "For example, AAPL for Apple, MSFT for Microsoft."
    )


class ToolLoop:
    def __init__(self, oai: OpenAIClient) -> None:
        self._oai = oai
        self._tools: list[Tool] = [
            Wikipedia(),
            YahooFinance(),
            Sec(),
            YahooFinanceFact(),
            Bing(),
        ]
        self._checker = RelevantDataChecker(self._oai)

    def loop(self, question: str) -> str:
        """TODO: return a fact set. Need to define type, but these must have attributes!"""
        print(f"--------- {question} ----------")
        known_facts = []
        all_responses = []

        total_turns = 0
        max_turns = 3

        while total_turns < max_turns:
            total_turns += 1

            prompt = self._build_prompt(question, all_responses)
            print(f"Prompt length: {len(prompt)}")
            raw_response_d = self._oai.call(prompt)
            raw_response = raw_response_d["response"]
            print(raw_response)

            responses = self._parse_response(raw_response)
            all_responses.append(raw_response)
            # TODO: store responses and pass to the prompt. not known facts...

            for response in responses:
                response_tool = response["tool"]
                found_tool = False

                if response_tool == "stop":
                    break

                for tool in self._tools:
                    if tool.name == response_tool:
                        found_tool = True
                        new_facts = tool.run(response["input"])

                        for new_fact in new_facts:
                            self._checker.is_relevant(question, new_fact.value)

                        # TODO: run a checker. is the tool/input any good? is the response useful/

                        if new_facts:
                            known_facts.extend(new_facts)

                if not found_tool:
                    logging.warn(f"No tool found for response {response_tool}")
            else:
                continue
            break

        return known_facts

    def _parse_response(self, raw_response: str):
        try:
            raw = json.loads(raw_response)
        except json.JSONDecodeError as e:
            print(f"Failed to parse {raw_response}: {e}")
            return []
        return raw

    def _build_prompt(self, question, known_facts):
        s_tools = "\n\n".join(
            [f"Tool Name: {t.name}\nDescription: {t.description}" for t in self._tools]
        )

        if known_facts:
            s_tools += "\n\nTool Name: Stop\n"
            s_tools += "Description: Call the stop tool if there is sufficient information in the Known Facts section to answer the question. You should only call the Stop tool if there is some information in the Known Facts section."

        # Consider moving this to a set of convo rounds with an "anything else".
        main_prompt = f"""You are a financial analyst assistant who helps compiles research reports. Our reports are known for their factual accuracy, depth, and detail.
Your specific task is to gather data that will help answer the question. Your job is not to generate a specific answer to the question. You only help to gather sources
that would be helpful. 

Your should respond with a JSON list of dictionaries. Each response is a dictionary with three keys:
"tool": name of the tool to use. 
"input": a query to pass to the tool
"reason": a brief reason why you chose this tool and input.


You may request more than one tool in a response, and you may suggest the same tool more than once with a different input, but each ToolName must have exactly one input.

For example:
```
[ 
    {{
    "tool": "CompanyFinancialDetails",
    "input": "Has Recursion Pharmaceuticals faced any regulatory issues in the past?",
    "reason": "Regulatory complains must be included in quarterly reports and in 8-k filings."
    }},
    {{
        "tool": "bing_search",
        "input": "What is the total size of the pharamaceutical industry?",
        "reason": "Industry size is a specific question and Bing is good at that."
    }}
]
```

Your tools are listed here:

{s_tools}


That is all of the tools you have available. Do not repeat the same tool and input combination in multiple answers.
""".strip()

        p = [
            {"role": "system", "content": main_prompt},
            {"role": "user", "content": question},
        ]
        if known_facts:
            for kf in known_facts:
                p.append({"role": "assistant", "content": kf})
                p.append(
                    {
                        "role": "user",
                        "content": "can you think of any more? do not repeat previous answers. Always include a reason.",
                    }
                )

        return p
