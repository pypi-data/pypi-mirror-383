# -*- coding: utf-8 -*-
import logging
import os
import requests



def message(text: str) -> bool:
    """
    Sends a message to a Telegram chat using the bot token and chat ID from environment variables.
    Expects the following environment variables to be set:
    - TELEGRAM_BOT_TOKEN: The token of the Telegram bot.
    - TELEGRAM_CHAT_ID: The chat ID where the message will be sent.
    
    Args:
      text (str): The message to send.

    Returns:
      bool: True if the message was sent successfully, False otherwise.
    """
    logging.info(text)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200 and response.json().get("ok", False)
    except Exception:
        return False
