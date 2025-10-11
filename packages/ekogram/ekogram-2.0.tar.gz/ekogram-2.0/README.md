# Ekogram

**Ekogram** — лёгкий Python-модуль для Telegram Bot API и работы с нейросетями.  
Он объединяет простую работу с Telegram и мощные функции: генерация текста и изображений, перевод и озвучка.

## Установка

```bash
pip install ekogram
```

или для macOS:

```bash
pip3 install ekogram
```

## Возможности

- Telegram Bot API: отправка сообщений, медиа, inline, reply клавиатуры и т.п.
- Мощные AI-инструменты: GPT, генерация картинок, перевод, озвучка.
- Поддержка классов Telegram: `Message`, `User`, `Chat`, `Audio`, `Photo`, `Voice` и т.д.
- Работа с `callback_query`, `inline_query`, `handlers`

---

## 🤖 Быстрый старт бота

```python
from ekogram import Bot

bot = Bot("ВАШ_ТОКЕН")

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.reply_message(chat_id=message.chat.id, text="Привет! Я бот Ekogram!")

bot.polling()
```

---

## 🧠 Использование AI

### `FreeGpt` — бесплатный GPT; `Uncensored_Ai` - бесплатный Deepseek

```python
from ekogram import Uncensored_Ai, FreeGpt

gpt = Uncensored_Ai()
gpt2 = FreeGpt()

messages = [
    {"role": "system", "content": "Отвечай кратко и по делу"},
    {"role": "user", "content": "Расскажи, кто такой Эйнштейн?"}
]

print(gpt.reply_ai(messages, True))
print("\n\n"+gpt2.poll_ai(messages))
```

### `FreeImg` — генерация картинок

```python
from ekogram import FreeImg

img = FreeImg()
print(img.flux("cyberpunk robot with fire"))
```

### `Translate` — перевод текста

```python
from ekogram import Deef

tr = Deef()
print(tr.translate("Hello, how are you?", target="ru"))
```

### `ChatGPT` — сессия с GPT

```python
from ekogram import ChatGPT

chat = ChatGPT(url='https://chatgpt.com', headers={})
print(chat.generate_chat_completion(model="gpt-4o-mini", messages=[{"role": 'user', "content": "Hi"}]))
```

---

## 🎤 Озвучка текста

```python
from ekogram import FreeGpt

gpt = FreeGpt()
gpt.speech(text="Привет, как дела?", filename="voice", voice="nova")    #filename -> voice.mp3
```

---

## 📎 Пример кнопок

```python
from ekogram import Bot, Markup

bot = Bot("TOKEN")

@bot.message_handler(commands=["menu"])
def menu(message):
    buttons = [{"text": "Кнопка 1"}, {"text": "Кнопка 2"}]
    markup = Markup.create_reply_keyboard(buttons)
    bot.reply_message(chat_id=message.chat.id, text="Выберите вариант:", reply_markup=markup)
```

---

## 📌 Поддерживаемые классы

- Telegram: `User`, `Chat`, `Message`, `File`, `Photo`, `Voice`, `Video`, `Sticker`, `Document`, `Location`, `Dice` и др.
- InputMedia: `InputMediaPhoto`, `InputMediaVideo`, `InputMediaAudio`, `InputMediaDocument`, `InputMediaAnimation`
- Inline: `InlineQuery`, `InlineQueryResultArticle`, `InlineQueryResultPhoto`, `InlineQueryResultVideo`
- Markup: `Markup.create_inline_keyboard()`, `Markup.create_reply_keyboard()`, `Markup.remove_reply_keyboard()`
- AI: `FreeGpt`, `Uncensored_Ai`, `FreeImg`, `Deef`, `ChatGPT`

---

## 🔒 Лицензия

MIT License

## 📫 Обратная связь

Email: **siriteamrs@gmail.com**

Если возникнут идеи, баги, предложения — пишите 🙌