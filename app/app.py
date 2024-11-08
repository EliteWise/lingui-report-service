import datetime

import requests
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename="report.log", level=logging.INFO)


class Messages(BaseModel):
    id: str
    user_id: str
    username: str
    messages: List[Dict[str, str]]


class Report(BaseModel):
    id: str
    user_id: str
    username: str
    corrected_words: List[Dict[str, str]]
    process_date: datetime.date


def check_text(lang, text):

    """
    Check the given text using Language Tool API.

    Args:
        lang (str): Language of the text.
        text (str): Text to be checked.

    Returns:
        List[Dict[str, str]]: A list of corrections. Each correction is a dictionary with two keys: "error" and "corrections". "error" is the text that has an error, and "corrections" is a list of suggestions for the error.
    """

    url = "https://api.languagetool.org/v2/check"
    params = {
        "text": text,
        "language": lang
    }
    response = requests.post(url, data=params)
    logger.info("Language Tool Status Code: " + str(response.status_code))
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
    """
    Replace all the words with corrections in the given text.

    Args:
        text (str): The text to be corrected.
        corrections (List[Dict[str, str]]): The list of corrections to be applied to the text.

    Returns:
        str: The corrected text.
    """
    for correction in corrections:
        if correction['corrections']:
            text = text.replace(correction['error'], correction['corrections'][0])
    return text


corrected_words = []


@app.post("/")
async def process_texts(texts: Messages):
    """
    Process a list of texts and return a report with the number of corrections done in each text
    """
    corrected_words.clear()
    for message in texts.messages:
        lang = message.get("lang")
        msg = message.get("text")
        try:
            # First check
            corrections = check_text(lang, msg)
            corrected_text = apply_corrections(msg, corrections)

            logger.info(f"Language: {lang}")
            logger.info(f"Original text: {msg}")

            logger.info(f"Text after corrections: {corrected_text}")
            print_corrections("Final corrections", corrections)

        except Exception as e:
            logger.info(f"Error processing language {lang}: {e}")

    return Report(id=texts.id, user_id=texts.user_id, username=texts.username, corrected_words=corrected_words, process_date=datetime.date.today())


def print_corrections(title, corrections):
    logger.info(f"{title}:")
    if corrections:
        for correction in corrections:
            logger.info(f"  Error: {correction['error']}")
            if correction['corrections']:
                logger.info(f"    Correction: " + correction['corrections'][0])
                corrected_words.append({correction['error']: correction['corrections'][0]})
    else:
        logger.info("  No corrections found.")