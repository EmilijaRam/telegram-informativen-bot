import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Твојот API токен што го доби од BotFather
TOKEN = 'ТУКА_СТАВИ_GOТВОЈОТ_ТОКЕН'

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Здраво! Јас сум бот што може да ти каже инфлација. Напиши /inflacija за да ја добиеш инфлацијата за Македонија."
    )

def inflacija(update: Update, context: CallbackContext):
    # World Bank API за инфлација (Consumer Price Index) за Македонија (MKD)
    url = "https://api.worldbank.org/v2/country/MKD/indicator/FP.CPI.TOTL?format=json&per_page=5"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and len(data) > 1:
        # Ги земаме последните 3 години
        results = data[1][:3]
        msg = "Инфлација (CPI) за Македонија последни години:\n"
        for entry in results:
            year = entry['date']
            value = entry['value']
            msg += f"{year}: {value}\n"
        update.message.reply_text(msg)
    else:
        update.message.reply_text("Не можев да ја преземам инфлацијата. Обиди се повторно.")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("inflacija", inflacija))

    print("Ботот е стартуван...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
