

def get_region(doc, sites):

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

Each item field should be separated by a comma, no whitespace, and MUST be an exact match with one of the items in the list above.

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
            {"role": "user", "content": doc},
        ],
        response_format={"type": "json_object"},
    )

    return json.loads(resp.choices[0].message.content)


def get_historic_sites_comments(doc_chunk):

    locations = get_region(doc_chunks[0])

    # Filter for states, counties, and cities mentioned in the document
    relevant_sites = sites[
        sites["State"].isin(locations["states"])
        & sites["County"].isin(locations["counties"])
        & sites["City "].isin(locations["cities"])
    ]

    HISTORIC_SITES_COMMENTS_PROMPT = f"""
    You are an expert legal analyst tasked with analyzing an Environmental Impact Statement (EIS) for a proposed development project.

    Here is a list of sites of national historic importance in the United States located int the region of the proposed development project:

    {relevant_sites.to_markdown()}

    Carefully read the document - the EIS may mention one or more of these sites. If it does, cite the specific text and comment on how it might contribute to a greater risk, specifically in relation to the following:
    * If sites are mentioned, are they being handled correctly?
    * Look for mentions of section 106 of historic preservation act.
    * If sites are mentioned, are did state historic preservation officers (SHPOs) or tribal historic preservation officers (THPOs) mentioned?
    """.strip()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": HISTORIC_SITES_COMMENTS_PROMPT},
            {"role": "user", "content": doc_chunk},
        ],
    )

    return resp.choices[0].message.content
