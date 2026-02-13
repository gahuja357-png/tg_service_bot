import os
import razorpay
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
# Simple service list (we will move this to SQLite later)
SERVICES = [
    {"id": 1, "name": "Instagram Followers", "price": 199},
    {"id": 2, "name": "YouTube Views", "price": 149},
    {"id": 3, "name": "Logo Design", "price": 499},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for s in SERVICES:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{s['name']} — ₹{s['price']}",
                callback_data=f"service:{s['id']}"
            )
        ])

    await update.message.reply_text(
        "Choose a service 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def service_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    service_id = int(q.data.split(":")[1])
    service = next((s for s in SERVICES if s["id"] == service_id), None)

    if not service:
        await q.edit_message_text("Service not found 😕")
        return

    keyboard = [
        [InlineKeyboardButton("💳 Pay Now", callback_data=f"pay:{service_id}")]
    ]

    await q.edit_message_text(
        f"🧾 *{service['name']}*\n"
        f"Price: ₹{service['price']}\n\n"
        f"Click below to proceed to payment 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
async def pay_clicked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    service_id = int(q.data.split(":")[1])
    service = next((s for s in SERVICES if s["id"] == service_id), None)

    if not service:
        await q.edit_message_text("Service not found 😕")
        return

    try:
        payment_link = razorpay_client.payment_link.create({
            "amount": service["price"] * 100,
            "currency": "INR",
            "description": service["name"],
        })

        payment_url = payment_link["short_url"]

        await q.edit_message_text(
            f"💳 *{service['name']}*\n"
            f"Price: ₹{service['price']}\n\n"
            f"Pay securely here 👇\n{payment_url}",
            parse_mode="Markdown"
        )

    except Exception as e:
        await q.edit_message_text(f"Error creating payment link:\n{str(e)}")
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(service_clicked, pattern=r"^service:\d+$"))
app.add_handler(CallbackQueryHandler(pay_clicked, pattern=r"^pay:\d+$"))

import os

PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # like https://your-app.onrender.com

print("Starting webhook...")
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path="webhook",
    webhook_url=f"{WEBHOOK_URL}/webhook",
)
