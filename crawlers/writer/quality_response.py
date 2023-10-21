from azurewrapper.openai_client import OpenAIClient


class RelevantDataChecker:

    def __init__(self, oai : OpenAIClient) -> None:
        self._oai = oai

    def is_relevant(self, question, data):
        """Say whether a piece of content is relevant to a question"""

        prompt = """You will always get two pieces of information: a question and a passage of text. Your job is to say whether the
content is relevant to answer the question. Always answer with only yes or no on first line. On second line give a reason.
"""

        example1_q = """Question: Costco revenue trend analysis
Passage: 'Costco Wholesale Corporation is a company that operates a chain of big-box retail stores which resemble warehouses and sells a wide variety of wholesale products. Unlike most big-box stores,...
""".strip()
        example1_a = """no
The passage describes Costco's business but doesn't talk about revenue."""

        example2_q = """Question: Costco revenue trend analysis
Passage: Since resuming the Costco name in 1997, the company has grown worldwide with total sales in recent fiscal years exceeding $192 billion. Costco has transformed the retail world. When entrepreneur Sol Price introduced a groundbreaking retail concept in San Diego, California. Price Club was the world's first membership warehouse club, a place ..."""
        example2_a = """yes
The passage describes growing sales with recent total of $192 billion."""

        example3_q = """Question: What is the size of the retail industry that Costco operates in?
Passage: Overview. World: retail sales 2021-2026. Total retail sales worldwide from 2021 to 2026 (in trillion U.S. dollars) World: leading retailers 2021, by retail revenue. Leading retailers..."""
        example3_a = """no
The passage is on topic but does not include the answer to the question."""

        input = f"""Question: {question}
Passage: {data}
""".strip()

        response_d = self._oai.call([
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': example1_q},
            {'role': 'assistant', 'content': example1_a},
            {'role': 'user', 'content': example2_q},
            {'role': 'assistant', 'content': example2_a},
            {'role': 'user', 'content': example3_q},
            {'role': 'assistant', 'content': example3_a},
            {'role': 'user', 'content': input}
        ])
        response = response_d['response']
        print(response)
        return response

