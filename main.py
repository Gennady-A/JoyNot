from bs4 import BeautifulSoup
import requests
import time
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher 
from aiogram.utils import executor 
import os
import datetime

import scraping_joy as sj # Модуль для парсинга.
import log_module as lm # Модуль для логирования работы скрипта.
import CONFIG # Данные для бота


tgToken = CONFIG.bot
adminId = CONFIG.admin

startChecking = False
autosave = False

tags = [] # Список ссылок на отслеживание.
tagsName = {} # Словарь ссылок-имён. Хранит названия разделов по ссылке в качестве ключа.
lastPostLinks = {} # Словарь ссылок-постов. Хранит последний пост раздела по ссылке в качестве ключа.
queueOfPosts = [] # Очередь постов на обработку.


def add_tag(tagLink):
    """
        Назначение: Добавление тэга в список тегов, которые необходимо 
                    отслеживать.

        Функционирование: Выполняется проверка полученной ссылки. 
                          Если ссылка допустима - она добавляется 
                          в список тэгов для отслеживания, после
                          чего тэг добавляется в словарь со ссылкой 
                          последнего поста в тэге. Затем возвращает 
                          соответствующий результату работы текст.
    """
    if sj.valid_link(tagLink):
        if not(tagLink in tags):
            tags.append(tagLink)
            tagsName[tagLink] = sj.getTagName(sj.get_page_bs4(tagLink))
            lastPostLinks[tagLink] = sj.get_lastPostLink_in_tagPage(sj.get_page_bs4(tagLink))
            return 'Тег успешно добавлен.' 
        else:
            return 'Этот тег уже добавлен.'
    else:
        return 'Ссылка не валидна'

def ret_tagList():
    """
        Назначение: Получение списка тэгов.
        
        Функционирование: Формирует из списка тэгов строку и возвращает 
                          её.
    """
    return '\n'.join(['{0}) {1}'.format(i, tags[i]) for i in range(len(tags))])

def ret_lastPostLinks():
    """
        Назначение: Получение списка последних ссылок по каждому тэгу.
        
        Функционирование: Формирует из словаря тэгов строку и возвращает 
                          её.
    """
    return '\n'.join(['{0}) {1} - {2}'.format(i, tagsName[tags[i]], lastPostLinks[tags[i]]) for i in range(len(tags))])

def ret_queueOfPosts():
    """
        Назначение: Получение очереди постов.
        
        Функционирование: Формирует из списка постов строку и возвращает 
                          её.
    """
    return '\n'.join(['{0}) {1}'.format(i, queueOfPosts[i]) for i in range(len(queueOfPosts))])

def del_tag(tagLink):
    """
        Назначение: Удаление тэга из списка на отслеживание.
        
        Функционирование: Если тэг присутствует в списке - удаляем 
                          из списка тэгов, затем из словаря. После 
                          возвращает соответсвующую строку в качестве 
                          ответа.
    """
    if sj.valid_link(tagLink):
        if tagLink in tags:
            tags.remove(tagLink)
            del lastPostLinks[tagLink]
            return 'Тег успешно удалён.' 
        else:
            return 'Этого тега нет в списке.'
    else:
        return 'Ссылка не валидна'




