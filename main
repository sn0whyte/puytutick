from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "PuyTutick Digital"

@app.route("/webhook/notification", methods=["POST"])
def webhook():
    data = request.json

    print("Webhook:", data)

    return jsonify({
        "status": "OK"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
