import json
from gigachat import GigaChat
from gigachat.models import Chat, MessagesRole, Messages

GIGA_TOKEN = 'secret'


async def recomendate_attractions(city: str) -> dict:
    async with GigaChat(credentials=GIGA_TOKEN, verify_ssl_certs=False) as giga:
        response = await giga.achat(
            'Я планирую посетить ' + city \
            + '. Напиши мне 3 достопримечательности, которые обязательно нужно посетить.' \
            + ' Результат верни в формате JSON-списка без каких-либо пояснений, например,' \
            + ' [{"title": "Спасо-Преображенский монастырь ", "description": ' \
            + '"это древнейший монастырь в Ярославле, основанный в XII веке.' \
            + ' Здесь можно увидеть множество уникальных памятников архитектуры и истории"}].' \
            + ' Не повторяй фразы из примера и не дублируй фразы.')
        data = json.loads(response.choices[0].message.content)
        return data


async def pack_help(is_man: bool, age: int, to_rest: bool, days: int, weather: str) -> dict:
    payload = Chat(messages=[Messages(
        role=MessagesRole.USER,
        content='Я собераюсь в путешествие на ' + str(days) + \
        ' дней. Мне необходимо собрать вещи. Я хочу, чтобы ты мне с этим помог. Я ' + (
            'мужчина' if is_man else 'женщина') + ', мне ' \
        + str(age) + ' лет. Я еду в поездку ' + (
            'для отдыха' if to_rest else 'по работе/учебе') \
        + '. Опишу погоду на данный момент в каждом городе, который я посещу, чтобы тебе было проще подобрать необходимые вещи.\n' + \
        weather + 'Я хочу, чтобы разделил вещи на категории, например, такие как: работа, гигиена, одежда, документы, еда и т.д.' + \
        'Напиши только о самых важных вещах. Обязательно напомни про документы и деньги, они нужны в любой поездке. Результат верни в формате JSON-списка без каких-либо пояснений, например, ' + \
        '[{"type": "Работа/учёба", "things": [{"name": "Ноутбук", "count": 1}, {"name": "Ежедневник", "count": 1}]}]. ' +
        'Не повторяй фразы из примера и не дублируй фразы.'
    )], max_tokens=4096)
    async with GigaChat(credentials=GIGA_TOKEN, verify_ssl_certs=False) as giga:
        response = await giga.achat(payload)
        data = json.loads(response.choices[0].message.content)
        return data
