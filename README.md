Telegram bot that monitors a Kaggle competition and sends notifications when a new best scoring public kernel is published.
You'll need to provide a config.json file with the following values:
- COMPETITION: The name of the competition to monitor
- TELEGRAM_BOT_TOKEN: The bot token from Telegram
- TELEGRAM_CHAT_ID: The chat ID from Telegram

To run the bot, use the following command:
```
python main.py
```

The bot will run indefinitely, checking for new best scoring public kernels every hour. Don't forget to publish on your server for continuous notifications!!!

Note: You'll need to have the kaggle SDK installed and authenticated to use this bot.
