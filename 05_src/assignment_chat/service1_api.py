import requests
import xml.etree.ElementTree as ET

BASE_URL = "https://retro.umoiq.com/service/publicXMLFeed"

import os
from openai import OpenAI
from dotenv import load_dotenv

# Loading API key from secret.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, "../.secrets")
load_dotenv(dotenv_path, override=True)
API_KEY = os.getenv("API_GATEWAY_KEY")

# Creating an OpenAI client.
client = OpenAI(
    base_url = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
    api_key = os.getenv("API_GATEWAY_KEY"),
    default_headers = {"x-api-key": os.getenv("API_GATEWAY_KEY")}
)


def get_next_arrivals(stop_id: str) -> list[str]:
    try:
        params = {
            "command": "predictions",
            "a": "ttc",
            "stopId": stop_id
        }

        response = requests.get(BASE_URL, params=params, timeout=10)

        if response.status_code != 200:
            return [f"API error. Status code: {response.status_code}"]

        root = ET.fromstring(response.text)

        results = []
        structured_data = []

        for predictions in root.findall("predictions"):
            route = predictions.get("routeTag")
            route_title = predictions.get("routeTitle")

            for direction in predictions.findall("direction"):
                direction_title = direction.get("title")

                for prediction in direction.findall("prediction"):
                    minutes = prediction.get("minutes")

                    if route and minutes:
                        if int(minutes) <= 5:
                            status = "arriving soon"
                        elif int(minutes) > 20:
                            status = "delayed"
                        else:
                            status = "on schedule"

                        structured_data.append({
                            "route": route,
                            "minutes": minutes,
                            "direction": direction_title,
                            "status": status
                        })

        # after loop
        if not structured_data:
            return ["No upcoming arrivals found."]

        summary = summarize_arrivals(structured_data[:3])
        return [summary]

    except Exception as e:
        return [f"Error fetching data: {e}"]
    
def summarize_arrivals(data: list[dict]) -> str:
    try:
        prompt = f"""
        Summarize the next TTC arrivals in 1-2 short sentences.
        Highlight if any bus is arriving soon (<=5 mins) or delayed (>20 mins).
        Keep it concise.
        Data:
        {data}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return "Could not generate summary."