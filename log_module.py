def scr_log(s):
    """
    
    """
    with open("Logs\\scr_log.txt", "a") as scr_log:
        scr_log.write(s+"\n")

def msg_log(s):
    """
    
    """
    with open("Logs\\msg_log.txt", "a") as msg_log:
        msg_log.write(s+"\n")


def write_into_scrlog(s):
    """
        Input: строку, которую нужно записать в файл логов.

        Output: ничего.

        Файл для записи в файл с логами программы. Вписывает переданную 
        строку и переносит каретку на следующую строку.
    """
    with open("Logs\\script_logs.txt", "a") as scr_log:
        scr_log.write(s+"\n")

def write_into_msglog(s):
    """
        Input: строку, которую нужно записать в файл логов.

        Output: ничего.

        Файл для записи в файл с логами сообщений. Вписывает переданную 
        строку и переносит каретку на следующую строку.
    """
    with open("Logs\\message_logs.txt", "a") as msg_log:
        msg_log.write(s+"\n")