import logging
import yt_dlp
import os

from create_bot import bot, dp, BASE_URL, ADMIN_ID, WEBHOOK_PATH, HOST, PORT, DIR_DOWNLOAD
from aiogram.types import BotCommand, BotCommandScopeDefault, FSInputFile, Message
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


async def set_commands():
    # Список комманд доступных юзерам
    commands = [BotCommand(command='start', description='Старт')]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup() -> None:
    await set_commands()
    await bot.set_webhook(f"{BASE_URL}{WEBHOOK_PATH}")
    await bot.send_message(chat_id=int(ADMIN_ID), text='Бот запущен!')


async def on_shutdown() -> None:
    await bot.send_message(chat_id=ADMIN_ID, text="Бот остановлен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.reply(f'Привет, <b>{message.from_user.full_name}</b>! Отправь мне <b><i>ссылку на ютуб-видео</i></b>, и я загружу его!')


@dp.message(lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
async def echo_handler(message: Message) -> None:
    link = message.text
    await message.answer("Загружаю видео, это может занять некоторое время...")

    video_file = await download_youtube_video(link)

    print(video_file)
    # input("press")
    if video_file:
        video = FSInputFile(video_file)
        await bot.send_video(chat_id=message.chat.id, video=video)
        if os.path.exists(video_file):
            os.remove(video_file)
    else:
        await message.answer("Не удалось загрузить видео. Попробуйте другую ссылку.")


async def download_youtube_video(link: str) -> str:
    fixed_video_name = "some_video"  # Задаем фиксированное имя
    file_path = os.path.join(DIR_DOWNLOAD, f"{fixed_video_name}.mp4")  # Формируем полный путь к файлу

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_path,  # Используем правильный путь
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'socket_timeout': 30,
        'noplaylist': True,
        'verbose': True,
        'proxy': 'PROXY'
    }

    # Создаём директорию, если её нет
    if not os.path.exists("O:/downloads"):
        os.makedirs('O:/downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            return ydl.prepare_filename(info)  # Возвращаем имя загруженного файла
    except Exception as e:
        print(f"Ошибка при загрузке видео: {e}")
        return str(None)


def main() -> None:
    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)

    app = web.Application()

    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )

    webhook_request_handler.register(app, path=WEBHOOK_PATH)
    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=HOST, port=PORT)


if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main()
