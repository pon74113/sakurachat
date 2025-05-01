
from flask import Flask, request, jsonify, render_template
import http.client
import json
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

NOUS_API_HOST = "inference-api.nousresearch.com"
NOUS_API_PATH = "/v1/chat/completions"
NOUS_API_KEY = "sk-4NosuJ3S2SjajcLEdoUSag"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask_ai():
    data = request.json
    user_question = data.get("question", "")

    try:
        conn = http.client.HTTPSConnection(NOUS_API_HOST)
        payload = {
            "model": "DeepHermes-3-Mistral-24B-Preview",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a thoughtful, helpful assistant. Reply in the same language as the user's question."
                },
                {"role": "user", "content": user_question}
            ],
            "max_tokens": 256
        }

        headers = {
            'Authorization': f"Bearer {NOUS_API_KEY}",
            'Content-Type': "application/json"
        }

        conn.request("POST", NOUS_API_PATH, body=json.dumps(payload), headers=headers)
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))

        if "choices" in response_data:
            reply = response_data["choices"][0]["message"]["content"]
        else:
            reply = "❌ Failed to get response from API\n\n" + json.dumps(response_data, indent=2)

        estimated_tokens = int(len(user_question) / 4 + len(reply) / 4)
        cost_per_1k_tokens = 0.002
        estimated_cost = round((estimated_tokens / 1000) * cost_per_1k_tokens, 6)

    except Exception as e:
        reply = f"❌ Error: {str(e)}"
        estimated_cost = 0.0

    return jsonify({
        "reply": reply,
        "cost": f"${estimated_cost:.6f}"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
