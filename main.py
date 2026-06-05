import os
import requests
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
CAMPAIGN_ID = "149145902"


def ok_response():
    return jsonify({
        "name": "puytutick-digital",
        "version": "1.0",
        "time": datetime.now(timezone.utc).isoformat(),
        "status": "OK"
    }), 200


def get_promo_by_sku(shop_sku, offer_name=""):
    text = f"{shop_sku} {offer_name}".lower()

    if "19" in text:
        return "PUYTUTICK19", "19%"

    if "10" in text:
        return "PUYTUTICK10", "10%"

    return "PUYTUTICK19", "19%"


def build_slip_text(promo_code, discount):
    return f"""
Ваш промокод: {promo_code}

Размер скидки: {discount}

Срок действия: 6 месяцев.

Промокод активируется через 24 часа после получения.

Инструкция:
1. Подпишитесь на магазин.
2. Выберите нужный товар.
3. Добавьте товар в корзину.
4. При оформлении заказа введите промокод {promo_code}.

Важно:
• Для применения скидки необходимо быть подписанным на магазин.
• Скидка не суммируется с другими акциями.
• Один промокод можно использовать один раз.

Спасибо за покупку!
"""


@app.route("/", methods=["GET"])
def home():
    return "PuyTutick Digital OK", 200


@app.route("/webhook", methods=["POST"])
@app.route("/webhook/notification", methods=["POST"])
def webhook():
    data = request.json
    print("Webhook:", data)

    if not data:
        return ok_response()

    if data.get("notificationType") == "PING":
        return ok_response()

    order_id = (
        data.get("orderId")
        or data.get("order", {}).get("id")
        or data.get("id")
    )

    if not order_id:
        return ok_response()

    try:
        order_response = requests.get(
            f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}",
            headers={"Api-Key": API_KEY}
        )

        order_data = order_response.json()
        print("Order:", order_data)

        order = order_data.get("order", {})

        if order.get("status") != "PROCESSING":
            return ok_response()

        item = order["items"][0]
        item_id = item["id"]
        shop_sku = item.get("shopSku", "")
        offer_name = item.get("offerName", "")

        promo_code, discount = get_promo_by_sku(shop_sku, offer_name)
        slip_text = build_slip_text(promo_code, discount)

        body = {
            "items": [
                {
                    "id": item_id,
                    "codes": [promo_code],
                    "activate_till": "2026-12-31",
                    "slip": slip_text
                }
            ]
        }

        send = requests.post(
            f"https://api.partner.market.yandex.ru/v2/campaigns/{CAMPAIGN_ID}/orders/{order_id}/deliverDigitalGoods",
            headers={
                "Api-Key": API_KEY,
                "Content-Type": "application/json"
            },
            json=body
        )

        print("SHOP SKU:", shop_sku)
        print("Offer name:", offer_name)
        print("Promo:", promo_code)
        print("Deliver response:", send.status_code)
        print(send.text)

    except Exception as e:
        print("ERROR:", e)

    return ok_response()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
