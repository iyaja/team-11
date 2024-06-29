import openai
import pymupdf4llm
import pymupdf
import json
from fuzzysearch import find_near_matches
from langchain.text_splitter import MarkdownTextSplitter
import pandas as pd
import openai
import json
import pymupdf4llm
import pymupdf

client = openai.Client()


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


def get_generic_comments_for_doc(doc):
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


def get_species_comments(doc, species):

    ENDANGERED_SPECIES_ANALYSIS_PROMPT = f"""
You are an expert legal analyst tasked with analyzing an Environmental Impact Statement (EIS) for a proposed development project.

Here is the complete list of current endangered species in the United States:

```csv
{species.to_csv()}
```

Carefully read the document - the EIS may mention one or more of these endangered species. Identify ALL species from the list above mentioned in the EIS, and cite sections of the text that may pose increased risk or scrutiny for the project, specifically with reference to the following criteria:

* Whether it has a reference to a section 7 consultation
* Has a "Biological Assessment"
* Additionally, if any other related species could be impacted by the proposed development, flag it for review, write a suggestion that the developer analyze, and inciting the specific details of that species from the table above.

Respond with the following format:

```json
{{
    "comments" : [
        {{
            "quote": "Exact text quote from the document",
            "comment": "Explanation for how the quoted text could introduce regulatory burden/risk, and what the the developer might need to consider to mitigate this risk.",
        }},
        ...
    ]
}}
```

If no relevant text is found, return an empty list.""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ENDANGERED_SPECIES_ANALYSIS_PROMPT},
            {"role": "user", "content": doc},
        ],
        response_format={"type": "json_object"},
    )

    resp_obj = json.loads(resp.choices[0].message.content)

    return resp_obj


def get_region(doc_chunk, sites):

    all_states = "\n".join(map(str, sites["State"].unique().tolist()))
    all_counties = "\n".join(map(str, sites["County"].unique().tolist()))
    all_cities = "\n".join(map(str, sites["City "].unique().tolist()))

    LOCATION_SEARCH_PROMPT = f"""
The following is a list of cities, counties, and states in the United States:

States:
-------

{all_states}

Counties:
---------

{all_counties}

Cities:
-------

{all_cities}

You will be provided with an Environmental Impact Statement (EIS) for a proposed development project. Identify the states, counties, and cities relevant to this project. Return your response in the following JSON format:

```json
{{
    "states": [""],
    "counties": [""],
    "cities": [""]
}}
```

DO NOT output any other information or text. If the EIS does not mention a state, county, or city, output an empty list for that field.
""".strip()
    # First, find the state from the list of states
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": LOCATION_SEARCH_PROMPT,
            },
            {"role": "user", "content": doc_chunk},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(resp.choices[0].message.content)


def get_historic_sites_comments(doc_chunk, sites):

    locations = get_region(doc_chunk, sites)

    # Filter for states, counties, and cities mentioned in the document
    relevant_sites = sites[
        sites["State"].isin(locations["states"])
        & sites["County"].isin(locations["counties"])
        & sites["City "].isin(locations["cities"])
    ]

    HISTORIC_SITES_COMMENTS_PROMPT = f"""
You are an expert legal analyst tasked with analyzing an Environmental Impact Statement (EIS) for a proposed development project.

Here is a list of sites of national historic importance in the United States located in the region of the proposed development project:

{relevant_sites.to_markdown()}

Carefully read the document - the EIS may mention one or more of these sites. If it does, cite the specific text and comment on how it might contribute to a greater risk, specifically in relation to the following:

* If sites are mentioned, are they being handled correctly?
* Look for mentions of section 106 of historic preservation act.
* If sites are mentioned, are state historic preservation officers (SHPOs) or tribal historic preservation officers (THPOs) mentioned?

Respond with the following format:

```json
{{
    "comments" : [
        {{
            "quote": "Exact text quote from the document",
            "comment": "Explanation for how the quoted text could introduce regulatory burden/risk, and what the the developer might need to consider to mitigate this risk.",
        }},
        ...
    ]
}}
```

If no relevant text is found, return an empty list.""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": HISTORIC_SITES_COMMENTS_PROMPT},
            {"role": "user", "content": doc_chunk},
        ],
        response_format={"type": "json_object"},
    )

    resp_obj = json.loads(resp.choices[0].message.content)

    return resp_obj
