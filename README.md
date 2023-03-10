# JoyNot
JoyReactor notifications in telegram 

Уведомления JoyReactor в телеграме


# История: 
В какой-то период я вёл несколко групп в вк и наполнял их по большей части контентом с JoyReactor'а. 
Для этого нужно было постоянно проверять портал по конкретным тэгам(разделам), скачивать контент и выгружать в группу.
Делать это с телефона не удобно, с компьютера не всегда получается, поэтому я подумал, что можно было бы написать небольшого
бота, который будет автоматически проверять контент выбранных разделов, с возможностью добавлять новые разделы на проверку, 
удалять старые и т.д. Так же, чтобы не заниматься добавление постов в группу самостоятельно, можно возложить и эту задачу на бота,
сделать так, чтобы получив уведомление о новом посте на Joyreactor, можно было бы просто одобрить отправку его содержимого в группу. 

Начать я решил с небольшой системы, главной задачей которой будет мониторинг нужных разделов Joyreactor'а и уведомление о новых постах. 
Вся работа осуществляется через telegram-бота.


# Функционал:
1) (+) Добавление и удаление ссылок на разделы, которые необходимо мониторить.
2) (+) Уведомление пользователя при появлении новых постов в выбранных разделах.
3) (+) Возможность выгрузки контента(Кроме видео) из поста по согласию пользователя.
4) (+) Добавление постов в очередь до момента, пока пользователь не ответит, выгружать контент или нет
5) (+) Возможность перевода бота в режим автоматической выгрузки контента всех новых постов.
6) (+) Возможность сохранения последнего состояния(Списка разделов, списка последних постов, очереди и т.д).


# Порядок настройки:
1) Зарегистрируйте бота в телеграме через официального бота BotFather.
2) Откройте файл CONFIG.py и запишите в переменную bot значение токена вашего бота, а в переменную admin ваш id.
3) Запустите файл main.py
4) Напишите вашему боту команду /start

!!!Помните, что бот будет работать до тех пор, пока работает устройство, на котором он размещён.


# Работа с ботом:
После выполнения всех пунктов предыдущего блока бот должен отправить вам список команд, который не нуждается в дополнительном
пояснении, но тем не менее, стоит привести его и здесь:   
/help - вызов справочной информации по боту.            
add_tag|"ссылка" - добавить ссылку в список на отслеживание(ссылку указывать без кавычек).            
del_tag|"ссылка" - удалить ссылку из списка на отслеживание(ссылку указывать без кавычек).            
/get_tagList - вернуть список ссылок на отслеживании.            
/get_lastPostLinks - вернуть список последних постов в каждом разделе на отслеживании.            
/get_queueOfPosts - вернуть список непроверенных пользователем постов.            
/start_checking - запустить отслеживание последних постов в разделах из списка.            
/stop_checking - остановить отслеживание последних постов в разделах из списка            
/my_id - узнать свой id.

Часть этих команд либо нужна только для отладки, либо слишком проста для пояснений, поэтому подробнее рассмотрим не все:
1) add_tag|"ссылка" - у бота имеется список разделов, которые он постоянно мониторит на предмет появления новых постов. 
Изначально этот список пуст, пополняется он как раз благодаря этой команде. Ссылка, указанная после знака "|" будет добавлена
в список разделов, поэтому перед выполнением команды нужно убедиться, что вы записали правильную ссылку, и что ссылка указывает 
именно на раздел Joyreactor'а. В ином случае бот уведомит вас об ошибке.
2) del_tag|"ссылка" - работает с всё тем же списком, но вместо добавления удаляет ссылку из списка разделов на отслеживание.
Правила всё те же - нужно убедится, что ссылка после знака "|" указана верно. Если такой нет в списке, бот уведомит об этом.
3) /start_checking - Так как изначально список разделов для отслеживания пуст - то и мониторить нечего. В связи с этим
проверки изначально не ведутся, а запуск проверок выделен в отдельную функцию. После заполнения списка разделов на 
отслеживание, нужно будет прописать функцию "/start_checking", и тогда бот начнёт мониторить выбранные разделы.
4) /stop_checking - Данная функция останавливает цикл проверок разделов из списка. Функционально в ней нет необходимости - бот 
будет успешно работать и без неё, всеми остальными функциями можно пользоваться и пока работает цикл проверок - это ничего не сломает
в работе бота, однако логически предусмотреть эту функцию было бы верно, ведь функция запуска предусмотрена.
