import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from utils import validate_birth_date, save_report_to_file, save_report_to_mp3
from analysis import (
    load_and_clean_orders,
    add_calculated_columns,
    analyze_data,
    extra_math_calculations,
    generate_report
)


selected_file = None


def create_app():
    root = tk.Tk()
    root.title("Анализ заказов интернет-магазина")
    root.geometry("1100x780")
    root.minsize(980, 700)
    root.configure(bg="#f4f6f8")

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Title.TLabel",
        font=("Segoe UI", 20, "bold"),
        foreground="#1f2937",
        background="#f4f6f8"
    )

    style.configure(
        "Header.TLabel",
        font=("Segoe UI", 11, "bold"),
        foreground="#111827",
        background="white"
    )

    style.configure(
        "Custom.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=10
    )

    style.configure(
        "Custom.TEntry",
        padding=6
    )

    main_frame = tk.Frame(root, bg="#f4f6f8")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ttk.Label(
        main_frame,
        text="Приложение для анализа заказов интернет-магазина",
        style="Title.TLabel"
    )
    title_label.pack(anchor="w", pady=(0, 10))

    subtitle = tk.Label(
        main_frame,
        text="Дата рождения, очистка CSV, аналитика, статистика, отчёт и озвучивание",
        font=("Segoe UI", 10),
        bg="#f4f6f8",
        fg="#6b7280"
    )
    subtitle.pack(anchor="w", pady=(0, 18))

    top_card = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
    top_card.pack(fill="x", pady=(0, 15))
    top_card.columnconfigure(1, weight=1)

    ttk.Label(
        top_card,
        text="Дата рождения (YYYY-MM-DD):",
        style="Header.TLabel"
    ).grid(row=0, column=0, padx=15, pady=(15, 8), sticky="w")

    birth_entry = ttk.Entry(
        top_card,
        width=25,
        font=("Segoe UI", 11),
        style="Custom.TEntry"
    )
    birth_entry.grid(row=0, column=1, padx=15, pady=(15, 8), sticky="w")

    ttk.Label(
        top_card,
        text="Файл заказов:",
        style="Header.TLabel"
    ).grid(row=1, column=0, padx=15, pady=8, sticky="w")

    file_label = tk.Label(
        top_card,
        text="Файл не выбран",
        font=("Segoe UI", 10),
        bg="white",
        fg="#6b7280",
        anchor="w"
    )
    file_label.grid(row=1, column=1, padx=15, pady=8, sticky="we")

    stats_frame = tk.Frame(main_frame, bg="#f4f6f8")
    stats_frame.pack(fill="x", pady=(0, 15))

    def create_stat_card(parent, title, value_var_text):
        card = tk.Frame(parent, bg="white", bd=1, relief="solid", width=200, height=90)
        card.pack_propagate(False)

        title_label = tk.Label(
            card,
            text=title,
            font=("Segoe UI", 10),
            bg="white",
            fg="#6b7280"
        )
        title_label.pack(anchor="w", padx=12, pady=(12, 4))

        value_label = tk.Label(
            card,
            text=value_var_text,
            font=("Segoe UI", 15, "bold"),
            bg="white",
            fg="#111827"
        )
        value_label.pack(anchor="w", padx=12)

        return card, value_label

    card1, income_value = create_stat_card(stats_frame, "Общий доход", "—")
    card2, returns_value = create_stat_card(stats_frame, "Возвраты", "—")
    card3, avg_check_value = create_stat_card(stats_frame, "Средний чек", "—")
    card4, top_product_value = create_stat_card(stats_frame, "Топ товар", "—")

    card1.pack(side="left", fill="x", expand=True, padx=(0, 10))
    card2.pack(side="left", fill="x", expand=True, padx=(0, 10))
    card3.pack(side="left", fill="x", expand=True, padx=(0, 10))
    card4.pack(side="left", fill="x", expand=True)

    result_card = tk.Frame(main_frame, bg="white", bd=1, relief="solid")
    result_card.pack(fill="both", expand=True)

    result_header = tk.Frame(result_card, bg="white")
    result_header.pack(fill="x", padx=15, pady=(15, 10))

    tk.Label(
        result_header,
        text="Результат анализа",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="#111827"
    ).pack(anchor="w")

    tk.Label(
        result_header,
        text="Ниже отображается итоговый текстовый отчёт",
        font=("Segoe UI", 9),
        bg="white",
        fg="#6b7280"
    ).pack(anchor="w", pady=(2, 0))

    result_text = ScrolledText(
        result_card,
        wrap="word",
        font=("Consolas", 11),
        bg="#fbfbfb",
        fg="#111827",
        insertbackground="black",
        relief="flat",
        bd=0
    )
    result_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    status_var = tk.StringVar()
    status_var.set("Готово к работе")

    def choose_file():
        global selected_file

        file_path = filedialog.askopenfilename(
            title="Выберите файл orders.csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if file_path:
            selected_file = file_path
            file_label.config(text=f"Файл: {file_path}")
            status_var.set("CSV файл успешно выбран")

    def clear_fields():
        global selected_file
        birth_entry.delete(0, tk.END)
        result_text.delete("1.0", tk.END)
        file_label.config(text="Файл не выбран")
        status_var.set("Поля очищены")
        selected_file = None

        income_value.config(text="—")
        returns_value.config(text="—")
        avg_check_value.config(text="—")
        top_product_value.config(text="—")

    def run_analysis():
        global selected_file

        try:
            user_date = birth_entry.get().strip()

            if not user_date:
                raise ValueError("Введите дату рождения")

            if not selected_file:
                raise ValueError("Сначала выберите файл orders.csv")

            _, birth_week_day, age_in_days = validate_birth_date(user_date)

            df = load_and_clean_orders(selected_file)
            df = add_calculated_columns(df)

            analysis = analyze_data(df)
            extra_results = extra_math_calculations(df)

            report_text = generate_report(
                user_date,
                birth_week_day,
                age_in_days,
                analysis,
                extra_results
            )

            df.to_csv("clean_orders.csv", index=False, encoding="utf-8-sig")
            save_report_to_file(report_text)
            save_report_to_mp3(report_text, lang="ru")

            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, report_text)

            income_value.config(text=f'{analysis["total_income"]:.2f}')
            returns_value.config(text=f'{analysis["return_rate"]:.2f}%')
            avg_check_value.config(text=f'{extra_results["avg_order"]:.2f}')

            if len(analysis["top_products"]) > 0:
                first_product = analysis["top_products"].index[0]
                top_product_value.config(text=str(first_product))
            else:
                top_product_value.config(text="Нет данных")

            status_var.set("Анализ завершён успешно")

            messagebox.showinfo(
                "Готово",
                "Анализ завершён успешно.\n\n"
                "Сохранены файлы:\n"
                "• clean_orders.csv\n"
                "• report.txt\n"
                "• report.mp3"
            )

        except Exception as e:
            status_var.set("Ошибка при выполнении анализа")
            messagebox.showerror("Ошибка", str(e))

    button_frame = tk.Frame(top_card, bg="white")
    button_frame.grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 15), sticky="w")

    choose_btn = ttk.Button(
        button_frame,
        text="Выбрать CSV",
        command=choose_file,
        style="Custom.TButton"
    )
    choose_btn.pack(side="left", padx=(0, 10))

    run_btn = ttk.Button(
        button_frame,
        text="Запустить анализ",
        command=run_analysis,
        style="Custom.TButton"
    )
    run_btn.pack(side="left", padx=(0, 10))

    clear_btn = ttk.Button(
        button_frame,
        text="Очистить",
        command=clear_fields,
        style="Custom.TButton"
    )
    clear_btn.pack(side="left")

    status_bar = tk.Label(
        root,
        textvariable=status_var,
        bd=1,
        relief="sunken",
        anchor="w",
        font=("Segoe UI", 9),
        bg="#e5e7eb",
        fg="#111827",
        padx=10
    )
    status_bar.pack(side="bottom", fill="x")

    return root