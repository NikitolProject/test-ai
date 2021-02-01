import asyncio

from botnetvk import botnet

import os
import dialogflow
from translate import Translator
import requests
import string
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import datetime
import wikipedia

bot = botnet

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'small-talk-cmng-d9902e2a00a1.json'

DIALOGFLOW_PROJECT_ID = 'small-talk-cmng'
DIALOGFLOW_LANGUAGE_CODE = 'ru'
SESSION_ID = 'me'

cmd = {
    'determine': ["Я смогла решить Ваш пример.", "Вот ответ на Ваш пример, надеюсь, я Вам помогла.",
                  "Держите ответ на Ваш пример!"],
    'search': ["Вот, что я смогла найти.", "Надеюсь, этот ответ Вам смог помочь.",
               "Это то, что я смогла найти по Вашему вопросу."],
    'time':  ["Сейчас", "Уже", "На часах", "На данный момент"]
}


def chatbot_query(query, index=0):
    fallback = 'Sorry, I cannot think of a reply for that.'
    result = ''
    try:
        search_result_list = list(search(query, tld="co.in", num=10, stop=3, pause=1))
        page = requests.get(search_result_list[index])
        tree = html.fromstring(page.content)
        soup = BeautifulSoup(page.content, features="lxml")
        article_text = ''
        article = soup.findAll('p')
        for element in article:
            article_text += '\n' + ''.join(element.findAll(text=True))
        article_text = article_text.replace('\n', '')
        first_sentence = article_text.split('.')
        first_sentence = first_sentence[0].split('?')[0]
        chars_without_whitespace = first_sentence.translate(
            {ord(c): None for c in string.whitespace}
        )
        if len(chars_without_whitespace) > 0:
            result = first_sentence
        else:
            result = fallback
        return result
    except:
        if len(result) == 0:
            result = fallback
        return result


@bot.decorator_function(text="/p <text>")
async def test(api):
    await api.vkwave.messages.send(
        message=api.pattern['text'],
        peer_id=api.event.object.peer_id,
        random_id=0
    )


@bot.decorator_function(bot_id=0, text="Альт, <speak>")
async def bot_bs(api):
    global cmd
    a = 0
    if api.pattern['speak'].startswith('переведи'):
        a = 1
    text_to_be_analyzed = api.pattern['speak']

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except Exception:
        raise
    if a == 1:
        translator = Translator(from_lang="Russian", to_lang="English")
        lang = translator.translate(response.query_result.parameters.fields['language'].string_value)
        if response.query_result.parameters.fields['language-from'].string_value != '':
            lang_from = translator.translate(response.query_result.parameters.fields['language-from'].string_value)
        else:
            lang_from = "Russian"
        translator = Translator(from_lang=lang_from, to_lang=lang)
        text = translator.translate(response.query_result.parameters.fields['any'].string_value)
        await api.vkwave.messages.send(
            peer_id=api.event.object.peer_id,
            message=f"Перевод: {text}",
            random_id=0
        )
    for x in cmd['determine']:
        if response.query_result.fulfillment_text == x:
            await api.vkwave.messages.send(
                peer_id=api.event.object.peer_id,
                message=f"Ответ: {eval(response.query_result.parameters.fields['any'].string_value)}",
                random_id=0
            )
    for x in cmd['search']:
        if response.query_result.fulfillment_text == x:
            link = response.query_result.parameters.fields['any'].string_value
            wikipedia.set_lang("ru")
            result = str(wikipedia.summary(link, sentences=1))
            await api.vkwave.messages.send(
                peer_id=api.event.object.peer_id,
                message=f"Ответ: {result}",
                random_id=0
            )
            await bot.speak(api=api, text=result)
    for x in cmd['time']:
        if response.query_result.fulfillment_text == x:
            now = datetime.datetime.now()
            response.query_result.fulfillment_text = f"{response.query_result.fulfillment_text} {now.strftime('%H:%M')}"

    await bot.speak(api=api, text=response.query_result.fulfillment_text)


@bot.decorator_function(text='/stop')
async def stopping(api):
    await bot.close()


@bot.decorator_function(bot_id=0, custom_event=[3, 4, 5])
async def bot_ls(api):
    print("ok")
    try:
        user = await api.vkbottle.users.get(user_id=api.event.object.peer_id)
        user_id = user[0].id
    except Exception:
        user_id = 0
        user = []
    if user_id == api.event.object.peer_id and user[0].last_name != "":
        global cmd
        a = 0
        text: str = api.event.object.text
        text: str = text.lower()
        if text.startswith('переведи'):
            a = 1
        text_to_be_analyzed = api.event.object.text

        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        try:
            response = session_client.detect_intent(session=session, query_input=query_input)
        except Exception:
            raise
        if a == 1:
            translator = Translator(from_lang="Russian", to_lang="English")
            lang = translator.translate(response.query_result.parameters.fields['language'].string_value)
            if response.query_result.parameters.fields['language-from'].string_value != '':
                lang_from = translator.translate(response.query_result.parameters.fields['language-from'].string_value)
            else:
                lang_from = "Russian"
            translator = Translator(from_lang=lang_from, to_lang=lang)
            text = translator.translate(response.query_result.parameters.fields['any'].string_value)
            await api.vkwave.messages.send(
                peer_id=api.event.object.peer_id,
                message=f"Перевод: {text}",
                random_id=0
            )
        for x in cmd['determine']:
            if response.query_result.fulfillment_text == x:
                await api.vkwave.messages.send(
                    peer_id=api.event.object.peer_id,
                    message=f"Ответ: {eval(response.query_result.parameters.fields['any'].string_value)}",
                    random_id=0
                )
        for x in cmd['search']:
            if response.query_result.fulfillment_text == x:
                link = response.query_result.parameters.fields['any'].string_value
                api.log.info(link)
                result = chatbot_query(link)
                await api.vkwave.messages.send(
                    peer_id=api.event.object.peer_id,
                    message=f"Ответ: {result}",
                    random_id=0
                )
                await bot.speak(api=api, text=result)
        for x in cmd['time']:
            if response.query_result.fulfillment_text == x:
                now = datetime.datetime.now()
                response.query_result.fulfillment_text = f"{response.query_result.fulfillment_text} {now.strftime('%H:%M')}"

        await bot.speak(api=api, text=response.query_result.fulfillment_text)


bot.run_forever()