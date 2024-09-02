import requests
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()


class Messages(BaseModel):
    id: str
    user_id: str
    username: str
    message: dict[str, str]


def check_text(lang, text):
    url = "https://api.languagetool.org/v2/check"
    params = {
        "text": text,
        "language": lang
    }
    response = requests.post(url, data=params)
    result = response.json()

    corrections = []
    for match in result.get("matches", []):
        # Extract error text
        error_text = text[match["offset"]:match["offset"] + match["length"]]

        # Extract all the corrections inside all the text
        suggestions = [replacement["value"] for replacement in match.get("replacements", [])]

        corrections.append({
            "error": error_text,
            "corrections": suggestions
        })

    return corrections


def apply_corrections(text, corrections):
    for correction in corrections:
        if correction['corrections']:
            text = text.replace(correction['error'], correction['corrections'][0])
    return text


@app.get("/")
async def process_texts(texts: Messages):
    for lang, msg in texts.message.items():
        try:
            # First check
            corrections = check_text(lang, msg)
            corrected_text = apply_corrections(msg, corrections)

            print(f"Language: {lang}")
            print(f"Original text: {msg}")

            print(f"Text after corrections: {corrected_text}")
            print_corrections("Final corrections", corrections)
            return corrected_words

        except Exception as e:
            print(f"Error processing language {lang}: {e}")


corrected_words = []


def print_corrections(title, corrections):
    print(f"{title}:")
    if corrections:
        for correction in corrections:
            print(f"  Error: {correction['error']}")
            if correction['corrections']:
                print(f"    Correction: " + correction['corrections'][0])
                corrected_words.append(correction['corrections'][0])
    else:
        print("  No corrections found.")
