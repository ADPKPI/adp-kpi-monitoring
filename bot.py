from aiohttp import web
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('MON_BOT_TOKEN')
bot = Bot(TOKEN)

async def handle_alert(request):
    """
    Обробляє HTTP POST запити для відправки повідомлень через Telegram бота.

    Аргументи:
    - request: Запит, отриманий від клієнта.

    Повертає:
    - web.Response: Відповідь з кодом статусу.
    """
    data = await request.json()
    chat_id = data.get('chat_id')
    message = data.get('message')
    if not chat_id or not message:
        return web.Response(status=400, text="Bad request: 'chat_id' and 'message' fields are required.")
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return web.Response(status=200, text="Message sent successfully.")
    except Exception as e:
        return web.Response(status=500, text=str(e))

app = web.Application()
app.add_routes([web.post('/alert', handle_alert)])

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=5001)
