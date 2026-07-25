# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params += key + "=" + value + "&"

    request_url = backend_url + endpoint

    if params:
        request_url = request_url + "?" + params[:-1]

    print("GET from {}".format(request_url))

    try:
        response = requests.get(request_url)
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())
        return response.json()
    except Exception as e:
        print(f"Network exception occurred: {e}")


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    print("Analyzing Review:", request_url)

    try:
        response = requests.get(request_url)
        result = response.json()

        if response.status_code == 200:
            return result
        else:
            return {
                "sentiment": "neutral"
            }

    except Exception as err:
        print("Error analyzing review sentiments:", err)
        return {
            "sentiment": "neutral"
        }


def post_review(data_dict):
    request_url = backend_url + "/insert_review"

    try:
        response = requests.post(request_url, json=data_dict)

        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    except Exception as e:
        print(f"Error posting review: {e}")
        return None
