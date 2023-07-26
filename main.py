from bot_const import *
from bot_db import add_user, delete_user, check_if_user
import sqlite3
import gspread as gs
import pandas as pd
from datetime import datetime, timedelta

gc = gs.service_account(filename="my-new-project-393911-88235ab22957.json")
sh = gc.open_by_url(students_link)
ws = sh.worksheet("Регистрация")
df = pd.DataFrame(ws.get_all_records())
sh_2 = gc.open_by_url(orgs_link)
ws_2 = sh_2.worksheet("Лист1")


# df_2 = pd.DataFrame(ws_2.get_all_values)


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
    res = ""
    fam = ws_2.col_values(1)
    times = ws_2.row_values(2)  # список времени
    for i in range(9):
        times.pop(0)
    ind = fam.index(mes) + 1  # получаем индекс строки с подходящей фамилией
    time_now = datetime.now().strftime("%H:%M")  # текущее время
    for t in range(len(times)):
        if (time_now >= times[t]) & (time_now <= times[t + 1]):
            k = t
            break
    places = ws_2.row_values(ind)
    for i in range(k):
        times.pop(0)
    for i in range(9 + k):
        places.pop(0)
    res += "Что делает сейчас: " + places[0] + "\n" + "Дальнейшее расписание:" + "\n"
    for i in range(len(places) - 1):
        res += times[i + 1] + ": " + places[i + 1] + "\n"
    return res


def get_my_schedule(mes):
    username = "@" + mes
    flag = check_if_in_tags(username)
    if flag is False:
        res = "Вас нет в нашем списке!"
    else:
        res = ""
        fam = ws_2.col_values(3)
        times = ws_2.row_values(2)  # список времени
        for i in range(9):
            times.pop(0)
        ind = fam.index(username) + 1  # получаем индекс строки с подходящей фамилией
        time_now = datetime.now().strftime("%H:%M")  # текущее время
        for t in range(len(times)):
            if (time_now >= times[t]) & (time_now <= times[t + 1]):
                k = t
                break
        places = ws_2.row_values(ind)
        for i in range(k):
            times.pop(0)
        for i in range(9 + k):
            places.pop(0)
        res += "Что делаю сейчас: " + places[0] + "\n" + "Дальнейшее расписание:" + "\n"
        for i in range(len(places) - 1):
            res += times[i + 1] + ": " + places[i + 1] + "\n"
    return res

