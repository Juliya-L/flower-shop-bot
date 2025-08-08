import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")


flowers = [
    ("Rose", 70),
    ("Tulip", 40),
    ("Chrysanthemum", 50),
    ("Hydrangea", 250),
    ("Peony", 60)
]


colors = ["Red", "White", "Yellow", "Pink", "Blue"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌸 Place an Order", callback_data="make_order")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to our flower shop bot! 💐\nClick the button below to start your order:",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    
    if query.data == "make_order":
        keyboard = [
            [InlineKeyboardButton(f"{name} — {price} UAH", callback_data=f"flower_{i}")]
            for i, (name, price) in enumerate(flowers)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a flower type:", reply_markup=reply_markup)

    
    elif query.data.startswith("flower_"):
        idx = int(query.data.split("_")[1])
        flower_name, flower_price = flowers[idx]
        context.user_data["flower"] = flower_name
        context.user_data["price"] = flower_price

        keyboard = [
            [InlineKeyboardButton(color, callback_data=f"color_{color}")]
            for color in colors
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"You selected: {flower_name} — {flower_price} UAH.\nChoose a color:",
            reply_markup=reply_markup
        )

    
    elif query.data.startswith("color_"):
        color_chosen = query.data.replace("color_", "")
        context.user_data["color"] = color_chosen

        keyboard = [
            [InlineKeyboardButton(str(i), callback_data=f"qty_{i}")]
            for i in range(1, 11)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"You selected: {context.user_data['flower']} ({context.user_data['color']})\n"
            "Choose quantity:",
            reply_markup=reply_markup
        )

    
    elif query.data.startswith("qty_"):
        qty = int(query.data.replace("qty_", ""))
        context.user_data["qty"] = qty
        total_price = context.user_data["price"] * qty
        context.user_data["total_price"] = total_price

        keyboard = [
            [InlineKeyboardButton("💳 Bank Transfer", callback_data="pay_bank")],
            [InlineKeyboardButton("💵 Cash on Delivery", callback_data="pay_cash")],
            [InlineKeyboardButton("🏪 Pickup", callback_data="pay_pickup")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Your order:\n"
            f"- {context.user_data['flower']} ({context.user_data['color']})\n"
            f"- Quantity: {qty}\n"
            f"Total: {total_price} UAH\n\n"
            "Select payment method:",
            reply_markup=reply_markup
        )

    
    elif query.data == "pay_bank":
        context.user_data["payment"] = "Bank Transfer"
        await query.edit_message_text(
            "💳 Payment details:\n"
            "IBAN: UA00 0000 0000 0000 0000 0000 0000\n"
            "Recipient: Flower Shop\n\n"
            "After payment, please send a photo or screenshot of the receipt."
        )

    
    elif query.data == "pay_cash":
        context.user_data["payment"] = "Cash on Delivery"
        await query.edit_message_text(
            "Thank you for your order! 💐\n"
            "Our seller will contact you shortly to confirm details."
        )

    
    elif query.data == "pay_pickup":
        context.user_data["payment"] = "Pickup"
        await query.edit_message_text(
            "Thank you for your order! 💐\n"
            "Our seller will contact you shortly to confirm details."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("payment") == "Bank Transfer":
        await update.message.reply_text(
            "Thank you for confirming the payment! 💐\n"
            "Our seller will contact you shortly to confirm details."
        )


def main():
    if not TOKEN:
        raise ValueError("TOKEN is not set. Please add it to your .env file.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
