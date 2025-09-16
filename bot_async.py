import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
from dotenv import load_dotenv
import os
import asyncio
import sys
import nest_asyncio
from requests.adapters import HTTPAdapter, Retry


# Вчитување на променливи од .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
print(f"OpenWeather API Key: {OPENWEATHER_API_KEY}")
# Проверка дали API клучевите се поставени

if not TOKEN:
    raise ValueError("Грешка: Не е поставен TELEGRAM_TOKEN во .env!")
if not OPENWEATHER_API_KEY:
    raise ValueError("Грешка: Не е поставен OPENWEATHER_API_KEY во .env!")

# Конфигурација на логирање
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Глобален requests.Session со timeout и retry
session = requests.Session()
retries = Retry(
    total=3,                # колку пати да проба повторно
    backoff_factor=1,       # време на чекање меѓу обиди (1s, 2s, 4s…)
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("http://", adapter)
session.mount("https://", adapter)

DEFAULT_TIMEOUT = 30  # секунди


# --- Функции за податоци ---

def vadi_inflacija_od_stat():
    url = "https://www.stat.gov.mk/PrikaziSoopstenie.aspx?rbrtxt=39"
    try:
        response = session.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Грешка при преземање на инфлација од ДЗС: {e}")
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

def vadi_placa_finansiski():
    url = "https://www.stat.gov.mk/PrikaziSoopstenie.aspx?rbrtxt=40"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Грешка при преземање на плата од ДЗС: {e}")
        return "Не можам да ја преземам страницата со плати."

    soup = BeautifulSoup(response.text, 'html.parser')
    tekst_div = soup.find(id='ctl00_ContentPlaceHolder1_FormView2_TEKSTSOOPST_MKLabel')
    if not tekst_div:
        return "Не најдов податоци за просечната плата."

    for p in tekst_div.find_all('p'):
        text = p.get_text(strip=True)
        if "денари" in text.lower():
            if "финансиски" in text.lower():
                return text  # Ако има и 'денари' и 'финансиски', ова е приоритетно
            else:
                possible_salary = text  # Ако има само 'денари', зачувај го како можен резултат

    if possible_salary:
        return f"(Без експлицитна референца на финансиски сектор)\n{possible_salary}"

    return "Не најдов валиден податок за просечна плата."

# --- Команди на ботот ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Добиена /start команда од {update.message.from_user.username}")
    msg = (
        "Здраво! Јас сум бот што може да ти каже корисни економски информации.\n\n"
        "📈 /inflacija - Инфлација од Светска банка\n"
        "🧾 /inflacija_kategorii - Инфлација по категории (ДЗС)\n"
        "💶 /kurs - Курс на еврото\n"
        "🌦 /vreme - Временска прогноза за Скопје\n"
        "👛 /plata_finansiski - Последна објавена нето плата во финансискиот сектор"
    )
    await update.message.reply_text(msg)


async def inflacija(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://api.worldbank.org/v2/country/MKD/indicator/FP.CPI.TOTL?format=json&per_page=5"
    try:
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        logger.error(f"World Bank API timeout.")
        await update.message.reply_text("⏳ World Bank API не одговара моментално, пробај подоцна.")
        return
    except ValueError as e:
        logger.error(f"Грешка при парсирање на JSON од Светска банка: {e}")
        await update.message.reply_text("Проблем при обработка на податоците за инфлација.")
        return

    if len(data) > 1 and data[1]:
        results = data[1][:3]  # земи последни 3 записи
        msg = "Инфлација (CPI) за Македонија последни години:\n"
        for entry in results:
            year = entry.get('date', 'Н/Д')
            value = entry.get('value', 'Н/Д')
            msg += f"{year}: {value}\n"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("Не добив валидни податоци за инфлација.")


async def inflacija_kategorii(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = vadi_inflacija_od_stat()
    await update.message.reply_text(text)


async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://open.er-api.com/v6/latest/EUR"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            await update.message.reply_text("API не е достапен или нема податоци.")
            return

        kurs_mkd = data["rates"].get("MKD")
        if kurs_mkd is None:
            await update.message.reply_text("Не можам да најдам курс за MKD.")
            return

        await update.message.reply_text(f"1 EUR = {kurs_mkd:.2f} MKD")
    except requests.RequestException as e:
        logger.error(f"Грешка при преземање на курс: {e}")
        await update.message.reply_text("Грешка при добивање на курсот.")
    except Exception as e:
        logger.error(f"Неочекувана грешка: {e}")
        await update.message.reply_text(f"Грешка: {e}")


async def vreme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        city = "Skopje"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=mk"
        response = requests.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        humidity = data['main']['humidity']

        msg = (
            f"Времето во {city}:\n"
            f"{desc.capitalize()}\n"
            f"Температура: {temp}°C\n"
            f"Влажност: {humidity}%"
        )
        await update.message.reply_text(msg)
    except requests.RequestException as e:
        logger.error(f"Грешка при преземање на временска прогноза: {e}")
        await update.message.reply_text("Грешка при читање на временската прогноза.")
    except KeyError:
        await update.message.reply_text("Не можам да ги обработам податоците за времето.")
    except Exception as e:
        logger.error(f"Неочекувана грешка при време: {e}")
        await update.message.reply_text(f"Грешка: {e}")


async def plata_finansiski(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plata = vadi_placa_finansiski()
    await update.message.reply_text(f"Последната објавена просечна нето плата во финансискиот сектор:\n{plata}")


async def reset_bot(token):
    bot = Bot(token=token)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.get_updates(offset=-1)
    logger.info("Webhook е избришан и getUpdates ресетиран.")


async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inflacija", inflacija))
    app.add_handler(CommandHandler("inflacija_kategorii", inflacija_kategorii))
    app.add_handler(CommandHandler("kurs", kurs))
    app.add_handler(CommandHandler("vreme", vreme))
    app.add_handler(CommandHandler("plata_finansiski", plata_finansiski))

    logger.info("Ботот е стартуван без ресет на webhook...")
    await app.run_polling()



if __name__ == "__main__":
    import asyncio
    import sys
    import nest_asyncio

    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    nest_asyncio.apply()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

