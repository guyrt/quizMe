from intelligence.openai_client import OpenAIClient
from writer.tools.bing_search import Bing
from writer.tools.wikipedia import Wikipedia

from .tools.base import Tool



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

    def __init__(self, oai : OpenAIClient) -> None:
        self._oai = oai
        self._tools = [
            Wikipedia(),
            YahooFinance(),
            Sec(),
            YahooFinanceFact(),
            Bing()
        ]

    def loop(self, question : str) -> str:
        """TODO: return a fact set. Need to define type, but these must have attributes!"""
        known_facts = []
        prompt = self._build_prompt(question, known_facts)
        response = self._oai.call(prompt)

        import ipdb; ipdb.set_trace()
        return known_facts


    def _build_prompt(self, question, known_facts):

        s_known_facts = "\n".join(known_facts)
        s_tools = '\n\n'.join([f"Tool Name: {t.name}\nDescription: {t.description}" for t in self._tools])

        if known_facts:
            s_tools += "\n\nTool Name: Stop\n"
            s_tools += "Description: Call the stop tool if there is sufficient information in the Known Facts section to answer the question. You should only call the Stop tool if there is some information in the Known Facts section."

        # Consider moving this to a set of convo rounds with an "anything else".
        main_prompt = f"""You are a financial analyst assistant who helps compiles research reports. Our reports are known for their factual accuracy, depth, and detail.
Your specific task is to gather data that will help answer the question. Your job is not to generate a specific answer to the question. You only help to gather sources
that would be helpful. 

Every response should contain three lines:
Tool name to use
Input to tool
Reason you chose this tool


You may request more than one tool in a response, and you may suggest teh same tool more than once with a different input, but each ToolName must have exactly one input.

For example:
```
ToolName: SecurityExchangeCommission
Input: Has Recursion Pharmaceuticals faced any regulatory issues in the past?
Reason: Regulatory complains must be included in quarterly reports and in 8-k filings.

ToolName: bing_search
Input: What is the total size of the pharamaceutical industry?
Reason: Industry size is a specific question and Bing is good at that.
```

Your tools are listed here:

{s_tools}


That is all of the tools you have available. If no tool seems suitable, then default to the bing_search tool.
""".strip()
        
        p = [
            {'role': 'system', 'content': main_prompt},
            {'role': 'user', 'content': question},
        ]
        if s_known_facts:
            p.append({'role': 'agent', 'content': s_known_facts})

        return p