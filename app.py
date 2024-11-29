import requests
import re
import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

def getTeacherList(url):
    data = {
        'status': True,
        'message': "",
        'data': ''
    }

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as err:
        data['status'] = False
        data['message'] = f"無法連接網站：{err}" 
    if data['status'] == True:
        if response.status_code == 200:
            teacherList = re.findall(r'<div\sclass="member">(.*?)<div\sclass="teacher-list"', response.text, re.DOTALL)
            teachers = []
            for teacher in teacherList:
                teacher_name = re.findall(r'teacher_rkey.*?>(.*?)<\/a><s', teacher, re.DOTALL)
                teacher_email = re.findall(r'mailto:\/\/(.*?)"', teacher, re.DOTALL)
                teacher_title = re.findall(r'職稱.*?member_info_content">(.*?)<', teacher, re.DOTALL)
                teachers.append({
                    'name': teacher_name[0].strip(),
                    'title': teacher_title[0].strip(),
                    'email': teacher_email[0].strip()
                })
            data['data'] = teachers
        elif response.status_code == 404:
            data['status'] = False
            data['message'] = "無法取得網頁：404"
    
    return data

def initDatabase(teacherList):
    connection = sqlite3.connect(os.getcwd() + "\\contacts.db")
    connection.row_factory = sqlite3.Row
    database = connection.cursor()

    try:
        database.execute('''
            CREATE TABLE IF NOT EXISTS "contacts" (
                "id"	INTEGER,
                "name"	TEXT NOT NULL,
                "title"	TEXT NOT NULL,
                "email"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
        ''')
    except sqlite3.OperationalError:  # 捕捉不合法的數值輸入
        print("資料表movies新增失敗")

    for teacher in teacherList:
        select_sql = "SELECT * FROM contacts Where `name` = ?;"
        database.execute(select_sql, [teacher['name']])
        result = database.fetchall()
        if(not result):
            insert_sql = "INSERT INTO contacts (`name`, `title`, `email`) VALUES (?, ?, ?);"
            database.execute(insert_sql, [teacher['name'], teacher['title'], teacher['email']])
            connection.commit()

def start():
    tableFields = {
        "name":"姓名",
        "title":"職稱",
        "email":"Email",
    }
    url = defaultUrl.get()
    result = getTeacherList(url)
    if(result['status']):
        initDatabase(result['data'])
        text_area.insert(tk.END, f"{tableFields['name']:{chr(12288)}<5} {tableFields['title']:{chr(12288)}<15} {tableFields['email']:{chr(12288)}<15}\n")
        text_area.insert(tk.END, "-------------------------------------------------------------\n")
        for teacher in result['data']:
            text_area.insert(tk.END, f"{teacher['name']:{chr(12288)}<5} {teacher['title']:{chr(12288)}<15} {teacher['email']:{chr(12288)}<15}\n")
    else:
        messagebox.showerror("網路錯誤", result['message'])

url="https://csie.ncut.edu.tw/content.php?key=86OP82WJQO"

window = tk.Tk()
window.title('聯絡資訊爬蟲')
window.geometry('640x480')
window.grid_columnconfigure(0, weight=1, uniform="equal")  # 左邊 Label
window.grid_columnconfigure(1, weight=2, uniform="equal")  # 中間 Entry
window.grid_columnconfigure(2, weight=1, uniform="equal") 
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(1, weight=1)
window.grid_columnconfigure(1, weight=1)

defaultUrl = tk.StringVar()
defaultUrl.set(url)

label = tk.Label(window, text="URL:").grid(row = 0, column = 0, padx=10, pady=10, sticky="e")

entry = tk.Entry(window, textvariable = defaultUrl).grid(row = 0, column = 1, padx = "5px", sticky="ew")

button = tk.Button(window, text="抓取", command=start).grid(row = 0, column = 2)

text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
text_area.grid(row = 2, column = 0, columnspan = 10, padx="10px", pady="10px", sticky="nsew")

window.mainloop()