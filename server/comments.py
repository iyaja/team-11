import openai
import pymupdf4llm
import pymupdf
import json
from fuzzysearch import find_near_matches
from langchain.text_splitter import MarkdownTextSplitter

client = openai.Client()

PROMPT = """
The following is an Environmental Impact Statement (EIS).

Read it carefully and assess the following risk factors that may pose regulatory hurdles for the project:
1. Endangered Species
2. Tribal Lands
3. National Historic Sites

Cite and comment on specific text in the document that is most relevant to the risk factors above. Respond with the following format:

```json
{
    "comments" : [
        {
            "quote": "Some exact text from the document",
            "risk_factor": "Which of the above risk factors does this quote relate to?",
            "comment": "Describe how the quoted text could introduce regulatory burden related to the risk factor",
        },
        ...
    ]
}
```

Return only valid JSON. DO NOT include any other text in your response.
""".strip()


def find_comments_in_doc(doc, comments):
    aligned_comments = []
    for c in comments:
        quote = c["quote"]
        # Perform fuzzy search to find approximate matches
        try:
            closest_match = find_near_matches(quote, doc, max_l_dist=5)[0]
        except IndexError:
            continue

        aligned_comments.append(
            {
                "quote": {
                    "start": closest_match.start,
                    "end": closest_match.end,
                    "text": doc[closest_match.start : closest_match.end],
                },
                "comment": c["comment"],
            }
        )

    return aligned_comments


def get_comments_for_doc(doc):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": doc},
        ],
        response_format={"type": "json_object"},
    )

    response_object = json.loads(response.choices[0].message.content)

    comments = []
    for c in response_object["comments"]:
        quote = c["quote"]
        # Perform fuzzy search to find approximate matches
        try:
            closest_match = find_near_matches(quote, doc, max_l_dist=5)[0]
        except IndexError:
            continue

        comments.append(
            {
                "quote": {
                    "start": closest_match.start,
                    "end": closest_match.end,
                    "text": doc[closest_match.start : closest_match.end],
                },
                "comment": c["comment"],
                "metadata": {
                    "risk_factor": c["risk_factor"],
                },
            }
        )

    return {
        "markdown": doc,
        "comments": comments,
    }
