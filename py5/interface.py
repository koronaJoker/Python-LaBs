from user_data import *
from report_to_md import make_md_report
from report_to_txt import make_txt_report
from speak import make_voice_report
import os
import tkinter as tk
from tkinter import messagebox


root = tk.Tk()
root.geometry("900x600")
root.title("Создание Отчёта")

data_frame = tk.Frame(root)
data_frame.pack()

report_data = None

user_header = tk.Label(
    data_frame,
    text="Укажите вашу дату рождения:",
    font=("Comic Sans MS", 18, "bold"),
    padx = 30,
    pady=30,
    #anchor="w"
)

user_header.pack(fill="x")


format_frame = tk.Frame(data_frame)
format_frame.pack(anchor="center")

format_label = tk.Label(
    format_frame,
    text="Формат:",
    font=("Comic Sans MS", 10)
)

format_label.pack(side="left")

text_format = tk.Label(
    format_frame,
    text="YYYY-MM-DD",
    font=("Comic Sans MS", 10, "bold")
)

text_format.pack(side="left", padx=(5, 0))

user_entry = tk.Entry(
    data_frame,
    font=("Comic Sans MS", 10),
    width=25
)

user_entry.pack(pady=15)

def handle_data():
    global report_data
    new_data = user_entry.get()
    if (not validate_data(new_data)):
        messagebox.showerror("Упс", "Неверный формат даты! (YYYY-MM-DD)")
    else:
        report_data = get_data(new_data)
        entered_date, date_in_days, day_of_week = report_data
        selected_date_label.config(
            text=f"Дата: {entered_date}\nДень недели: {day_of_week}\nПрошло дней: {date_in_days}"
        )
        data_frame.pack_forget()
        main_frame.pack(fill="both", expand=True)


def check_report_data():
    if report_data is None:
        messagebox.showerror("Упс", "Сначала укажите дату рождения.")
        return False
    return True


def handle_txt_report():
    if not check_report_data():
        return

    make_txt_report(*report_data)
    messagebox.showinfo("Готово", "TXT отчёт создан: report.txt")


def handle_md_report():
    if not check_report_data():
        return

    make_md_report(*report_data)
    messagebox.showinfo("Готово", "MD отчёт создан: report.md")


def handle_voice_report():
    if not check_report_data():
        return

    try:
        text = make_txt_report(*report_data)
        make_voice_report(text)
        messagebox.showinfo("Готово", "Голосовой отчёт создан: report.mp3")
    except Exception as error:
        messagebox.showerror("Упс", f"Не получилось создать голосовой отчёт:\n{error}")


def open_handled_orders():
    file_path = "handled_orders.csv"

    if not os.path.exists(file_path):
        messagebox.showerror("Упс", "Файл handled_orders.csv не найден.")
        return

    try:
        os.startfile(file_path)
    except OSError as error:
        messagebox.showerror("Упс", f"Не получилось открыть таблицу:\n{error}")


def open_report(file_path, report_name):
    if not os.path.exists(file_path):
        messagebox.showerror("Упс", f"Файл {file_path} не найден. Сначала создайте {report_name} отчёт.")
        return

    try:
        os.startfile(file_path)
    except OSError as error:
        messagebox.showerror("Упс", f"Не получилось открыть {report_name} отчёт:\n{error}")


def open_txt_report():
    open_report("report.txt", "TXT")


def open_md_report():
    open_report("report.md", "MD")


btn = tk.Button(data_frame,
                text = "Подтвердить",
                font = ("Comic Sans MS", 12, "bold"),
                width = 25,
                bg = "#4f11c2",
                fg="white",
                activebackground="#320880",
                activeforeground="white",
                cursor="hand2",
                command=handle_data
                )

btn.pack(pady = 20)


img = tk.PhotoImage(file="meme_resized.png")

label = tk.Label(data_frame, image=img)
label.pack()


main_frame = tk.Frame(root)

main_header = tk.Label(
    main_frame,
    text="Генерация отчётов",
    font=("Comic Sans MS", 20, "bold"),
    padx=30,
    pady=30
)
main_header.pack(fill="x")

selected_date_label = tk.Label(
    main_frame,
    text="",
    font=("Comic Sans MS", 12),
    justify="center"
)
selected_date_label.pack(pady=(0, 25))

report_buttons_frame = tk.Frame(main_frame)
report_buttons_frame.pack()

txt_btn = tk.Button(
    report_buttons_frame,
    text="Создать TXT отчёт",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=handle_txt_report
)
txt_btn.pack(pady=8)

md_btn = tk.Button(
    report_buttons_frame,
    text="Создать MD отчёт",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=handle_md_report
)
md_btn.pack(pady=8)

open_txt_btn = tk.Button(
    report_buttons_frame,
    text="Открыть TXT отчёт",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=open_txt_report
)
open_txt_btn.pack(pady=8)

open_md_btn = tk.Button(
    report_buttons_frame,
    text="Открыть MD отчёт",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=open_md_report
)
open_md_btn.pack(pady=8)

voice_btn = tk.Button(
    report_buttons_frame,
    text="Создать голосовой отчёт",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=handle_voice_report
)
voice_btn.pack(pady=8)

excel_btn = tk.Button(
    report_buttons_frame,
    text="Открыть таблицу в Excel",
    font=("Comic Sans MS", 12, "bold"),
    width=25,
    bg="#4f11c2",
    fg="white",
    activebackground="#320880",
    activeforeground="white",
    cursor="hand2",
    command=open_handled_orders
)
excel_btn.pack(pady=8)



root.mainloop()
