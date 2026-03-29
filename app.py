import os
import base64
import json
from flask import Flask, request, jsonify, render_template
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    image_data = data["image"]
    # Strip the data URL prefix if present
    if "," in image_data:
        media_type_part, image_data = image_data.split(",", 1)
        media_type = media_type_part.split(":")[1].split(";")[0]
    else:
        media_type = "image/jpeg"

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "This is a shopping list. Extract all items from it. "
                                "Return ONLY a JSON array of strings, one item per entry. "
                                "Example: [\"apples\", \"milk\", \"bread\"]. "
                                "No explanation, no markdown, just the JSON array."
                            ),
                        },
                    ],
                }
            ],
        )

        text = response.content[0].text.strip()
        # Clean up any markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        items = json.loads(text)
        return jsonify({"items": items})

    except json.JSONDecodeError:
        # If Claude didn't return valid JSON, try to parse line by line
        lines = [line.strip("- •*").strip() for line in text.splitlines() if line.strip()]
        return jsonify({"items": lines})
    except anthropic.APIError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
