# 📊 Telegram Informative Bot for North Macedonia

This bot provides useful information about North Macedonia directly on Telegram, including:

🧾 Inflation data from the World Bank

🧺 Inflation by categories from the State Statistical Office (SSO)

💰 Average net salary

💶 EUR to MKD exchange rate

🌤️ Weather forecast for Skopje

---

## 🚀 How to Use

🟢 The bot is available on Telegram: 

👉 [t.me/inflacija_bot](https://t.me/inflacija_bot)

🗒️ Supported Commands:
| Команда              | Опис |
|----------------------|------
| /start               | Welcome message and instructions
| /inflacija           | Inflation by years from the World Bank 
| /inflacija_kategorii | Inflation by categories from SSO 
| /plata               | Latest published average net salary
| /kurs                | EUR to MKD exchange rate 
| /vreme               | Wather in Skopje 

---

## 🛠️ Technologies Used

 - [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot)
 - requests, BeautifulSoup (`bs4`)
 - [OpenWeatherMap API](https://openweathermap.org/api)
 - [ER-API](https://www.exchangerate-api.com/) (exchange rates)
 - [World Bank API](https://data.worldbank.org/)
 - Web scraping (SSO and salary data from official sites)


---

## 🔧 Local Installation

1. Clone the repository:

git clone https://github.com/your-username/telegram-informative-bot.git

cd telegram-informative-bot


2.Install dependencies: 

pip install -r requirements.txt


3.Set your Telegram Bot Token:

Create a file called .env in the project folder and add:

TELEGRAM_TOKEN=your_telegram_bot_token


4.Run the bot:

python main.py

----

## 📸 Example Bot Output

Start Message

![/start](https://github.com/EmilijaRam/telegram-informativen-bot/blob/main/start.png)

Annual Inflation in North Macedonia

![/inflacija](https://github.com/EmilijaRam/telegram-informativen-bot/blob/main/inflation.png)

Monthly inflation by categories

![/inflacija_kategorii](https://github.com/EmilijaRam/telegram-informativen-bot/blob/main/inflation%20categories.png)

Average net salary

![/plata](https://github.com/EmilijaRam/telegram-informativen-bot/blob/main/salary.png)

Daily weather forecast for Skopje

![/vreme](https://github.com/EmilijaRam/telegram-informativen-bot/blob/main/weather%20forecast.png)

----
## 📬 Contact
Created by Emilija Ramova
