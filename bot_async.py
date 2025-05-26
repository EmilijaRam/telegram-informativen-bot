import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from telegram import Bot
import logging


TOKEN = '7734520522:AAFPWEruBi5UI_sjrxvxRR5vO8ZdFc6M-Yk'
OPENWEATHER_API_KEY = "3765925764c3f36e135ae51a54a2e13e"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
def vadi_inflacija_od_stat():
    url = "https://www.stat.gov.mk/PrikaziSoopstenie.aspx?rbrtxt=39"
    response = requests.get(url)
    if response.status_code != 200:
        return "Не можам да ја преземам страницата."

    soup = BeautifulSoup(response.text, 'html.parser')
    tekst_div = soup.find(id='ctl00_ContentPlaceHolder1_FormView2_TEKSTSOOPST_MKLabel')
    if not tekst_div:
        return "Не најдов податоци за инфлацијата."

    paragraphs = tekst_div.find_all('p')
    if not paragraphs:
        return "Податоците се празни."

    poraka = ""
    for p in paragraphs:
        text = p.get_text(strip=True)
        poraka += text + "\n\n"

    return poraka.strip()

def vadi_placa():
    url = "https://www.stat.gov.mk/PrikaziSoopstenie.aspx?rbrtxt=40"
    response = requests.get(url)
    if response.status_code != 200:
        return "Не можам да ја преземам страницата со плати."
    soup = BeautifulSoup(response.text, 'html.parser')

    # Пребаруваме по елемент каде што е текстот со платата (пример: некој div или span)
    tekst_div = soup.find(id='ctl00_ContentPlaceHolder1_FormView2_TEKSTSOOPST_MKLabel')
    if not tekst_div:
        return "Не најдов податоци за просечната плата."
    
    paragraphs = tekst_div.find_all('p')
    if not paragraphs:
        return "Податоците за плата се празни."
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if "денари" in text.lower() and ("плата" in text.lower() or "нето" in text.lower()):
            return text  # Враќаме ја првата релевантна реченица
    
    return "Не најдов валиден податок за просечна плата."

async def placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plata = vadi_placa()
    await update.message.reply_text(f"Последната објавена просечна нето плата:\n{plata}")



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Здраво! Јас сум бот што може да ти каже корисни економски информации.\n\n"
        "📈 /inflacija - Инфлација од Светска банка\n"
        "🧾 /inflacija_kategorii - Инфлација по категории (ДЗС)\n"
        "💶 /kurs - Курс на еврото\n"
        "🌦 /vreme - Временска прогноза за Скопје\n"
        "👛 /plata - Последна објавена нето плата"
        )


async def inflacija(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.worldbank.org/v2/country/MKD/indicator/FP.CPI.TOTL?format=json&per_page=5"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and len(data) > 1:
        results = data[1][:3]
        msg = "Инфлација (CPI) за Македонија последни години:\n"
        for entry in results:
            year = entry['date']
            value = entry['value']
            msg += f"{year}: {value}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Не можев да ја преземам инфлацијата. Обиди се повторно.")


async def inflacija_kategorii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = vadi_inflacija_od_stat()
    await update.message.reply_text(text)

async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://open.er-api.com/v6/latest/EUR"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or data.get("result") != "success":
            await update.message.reply_text("API не е достапен или нема податоци.")
            return

        kurs_mkd = data["rates"]["MKD"]
        await update.message.reply_text(f"1 EUR = {kurs_mkd:.2f} MKD")
    except Exception as e:
        await update.message.reply_text(f"Грешка: {e}")

async def reset_bot(token):
    bot = Bot(token=token)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.get_updates(offset=-1)
    print("Webhook е избришан и getUpdates ресетиран.")

async def vreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        city = "Skopje"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=mk"
        response = requests.get(url)
        data = response.json()

        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        humidity = data['main']['humidity']

        msg = f"Времето во {city}:\n{desc.capitalize()}\nТемпература: {temp}°C\nВлажност: {humidity}%"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text("Грешка при читање на временската прогноза.")

async def main():
    await reset_bot(TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inflacija", inflacija))
    app.add_handler(CommandHandler("inflacija_kategorii", inflacija_kategorii))
    app.add_handler(CommandHandler("kurs", kurs))
    app.add_handler(CommandHandler("vreme", vreme))
    app.add_handler(CommandHandler("plata", placa))



    print("Ботот е стартуван...")
    await app.run_polling()
import asyncio
import sys

if __name__ == "__main__":
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nest_asyncio
nest_asyncio.apply()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
       