bot = Bot(token = tgToken)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_app(message : types.Message):
    """
        Назначение: Команда старта для пользователя - 
        вызывает сообщение с пояснением по использованию бота. 

        Функционирование: Проверяет пользователя, в зависимости
                          от результата проверки либо присылает 
                          руководство по использованию, либо 
                          отказывает в доступе.
    """
    if os.path.exists('Posts'):
        pass
    else:
        os.mkdir('Posts')

    lm.scr_log('{0} - Вызов команды "start" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "start" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        await message.answer('Привет, этот бот создан для того, чтобы можно было удобно отслеживать последние пости из интересующих разделов сайта joyreactor прямо в тг\
            \n\
            \nКоманды:\
            \n/help - вызов справочной информации по боту.\
            \nadd_tag|"ссылка" - добавить ссылку в список на отслеживание(ссылку указывать без кавычек).\
            \ndel_tag|"ссылка" - удалить ссылку из списка на отслеживание(ссылку указывать без кавычек).\
            \n/get_tagList - вернуть список ссылок на отслеживании.\
            \n/get_lastPostLinks - вернуть список последних постов в каждом разделе на отслеживании.\
            \n/get_queueOfPosts - вернуть список непроверенных пользователем постов.\
            \n/start_checking - запустить отслеживание последних постов в разделах из списка.\
            \n/stop_checking - остановить отслеживание последних постов в разделах из списка\
            \n/my_id - узнать мой id.\
            \n/autosave_on - включить автоматическую загрузку содержимого поста.\
            \n/autosave_off - выключить автоматическую загрузку содержимого поста.\
            \n/savedata - сохранить текущие настройки(список разделов, последние посты и т.д) в отдельный файл\
            \n/loaddata - загрузка последнего сохранённого состояния')
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "start" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

@dp.message_handler(commands=['help'])
async def help(message : types.Message):
    """
        Назначение: Вывода справки.

        Функционирование: Проверяет пользователя, в зависимости
                          от результата проверки либо выводит 
                          справку, либо запрещает доступ.
    """
    lm.scr_log('{0} - Вызов команды "help" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "help" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        await message.answer('Привет, этот бот создан для того, чтобы можно было удобно отслеживать последние посты из интересующих разделов сайта joyreactor прямо в тг\
            \n\
            \nКоманды:\
            \n/help - вызов справочной информации по боту.\
            \nadd_tag|"ссылка" - добавить ссылку в список на отслеживание(ссылку указывать без кавычек).\
            \ndel_tag|"ссылка" - удалить ссылку из списка на отслеживание(ссылку указывать без кавычек).\
            \n/get_tagList - вернуть список ссылок на отслеживании.\
            \n/get_lastPostLinks - вернуть список последних постов в каждом разделе на отслеживании.\
            \n/get_queueOfPosts - вернуть список непроверенных пользователем постов.\
            \n/start_checking - запустить отслеживание последних постов в разделах из списка.\
            \n/stop_checking - остановить отслеживание последних постов в разделах из списка\
            \n/my_id - узнать мой id.\
            \n/autosave_on - включить автоматическую загрузку содержимого поста.\
            \n/autosave_off - выключить автоматическую загрузку содержимого поста.\
            \n/savedata - сохранить текущие настройки(список разделов, последние посты и т.д) в отдельный файл\
            \n/loaddata - загрузка последнего сохранённого состояния')
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "help" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

# Команда запуска проверок. 
@dp.message_handler(commands=['start_checking'])
async def start_сhecking(message : types.Message):
    """
        Назначение: Запуск цикла проверок.

        Функционирование: Проверяет пользователя, в зависимости 
                          от результата проверки либо запрещает 
                          доступ, либо запускает цикл:
                          присваивает переменной startChecking 
                          значение True и запускает цикл на 
                          выполнение. Цикл выполняется пока 
                          переменная равна True. В цикле происходит 
                          по-тэговая проверка последнего поста. В 
                          случае несовпадения пользователь уведомляется 
                          о новом посте в разделе.
    """
    print('start_checking')
    lm.scr_log('{0} - Вызов команды "start_checking" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "start_checking" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        global startChecking
        startChecking = True
        await message.answer('Стартуем')
        while startChecking:
            await asyncio.sleep(10)
            lm.scr_log('{0} - Запуск новой итерации цикла проверки'.format(str(datetime.datetime.now())))

            for tag in tags:
                newLastPost = sj.get_lastPostLink_in_tagPage(sj.get_page_bs4(tag))
                if newLastPost != lastPostLinks[tag]:
                    lastPostLinks[tag] = newLastPost
                    if not(newLastPost in queueOfPosts): 
                        if autosave:
                            sj.download_Post_full(newLastPost, 'Posts')
                        else:
                            queueOfPosts.append(newLastPost)
                            await message.answer('Эй! Для тебя новость! \nВ разделе {0} появился новый пост:\n {1}\nХочешь скачать его(Да\\Нет)?\nПомни, что посты могут накапливаться, а твой ответ будет привязан к самому старому, оставленному без ответа. \nПрвоерить очередь можно командой \\get_queueOfPosts'.format(tag, newLastPost))
                    
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "start_checking" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

# Команда для выключения проверок. 
@dp.message_handler(commands=['stop_checking'])
async def stop_checking(message : types.Message):
    """
        Назначение: Остановка цикла проверок.

        Функционирование: Проверяет пользователя, в зависимости
                          от результата проверки либо запрещает 
                          доступ, либо присваивает переменной
                          startChecking значение False, что 
                          выведет программу из цикла проверок 
                          в функции start_checking при следующей
                          иттерации.
    """
    lm.scr_log('{0} - Вызов команды "stop_checking" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "stop_checking" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        global startChecking 
        startChecking = False
        await message.answer('Окей, дай мне 15 секунд остановится')
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "stop_checking" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

@dp.message_handler(commands=['autosave_on'])
async def autosave_on(message : types.Message):
    """
        Назначение: Включение автоматической выгрузки контента.

        Функционирование: Обращается к глобальной переменной, показывающей, 
                          нужно ли автоматически выгружать контент
                          или необходимо уведомить пользователя. Присваивает
                          ей значение True.
    """
    global autosave 
    autosave = True

@dp.message_handler(commands=['autosave_off'])
async def autosave_off(message : types.Message):
    """
        Назначение: Выключение автоматической выгрузки контента.

        Функционирование: Обращается к глобальной переменной, показывающей, 
                          нужно ли автоматически выгружать контент
                          или необходимо уведомить пользователя. Присваивает
                          ей значение False. 
    """
    global autosave 
    autosave = False

@dp.message_handler(commands=['savedata'])
async def savedata(message : types.Message):
    """
        Назначение: Сохранение настоящего состояния бота.

        Функционирование: Сохраняет основные данные, с которыми работает бот,
                          записывая их в файл формата .txt построчно.
    """
    with open('Logs\data.txt', 'w') as d:
        d.write('|'.join(['{0}'.format(tags[i]) for i in range(len(tags))]) + '\n' \
              + '|'.join(['{0}-{1}'.format(tagsName[tags[i]], lastPostLinks[tags[i]]) for i in range(len(tags))]) + '\n' \
              + '|'.join(['{0}'.format(queueOfPosts[i]) for i in range(len(queueOfPosts))]))

@dp.message_handler(commands=['loaddata'])
async def loaddata(message : types.Message):
    """
        Назначение: Установка последнего сохранённого состояния бота.

        Функционирование: Считывает основные данные, с которыми работает бот,
                          из файла формата .txt построчно.
    """
    with open('Logs\data.txt', 'r') as d:
        tags = d.readline().strip().split('|')
        lastPostLinksL = d.readline().strip().split('|')
        for i in lastPostLinksL:
            lastPostLinks[i.split('-')[0]] = i.split('-')[1]
        queueOfPosts = d.readline().strip().split('|')

# Команда выводит список добавленнных тегов. 
@dp.message_handler(commands=['get_tagList'])
async def get_tagList(message : types.Message):
    """
        Назначение: Получение списка разделов для отслеживания.

        Функционирование: Проверяет пользователя и в зависимости
                          от результата проверки либо запрещает 
                          доступ, либо выводит результат функции 
                          ret_tagList().
    """
    lm.scr_log('{0} - Вызов команды "get_tagList" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "get_tagList" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        ans = ('Список разделов: \n' + ret_tagList()) if len(ret_tagList()) != 0 else 'Список разделов пуст.'
        await message.answer(ans)
        print(ans)
        lm.scr_log('{0} - Команда "get_tagList" отработала с результатом: {1}'.format(str(datetime.datetime.now()), ans))
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "get_tagList" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

# Команды выводит последний пост в каждом теге. 
@dp.message_handler(commands=['get_lastPostLinks'])
async def get_lastPostLinks(message : types.Message):
    """
        Назначение: Получение словаря последних постов по разделам.

        Функционирование: Проверяет пользователя и в зависимости
                          от результата проверки либо запрещает 
                          доступ, либо выводит результат функции 
                          ret_lastPostLinks().
    """
    lm.scr_log('{0} - Вызов команды "get_lastPostLinks" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "get_lastPostLinks" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        ans = ('Список последних постов: \n' + ret_lastPostLinks()) if len(ret_lastPostLinks()) != 0 else 'Список последних постов пуст.'
        await message.answer(ans)
        print(ans)
        lm.scr_log('{0} - Команда "get_lastPostLinks" отработала с результатом: {1}'.format(str(datetime.datetime.now()), ans))
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "get_lastPostLinks" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

# Каманда выводить очередь непроверенных пользователем постов. 
@dp.message_handler(commands=['get_queueOfPosts'])
async def get_queueOfPosts(message : types.Message):
    """
        Назначение: Получение очереди необработанных постов.

        Функционирование: Проверяет пользователя и в зависимости
                          от результата проверки либо запрещает 
                          доступ, либо выводит результат функции 
                          ret_queueOfPosts(). 
    """
    lm.scr_log('{0} - Вызов команды "get_queueOfPosts" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    if str(message.from_user.id) == adminId:
        lm.scr_log('{0} - Проверка пройдена, вызов команды "get_queueOfPosts" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
        ans = ('Очередь постов: \n' + ret_queueOfPosts()) if len(ret_queueOfPosts()) != 0 else 'Очередь пуста.' 
        await message.answer(ans)
        print(ans)
        lm.scr_log('{0} - Команда "get_queueOfPosts" отработала с результатом: {1}'.format(str(datetime.datetime.now()), ans))
    else:
        await message.answer('Ты не армянини.')
        lm.scr_log('{0} - Проверка не пройдена, вызов команды "get_queueOfPosts" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

# Команда для проверки id. 
@dp.message_handler(commands=['my_id'])
async def my_id(message : types.Message):
    """
        Назначение: Получение id.

        Функционирование: Получает id пользователя и отправляет его в ответ.
    """
    lm.scr_log('{0} - Вызов команды "my_id" от пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    ans = 'Твой id: '  + str(message.from_user.id)  + ' - ' + ( 'Ты админ!' if str(message.from_user.id) == adminId else 'Ты не админ :(')
    await message.answer(ans)
    print(ans)
    lm.scr_log('{0} - Команда "my_id" отработала с результатом: {1}'.format(str(datetime.datetime.now()), ans))


# Если пользователь вводит непредусмотренные команды или сообщения.
@dp.message_handler()
async def echo_send(message : types.Message):
    """
        Назначение: Отлавливание сообщений, не являющихся командами.

        Функционирование: Получает сообщение и действует в 
                          зависимости от ситуации. 
    """
    if 'add_tag' in message.text:
        lm.scr_log('{0} - Вызов функции "add_tag" от пользователя: {1} - содержание вызова: {2}'.format(str(datetime.datetime.now()), message.from_user.id, message.text))
        if str(message.from_user.id) == adminId:
            lm.scr_log('{0} - Проверка пройдена, вызов команды "add_tag" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
            try:
                command = (message.text).split('|')
                link = (command[1]).strip()
                print(link)
                ans = add_tag(link) 
            except:
                ans = 'Непредвиденная ошибка'
            await message.answer(ans)
            lm.scr_log('{0} - Вызов функции "add_tag" для пользователя {1} завершился с результатом {2}'.format(str(datetime.datetime.now()), str(message.from_user.id), ans))
        else:
            await message.answer('Ты не армянини.')
            lm.scr_log('{0} - Проверка не пройдена, вызов команды "add_tag" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

    elif 'del_tag' in message.text:
        lm.scr_log('Вызов функции "del_tag" от пользователя: {0} - содержание вызова: {1}'.format(message.from_user.id, message.text))
        if str(message.from_user.id) == adminId:
            lm.scr_log('{0} - Проверка пройдена, вызов команды "del_tag" одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
            try:
                command = (message.text).split('|')
                link = (command[1]).strip()
                print(link)
                ans = del_tag(link)
            except:
                ans = 'Непредвиденная ошибка'
            await message.answer(ans)
            lm.scr_log('{0} - Вызов функции "del_tag" для пользователя {1} завершился с результатом {2}'.format(str(datetime.datetime.now()), str(message.from_user.id), ans))
        else:
            await message.answer('Ты не армянини.')
            lm.scr_log('{0} - Проверка не пройдена, вызов команды "del_tag" запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
    elif message.text == 'Да':
        lm.scr_log('Согласие на выгрузку поста от пользователя: {0} - содержание вызова: {1}'.format(message.from_user.id, message.text))
        if str(message.from_user.id) == adminId:
            lm.scr_log('{0} - Проверка пройдена, согласие на выгрузку поста одобрено для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
            if len(queueOfPosts) == 0:
                await message.answer('Очередь постов пуста')
            else:
                downloadPost = queueOfPosts.pop(0)
                sj.download_Post_full(downloadPost, 'Posts')
                await message.answer('Пост {0} выгружен. В очереди осталось {1} необработанных постов'.format(downloadPost, len(queueOfPosts)))
        else:
            await message.answer('Ты не армянини.')
            lm.scr_log('{0} - Проверка не пройдена, согласие на выгрузку запрещёно для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

    elif message.text == 'Нет':
        lm.scr_log('Отказ от выгрузки поста от пользователя: {0} - содержание вызова: {1}'.format(message.from_user.id, message.text))
        if str(message.from_user.id) == adminId:
            lm.scr_log('{0} - Проверка пройдена, отказ от выгрузки поста одобрен для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))
            if len(queueOfPosts) == 0:
                await message.answer('Очередь постов пуста')
            else:
                downloadPost = queueOfPosts.pop(0)
                await message.answer('Пост {0} отклонён. В очереди осталось {1} необработанных постов'.format(downloadPost, len(queueOfPosts)))
        else:
            await message.answer('Ты не армянини.')
            lm.scr_log('{0} - Проверка не пройдена, отказ от выгрузки запрещён для пользователя: {1}'.format(str(datetime.datetime.now()), str(message.from_user.id)))

    else:
        await message.answer(message.text) 
        lm.msg_log('date: {0}; id: {1}; message: {2} '.format(str(datetime.datetime.now()), str(message.from_user.id), message.text))

# Главная функция - запускает бота.
def main(): 
    lm.scr_log('{0} - Запуск бота'.format(str(datetime.datetime.now())))
    lm.scr_log('')
    lm.scr_log('')
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    main()
