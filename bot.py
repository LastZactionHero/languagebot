import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file
load_dotenv()

client = OpenAI(
    # Load the API key from the .env file
    api_key=os.getenv("OPENAI_API_KEY"),
)


def generate(history, instruction):
    # Truncate to the last 50 messages
    truncated_history = history[-50:]

    # Add instructions to the history
    truncated_history.append({"role": "system", "content": instruction})

    chat_completion = client.chat.completions.create(
        messages=truncated_history,
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


history = []

PROMPT = """You are a Japanese-language conversation tutor for a beginner student. Continue the conversation in simple Japanese, not much more than a single sentence.

You will output in the following JSON format:

{
    "corrections": "Any corrections to the student's sentence, in English (weird or incorrect words, etc)",
    "response_ja": "Japanese-language response to the student's last sentence, e.g. 私は食べます。",
    "response_hiragana": "Phoenetic version of your Japanese-langauge response",
    "response_en": "English-language translation to your response",
    // Definition of every word in your response, word-by-word
    "words": [
        { "english": "I", "hiragana": "わたし", "kanji": "私", },
        { "english": "eat", "hiragana": "たべる", "kanji": "食べる" }
    ]
}
"""

import json

last_response = None

while True:
    user_text = input("User: ").strip()

    if user_text == "[q]":
        break
    elif user_text == "[d]":
        if last_response is not None:
            for word in last_response["words"]:
                print("{} - {} - {}", word["english"], word["hiragana"], word["kanji"])
    elif user_text == "[en]":
        if last_response is not None:
            print(last_response["response_en"])
    else:
        user_message = {"role": "user", "content": user_text}
        history.append(user_message)
        response = generate(history, PROMPT)

        try:
            response_json = json.loads(response)
        except json.JSONDecodeError:
            print("An error occurred while parsing JSON.")
            history.pop()
            continue

        last_response = response_json
        bot_message = {"role": "assistant", "content": response_json.get("response_ja", "")}
        history.append(bot_message)

        if response_json['corrections'] is not None and len(response_json['corrections']) > 0:
            print("Corrections: ", response_json['corrections'])

        print("先生: ", response_json.get("response_ja", ""))
        print("先生: ", response_json.get("response_hiragana", ""))
