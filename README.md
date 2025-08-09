# Flower Shop Telegram Bot

Simple Telegram bot for ordering flowers with escolha of type, color, quantity and payment method.

## Features
- Select flower type, color and quantity
- Calculate total price
- Payment via bank transfer or cash on delivery
- Upload photo of payment receipt for bank transfers
- Orders are saved to `orders.json`
- Optional admin notifications (set ADMIN_ID in .env)

## Quick start
1. Copy `.env.example` to `.env` and set your `TOKEN` (and `ADMIN_ID` if you want admin notifications)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python bot.py
   ```

## Notes
- Do **not** commit your real `.env` file to GitHub.
- `orders.json` is in `.gitignore` by default to avoid leaking real orders.
