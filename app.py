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
        return jsonify({"error": "Aucune image fournie"}), 400

    image_data = data["image"]
    if "," in image_data:
        header, image_data = image_data.split(",", 1)
        media_type = header.split(":")[1].split(";")[0]
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
                                "Voici une liste de courses. "
                                "Extrais tous les articles. "
                                "Réponds UNIQUEMENT avec un tableau JSON de chaînes de caractères. "
                                "Exemple : [\"pommes\", \"lait\", \"pain\"]. "
                                "Aucune explication, aucun markdown, juste le tableau JSON."
                            ),
                        },
                    ],
                }
            ],
        )

        text = response.content[0].text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]).strip()

        items = json.loads(text)
        if not isinstance(items, list):
            raise ValueError("Expected a list")
        items = [str(i).strip() for i in items if str(i).strip()]
        return jsonify({"items": items})

    except (json.JSONDecodeError, ValueError):
        lines = [l.strip().lstrip("-•*·").strip() for l in text.splitlines() if l.strip()]
        return jsonify({"items": lines})
    except anthropic.APIError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
