import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import flowers, colors
from utils import save_order

ADMIN_ID = os.getenv('ADMIN_ID')  # leave placeholder in .env.example

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌸 Place an Order", callback_data="make_order")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to our flower shop bot! 💐\nClick the button below to start your order:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "make_order":
        keyboard = [[InlineKeyboardButton(f"{name} — {price} UAH", callback_data=f"flower_{i}")] for i,(name,price) in enumerate(flowers)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select a flower type:", reply_markup=reply_markup)
        return

    if data.startswith("flower_"):
        idx = int(data.split("_")[1])
        name, price = flowers[idx]
        context.user_data['flower'] = name
        context.user_data['price'] = price
        keyboard = [[InlineKeyboardButton(color, callback_data=f"color_{color}")] for color in colors]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"You selected: {name} — {price} UAH.\nChoose a color:", reply_markup=reply_markup)
        return

    if data.startswith("color_"):
        color = data.replace("color_", "")
        context.user_data['color'] = color
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"qty_{i}")] for i in range(1,11)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"You selected: {context.user_data['flower']} ({color})\nChoose quantity:", reply_markup=reply_markup)
        return

    if data.startswith("qty_"):
        qty = int(data.replace("qty_",""))
        context.user_data['qty'] = qty
        total = context.user_data['price'] * qty
        context.user_data['total_price'] = total
        keyboard = [
            [InlineKeyboardButton("💳 Bank Transfer", callback_data="pay_bank")],
            [InlineKeyboardButton("💵 Cash on Delivery", callback_data="pay_cash")],
            [InlineKeyboardButton("🏪 Pickup", callback_data="pay_pickup")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Your order:\n- {context.user_data['flower']} ({context.user_data['color']})\n- Quantity: {qty}\nTotal: {total} UAH\n\nSelect payment method:",
            reply_markup=reply_markup
        )
        return

    if data == "pay_bank" or data == "pay_cash" or data == "pay_pickup":
        payment = "Bank Transfer" if data=="pay_bank" else ("Cash on Delivery" if data=="pay_cash" else "Pickup")
        context.user_data['payment'] = payment
        if payment == "Bank Transfer":
            await query.edit_message_text("💳 Payment details:\nIBAN: UA00 0000 0000 0000 0000 0000 0000\nRecipient: Flower Shop\n\nAfter payment, please send a photo or screenshot of the receipt.")
            return
        else:
            # Save order and notify admin
            order = {
                'user_id': update.effective_user.id,
                'username': update.effective_user.username,
                'flower': context.user_data.get('flower'),
                'color': context.user_data.get('color'),
                'qty': context.user_data.get('qty'),
                'total': context.user_data.get('total_price'),
                'payment': payment
            }
            save_order(order)
            await query.edit_message_text("Thank you for your order! 💐\nOur seller will contact you shortly to confirm details.")
            # notify admin if ADMIN_ID set
            if ADMIN_ID:
                try:
                    await context.bot.send_message(int(ADMIN_ID), f"New order:\nUser: @{order.get('username')} (id={order.get('user_id')})\n{order.get('flower')} ({order.get('color')}) x{order.get('qty')} — {order.get('total')} UAH\nPayment: {order.get('payment')}")
                except Exception:
                    pass
            return

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only accept photos for bank transfer confirmation
    if context.user_data.get('payment') == 'Bank Transfer':
        # Save order and notify admin
        order = {
            'user_id': update.effective_user.id,
            'username': update.effective_user.username,
            'flower': context.user_data.get('flower'),
            'color': context.user_data.get('color'),
            'qty': context.user_data.get('qty'),
            'total': context.user_data.get('total_price'),
            'payment': 'Bank Transfer',
            'receipt': True
        }
        save_order(order)
        await update.message.reply_text("Thank you for confirming the payment! 💐\nOur seller will contact you shortly to confirm details.")
        if ADMIN_ID:
            try:
                await context.bot.send_message(int(ADMIN_ID), f"New paid order (bank transfer):\nUser: @{order.get('username')} (id={order.get('user_id')})\n{order.get('flower')} ({order.get('color')}) x{order.get('qty')} — {order.get('total')} UAH")
            except Exception:
                pass

def register_handlers(app):
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
