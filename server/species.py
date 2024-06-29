def get_species_comments(doc):

    ENDANGERED_SPECIES_ANALYSIS_PROMPT = f"""
You are an expert legal analyst tasked with analyzing an Environmental Impact Statement (EIS) for a proposed development project.

The EIS may mention the impact on one or more endangered species. Here is the complete list of current endangered species in the United States:

```csv
{species.to_csv()}
```

Identify any and ALL species from the list above mentioned in the EIS and provide a summary of the impact on the endangered species mentioned in the document. Cite the specific sections and text from the EIS that mention species from the list above. Be comprehensive - ensure if a species is mentioned both in the document and the list above, that it is flagged for review.
""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ENDANGERED_SPECIES_ANALYSIS_PROMPT},
            {"role": "user", "content": doc_chunks[0]},
        ],
    )
