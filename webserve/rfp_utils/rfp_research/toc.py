from azurewrapper.prompt_types import Prompt, PromptCell


toc_system_prompt = """Your job is to extract a Table of Contents from a document. 

There are many errors you might see:
- Words have extra spaces in them. You should rewrite the text with the spaces removed.
- New lines are in the wrong place or missing. 
- If you think some text represents a table then reproduce it in a table. This will not always be true. Only output a table if the structure of the input implies it's a table. 
- The text may include headers and footers that restate the section or document name and that contain page numbers. You should ignore these headers and footers and not return them. 

DO NOT reword text other than correcting formatting errors as described above. 

Sometimes, the table of contents will have more than one layer, so you can see a parent/child relationship. Here's an example:

Section 1   My childhood     - 1
Section 1.1 - My preschool years - 4
1.1.1 - my friends   - 6
Section 1.1.2 - my hobbies - 6
Section 1.2 - grade school  - 12
Section 2. colle ge  - 15
Section 3. my jobs  - 31
Section 3.1 something  - 34

APPENDIX A  - 51

Return the table of contents in JSON structure. Here's the expected format, using the example above:

```
[
   {{"number": "1", "title": "My childhood", "parent": "none", "page": "1"}},
   {{"number": "1.1", "title": "My preschool years", "parent": "1", "page": "4"}},
   {{"number": "1.1.1", "title": "my friends", "parent": "1.1", "page": "6"}},
   {{"number": "1.1.2", "title": "my hobbies", "parent": "1.1", "page": "6"}},
   {{"number": "1.2", "title": "Grade school", "parent": "1", "page": "12"}},
   {{"number": "2", "title": "college", "parent": "none", "page": "15"}},
   {{"number": "3", "title": "my jobs", "parent": "none", "page": "31"}},
   {{"number": "3.1", "title": "something", "parent": "3", "page": "34"}},
   {{"number": "A", "title": "APPENDIX A", "parent": "none", "is_appendix": "true", "page": "51"}},
]
```

It's important to use a common format for sections other than Appendices. You should uniformly exclude words like "Section". 
"""


table_of_contents_extract_prompt = Prompt(
    name="TOCExtract",
    content=[
        PromptCell(role="system", content=toc_system_prompt),
        PromptCell(role="user", content="{doc_content}"),
    ],
    version=1,
)
