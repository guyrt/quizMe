from intelligence.openai_client import OpenAIClient


class Tool:

    name = "name"
    description = "dummy"

    # TODO: always must log a query and a source that comes back from tool.
    # This is how we'll track provenance.


class Wikipedia(Tool):

    name = "wikipedia"
    description = (
        "A wrapper around Wikipedia. Usefor for when you need to answer general "
        "questions about people, places, companies, industries, or historical events."
        "Input should be a search query."           
    )


class Bing(Tool):

    name = "bing_search"
    description = (
        "A wrapper around Bing Search. "
        "Useful to answer questions about current events including news. "
        "Provides less detail than wikipedia, but is more likely to contain "
        "information that is up to date. "
        "Is very helpful for specific questions. "
        "Input should be a search query. If you are asking for background information about a company's market "
        "or industry, do not include the company name in the search term. "
    )


class Sec(Tool):

    name = "SecurityExchangeCommission"
    description = (
        "A wrapper around a search engine for Securities Exchange Commission documents. "
        "Contains every document uploaded to the SEC. "
        "Useful for specific questions about a company that files with the SEC including quarterly reports and 8-K filings. "
        "Useful for information about the financial health of a company, but does not have its stock price or "
        "data that requires a stock price to compute like PE Ratios. "
        "Input should be a CIK and a search topic or query."
    )


class YahooFinance(Tool):

    name = "FinanceNewsAPI"
    description = (
        "Useful for when you need to find recent financial news about a public company. "
        "Input should be a company ticker. "
        "For example, AAPL for Apple, MSFT for Microsoft."
    )


class YahooFinanceFact(Tool):

    name = "FinanceFactsAPI"
    description = (
        "Useful for when you need to get financial data about a company that cannot be retrieved from the SEC."
        "this API will return current and historical stock prices, financial measures of interest to investors like PE Ratio "
        "and details about the sector of a company. "
        "Input should be a company ticker. "
        "For example, AAPL for Apple, MSFT for Microsoft."
    )


class ToolLoop:

    def __init__(self, oai : OpenAIClient) -> None:
        self._oai = oai
        self._tools = [
            Wikipedia(),
            YahooFinance(),
            YahooFinanceFact(),
            Sec(),
            Bing()
        ]

    def loop(self, question : str) -> str:
        """TODO: return a fact set. Need to define type, but these must have attributes!"""
        known_facts = []
        prompt = self._build_prompt(question, known_facts)
        response = self._oai.call([{'role': 'system', 'content': prompt}])
        print(question)
        print(response)
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
Input: 000728391, Has Recursion Pharmaceuticals faced any regulatory issues in the past?
Reason: Regulatory complains must be included in quarterly reports and in 8-k filings.

ToolName: bing_search
Input: What is the total size of the pharamaceutical industry?
Reason: Industry size is a specific question and Bing is good at that.
```

Your tools are listed here:

{s_tools}


That is all of the tools you have available. If no tool seems suitable, then default to the bing_search tool.

The question is:
{question}

Known Facts:
{s_known_facts}
""".strip()
        return main_prompt