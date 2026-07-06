"""
============================================================
БОТ "КЛУБ ТРЕЙПА" — обработка трафика с сайта
============================================================

Что нужно сделать перед запуском (шаг за шагом):

1) Установите библиотеку (один раз, в терминале):
   pip install aiogram

2) Впишите ниже, в блоке "НАСТРОЙКИ", свой токен бота из @BotFather.

3) Для тарифа "Магазин под ключ" бот после оплаты создаёт ОДНОРАЗОВУЮ
   ссылку-приглашение в закрытый канал. Чтобы это работало, нужно:
     а) добавить этого бота АДМИНИСТРАТОРОМ в закрытый канал
        (https://t.me/+C8r0SYMar-plMTdk) с правом "Приглашать пользователей";
     б) узнать числовой ID этого канала и вписать его в CHANNEL_SHOP_ID ниже.
        Как узнать ID канала:
        - перешлите любое сообщение из канала боту @userinfobot,
          либо
        - добавьте бота @getidsbot в канал администратором на минуту —
          он покажет ID вида -1001234567890.
   Если не настроите это — бот просто отправит запасную (постоянную)
   ссылку на канал, которая уже указана ниже. Всё равно будет работать,
   просто ссылка не будет одноразовой.

4) Запустите файл:
   python bot.py

============================================================
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import (
    Message,
    CallbackQuery,
    PreCheckoutQuery,
    LabeledPrice,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    MenuButtonWebApp,
)

# ============================================================
# НАСТРОЙКИ — впишите свои данные сюда
# ============================================================

# Токен бота из @BotFather (обязательно замените на свой!)
BOT_TOKEN = "8569629917:AAHVYpGlaH-MI4-nECmKlHfFnWda9_qpQjo"

# Ссылка на закрытый VIP-чат/канал с сигналами (для тарифа "Трейдинг")
TRADING_CHANNEL_LINK = "https://t.me/+nDIiCjRs5IRmZGE0"

# Ссылка на личный аккаунт автора (оплата USDT / картой напрямую)
OWNER_CONTACT_LINK = "https://t.me/trape8"

# Запасная (постоянная) ссылка на закрытый канал с курсом "Магазин под ключ".
# Используется, если не настроен CHANNEL_SHOP_ID (см. пункт 3 в шапке файла).
SHOP_CHANNEL_FALLBACK_LINK = "https://t.me/+C8r0SYMar-plMTdk"

# Числовой ID закрытого канала с курсом "Магазин под ключ".
# Нужен, чтобы бот генерировал ОДНОРАЗОВУЮ ссылку каждому покупателю.
# Пример правильного формата: -1001234567890
# Если не знаете ID — оставьте None, бот будет слать запасную ссылку выше.
CHANNEL_SHOP_ID = -1002665594068  # например: -1001234567890

# Цена курса "Магазин под ключ" в Telegram Stars
SHOP_PRICE_STARS = 1499

# Ссылка на ваш сайт (обязательно HTTPS!), например GitHub Pages:
# https://ваш_логин.github.io/название_репозитория/
WEBSITE_URL = "https://trape-site-tr5o.vercel.app"

# ============================================================
# Дальше ничего менять не нужно
# ============================================================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


# ------------------------------------------------------------
# Обработка команды /start (в том числе с параметром из ссылки сайта)
# Ссылка с сайта выглядит так: https://t.me/ИМЯ_БОТА?start=trading
# После перехода Telegram сам вызывает /start trading — этот параметр
# мы и ловим ниже через command.args
# ------------------------------------------------------------
@dp.message(CommandStart())
async def handle_start(message: Message, command: CommandObject):
    payload = command.args  # это то, что стоит после "?start=" в ссылке

    if payload == "trading":
        await send_trading_offer(message)
    elif payload == "shop":
        await send_shop_offer(message)
    else:
        # Если человек просто написал боту /start без параметра —
        # показываем кнопку, которая открывает сайт прямо внутри Telegram
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🌐 Открыть сайт",
                        web_app=WebAppInfo(url=WEBSITE_URL),
                    )
                ]
            ]
        )
        await message.answer(
            "Привет! 👋 Это бот <b>Клуба Трейпа</b>.\n\n"
            "Открой сайт, чтобы выбрать подходящий тариф — "
            "бесплатное обучение трейдингу или курс по запуску "
            "онлайн-магазина.",
            reply_markup=keyboard,
        )


# ------------------------------------------------------------
# Блок 1: Тариф "Бесплатный старт в трейдинге"
# ------------------------------------------------------------
async def send_trading_offer(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📈 Перейти в VIP-чат с сигналами",
                    url=TRADING_CHANNEL_LINK,
                )
            ]
        ]
    )

    await message.answer(
        "Привет! Ты выбрал бесплатное обучение трейдингу.\n\n"
        "Вот твоя ссылка на пошаговый курс и наш закрытый VIP-чат с сигналами!",
        reply_markup=keyboard,
    )


# ------------------------------------------------------------
# Блок 2: Тариф "Онлайн-магазин под ключ"
# ------------------------------------------------------------
async def send_shop_offer(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Оплатить через Telegram Stars",
                    callback_data="pay_stars_shop",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Оплатить в USDT / картой (связаться с автором)",
                    url=OWNER_CONTACT_LINK,
                )
            ],
        ]
    )

    await message.answer(
        "Отличный выбор! Курс «Онлайн-магазин под ключ» поможет тебе "
        "запустить бизнес за 1 вечер.\n\n"
        f"Стоимость: 35$ ({SHOP_PRICE_STARS} Telegram Stars).\n\n"
        "Выбери удобный способ оплаты ниже 👇",
        reply_markup=keyboard,
    )


# ------------------------------------------------------------
# Нажатие на кнопку "Оплатить через Telegram Stars"
# Выставляем счёт (инвойс) в валюте XTR — это и есть Telegram Stars
# ------------------------------------------------------------
@dp.callback_query(F.data == "pay_stars_shop")
async def process_pay_stars(callback: CallbackQuery):
    await callback.answer()  # убираем "часики" на кнопке

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Онлайн-магазин под ключ",
        description="Пошаговая система запуска своего интернет-магазина за 1 вечер.",
        payload="shop_course_payment",  # внутренний идентификатор заказа
        currency="XTR",  # XTR — это Telegram Stars
        prices=[LabeledPrice(label="Курс «Магазин под ключ»", amount=SHOP_PRICE_STARS)],
        provider_token="",  # для оплаты Stars provider_token оставляем пустым
    )


# ------------------------------------------------------------
# Обязательное подтверждение перед оплатой (без этого платёж не пройдёт)
# ------------------------------------------------------------
@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# ------------------------------------------------------------
# Успешная оплата — выдаём доступ к закрытому каналу с курсом
# ------------------------------------------------------------
@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    invite_link = SHOP_CHANNEL_FALLBACK_LINK

    # Если указан числовой ID канала — пробуем создать ОДНОРАЗОВУЮ ссылку
    if CHANNEL_SHOP_ID is not None:
        try:
            invite = await bot.create_chat_invite_link(
                chat_id=CHANNEL_SHOP_ID,
                member_limit=1,  # ссылка сработает только один раз
            )
            invite_link = invite.invite_link
        except Exception as error:
            logging.warning(
                "Не удалось создать одноразовую ссылку, отправляю запасную. "
                "Проверьте, что бот добавлен админом в канал. Ошибка: %s",
                error,
            )

    await message.answer(
        "✅ Оплата прошла успешно! Спасибо за покупку.\n\n"
        "Вот твоя ссылка для входа в закрытый канал с курсом:\n"
        f"{invite_link}\n\n"
        "Если ссылка не открывается — напиши автору: "
        f"{OWNER_CONTACT_LINK}"
    )


# ------------------------------------------------------------
# Запуск бота
# ------------------------------------------------------------
async def main():
    # Устанавливаем постоянную кнопку "Меню" рядом с полем ввода —
    # при нажатии она сразу открывает сайт как Web App
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Открыть сайт",
            web_app=WebAppInfo(url=WEBSITE_URL),
        )
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

