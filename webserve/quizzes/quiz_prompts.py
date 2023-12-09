from azurewrapper.prompt_types import Prompt, PromptCell

system = """I'm trying to retain the information from this blog post. Please help me by coming up with five multiple choice questions about the content. Write questions that make me understand the point about the article, not easy facts like the author. The ideal question requires me to synthesize the thesis of the author.

Always answer by first stating the thesis and major claims or points in the article. Then write the questions. Always write them in this JSON format:

```
[
{{
    "question": "This is a question",
    "answers": [
    {{"answer": "answer 1"}},
    {{"answer": "answer 2", "correct": 1}},
    {{"answer": "answer3"}}
    ...
    ]
}}
]
```

Mark exactly one answer as correct for each question.
"""

quiz_gen = Prompt(
    name='SimpleQuizGen',
    content=[
        PromptCell(role='system', content=system),
        PromptCell(role='user', content='Write questions for this article: \n"{doc_content}"')
    ],
    version=1
)
