import os
from flask import Flask, request, abort
from bot import telegram_bot, handle_update

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


@app.route("/webhook/<secret>", methods=["POST"])
def webhook(secret):
    if secret != WEBHOOK_SECRET:
        abort(403, "Forbidden")

    if request.method == "POST":
        update = request.get_json(force=True, silent=True)
        if update:
            handle_update(update)
        return "OK"
    return "Bad Request", 400


@app.route("/health")
def health():
    return "OK"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
