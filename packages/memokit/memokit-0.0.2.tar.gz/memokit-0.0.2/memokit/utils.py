from openai import OpenAI
import os
from functools import partial

def call_openai_function(prompt, base_url, api_key, model):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1

    )

    return response.choices[0].message.content


def call_openai(base_url, api_key, model):
    return partial(
        call_openai_function,
        base_url=base_url,
        api_key=api_key,
        model=model,
    )
