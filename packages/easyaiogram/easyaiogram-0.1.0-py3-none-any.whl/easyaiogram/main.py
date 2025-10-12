from aiogram import Bot, Dispatcher, F, types
import asyncio

class InlineKey:
    """Helper class for creating inline keyboards easily."""
    def __init__(self, name: str):
        self.name = name
        self.markup = types.InlineKeyboardMarkup(inline_keyboard=[])

    def append(self, text: str, call_data: str):
        button = types.InlineKeyboardButton(text=text, callback_data=call_data)
        self.markup.inline_keyboard.append([button])
        return self
    def get(self):
        return self.markup


class EasyAiogram:
    def __init__(self, token):
        self.token = token
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

    def makecommand(self, command, letter, keyboard: InlineKey | None = None):
        @self.dp.message(F.text == command)
        async def root(msg: types.Message):
            await msg.answer(letter, reply_markup=keyboard.get() if keyboard else None)

    def createinkey(self, name: str):
        return InlineKey(name)

    def oncallback(self, call_data: str, answer_text: str):
        @self.dp.callback_query(F.data == call_data)
        async def handle_callback(callback: types.CallbackQuery):
            await callback.message.answer(answer_text)
            await callback.answer()

    async def _start(self):
        await self.dp.start_polling(self.bot)

    def startbot(self):
        asyncio.run(self._start())
