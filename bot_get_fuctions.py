from bot_const import *
import gspread as gs
import pandas as pd
from datetime import datetime, timedelta

gc = gs.service_account(filename="my-new-project-393911-88235ab22957.json")
sh = gc.open_by_url(students_link)
ws = sh.worksheet("Регистрация")
df = pd.DataFrame(ws.get_all_records())
sh_2 = gc.open_by_url(orgs_link)
ws_2 = sh_2.worksheet("Лист1")


def get_student_info(mes):
    fi = mes.split()
    new_df = df.loc[
        ((df['Фамилия'] == fi[0]) & (df['Имя'] == fi[1])), ["Комната", "Номер телефона (в формате +71234567890)",
                                                            "Ссылка на страницу VK (Например, vk.com/tag)",
                                                            "Ссылка на Telegtam (Например, t.me/tag)"]]
    room = new_df.iloc[0]["Комната"]
    new_df_2 = df.loc[
        ((df['Комната'] == room) & (df['Имя'] != fi[1])), ["Фамилия", "Имя"]]
    tel_number = new_df.iloc[0]["Номер телефона (в формате +71234567890)"]
    vk_link = new_df.iloc[0]["Ссылка на страницу VK (Например, vk.com/tag)"]
    tg_link = new_df.iloc[0]["Ссылка на Telegtam (Например, t.me/tag)"]
    surnames = new_df_2['Фамилия'].tolist()
    names = new_df_2['Имя'].tolist()
    neighbours = ""
    if len(surnames) == 0:
        neighbours = "Живет один"
    else:
        for i in range(len(surnames)):
            neighbours += surnames[i] + " " + names[i] + "\n"
    result = "Номер комнаты: " + str(room) + "\n" + "Номер телефона: " + str(
        tel_number) + "\n" + "Ссылка на VK: " + vk_link + "\n" + "Ссылка на TG: " + tg_link + "\n" + "Соседи: " + "\n" + neighbours
    return result


def check_if_in(mes):
    fi = mes.split()
    try:
        new_df = df.loc[
            ((df['Фамилия'] == fi[0]) & (df['Имя'] == fi[1]))]
        flag = new_df.empty
    except IndexError:
        flag = True
    return flag


def check_if_in_org(mes):
    values_list = ws_2.col_values(1)
    if mes in values_list:
        flag = True
    else:
        flag = False
    return flag


def check_if_in_tags(mes):
    values_list = ws_2.col_values(3)
    if mes in values_list:
        flag = True
    else:
        flag = False
    return flag


def get_org_schedule(mes):
    date = datetime.now()
    res = ""
    if date < date_start:
        res = "Посвят еще не начался, гетинг реди!"
    elif date > date_end:
        res = "Посвят закончился, чилл!"
    else:
        fam = ws_2.col_values(1)
        ind = fam.index(mes) + 1  # получаем индекс строки с подходящей фамилией
        times_list = get_times_list()
        places = ws_2.row_values(ind)
        time_now = datetime.now().time()
        flag = False
        t = 0
        while (flag is False) & (t < len(times_list)):
            now = datetime.strptime(times_list[t], '%H:%M').time()
            next_time = datetime.strptime(times_list[t + 1], '%H:%M').time()
            if (time_now >= now) & (time_now <= next_time):
                flag = True
            else:
                t += 1
        if date.date() == date_start.date():
            for i in range(9 + t):
                places.pop(0)
            for i in range(t):
                times_list.pop(0)
        if date.date() == date_end.date():
            for i in range(42 + t):
                places.pop(0)
            for i in range(42 + t):
                times_list.pop(0)
        res += "Сейчас на точке: " + places[0] + "\n" + "Дальнейшее расписание:\n"
        for i in range(len(places) - 1):
            res += times_list[i + 1] + ": " + places[i + 1] + "\n"
    return res


def get_times_list():
    times_list = []
    date = datetime.now()
    if date.date() == date_end.date():
        for k in range(33):
            val = ws_2.cell(2, 43 + k).value
            times_list.append(val)
    if date.date() == date_start.date():
        times_list = ws_2.row_values(2)  # список времени
        for i in range(9):
            times_list.pop(0)
    return times_list


def get_times_list_for_now():
    date = datetime.now()
    time_list = []
    if date.date() == date_start.date():
        for k in range(33):
            val = ws_2.cell(2, 10 + k).value
            time_list.append(val)
    if date.date() == date_end.date():
        for k in range(33):
            val = ws_2.cell(2, 43 + k).value
            time_list.append(val)
    return time_list


def get_my_schedule(mes):
    date = datetime.now()
    res = ""
    if date < date_start:
        res = "Посвят еще не начался, гетинг реди!"
    elif date > date_end:
        res = "Посвят закончился, чилл!"
    else:
        username = "@" + mes
        fam = ws_2.col_values(3)
        ind = fam.index(username) + 1  # получаем индекс строки с подходящей фамилией
        times_list = get_times_list()
        places = ws_2.row_values(ind)
        time_now = datetime.now().time()
        flag = False
        t = 0
        while (flag is False) & (t < len(times_list)):
            now = datetime.strptime(times_list[t], '%H:%M').time()
            next_time = datetime.strptime(times_list[t + 1], '%H:%M').time()
            if (time_now >= now) & (time_now <= next_time):
                flag = True
            else:
                t += 1
        if date.date() == date_start.date():
            for i in range(9 + t):
                places.pop(0)
            for i in range(t):
                times_list.pop(0)
        if date.date() == date_end.date():
            for i in range(42 + t):
                places.pop(0)
            for i in range(42 + t):
                times_list.pop(0)
        res += "Дальнейшее расписание:" + "\n"
        for i in range(len(places) - 1):
            res += times_list[i + 1] + ": " + places[i + 1] + "\n"
    return res


def get_my_schedule_now(mes):
    res = ""
    date = datetime.now()
    if date < date_start:
        res = "Посвят еще не начался, гетинг реди!"
    elif date > date_end:
        res = "Посвят закончился, чилл!"
    else:
        username = "@" + mes
        fam = ws_2.col_values(3)
        ind = fam.index(username) + 1  # получаем индекс строки с подходящей фамилией
        places = ws_2.row_values(ind)
        time_list = get_times_list_for_now()
        time_now = date.time()
        flag = False
        t = 0
        while (flag is False) & (t < len(time_list)-1):
            now = datetime.strptime(time_list[t], '%H:%M').time()
            next_time = datetime.strptime(time_list[t + 1], '%H:%M').time()
            if (time_now >= now) & (time_now <= next_time):
                flag = True
            else:
                t += 1
        if date.date() == date_start.date():
            res += "Моя точка на данный момент: " + places[9+t]
        if date.date() == date_end.date():
            res += "Моя точка на данный момент: " + places[42+t]
    return res